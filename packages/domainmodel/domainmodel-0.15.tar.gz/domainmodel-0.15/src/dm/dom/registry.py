from dm.dom.classregister import DomainClassRegister
from dm.dom.base import *
from dm.dom.stateful import *
from dm.dom.temporal import TemporalProperty
from dm.dom.temporal import BitemporalProperty
from dm.dom.temporal import BitemporalActual
from dm.dom.temporal import TemporalRevision
from dm.dom.temporal import TemporalAssociateList
from dm.ioc import * 
from dm.exceptions import * 
import inspect
import dm.times
import weakref
import os

class DomainRegistry(AbstractRegister):
    """
    Central register for the domain model classes and top-level model registers.
    """

    def __init__(self):
        super(DomainRegistry, self).__init__()
        self.domainClassRegister = None
        self.backgroundObjectCache = []
        self.path = ModelPath(self)

    def registerDomainClass(self, domainClass):
        """
        Activates given domain class with the domain model.
        """
        self.log.debug("Registering domain class '%s'." % domainClass)
        # Check domain class type.
        if not issubclass(domainClass, DomainObject):
            raise Exception, "Domain class %s is not subclass of DomainObject." % domainClass
        # Check domain class name not already registered.
        classRegister = self.getDomainClassRegister()
        domainClassName = domainClass.__name__
        if domainClassName in classRegister:
            existingClass = classRegister[domainClassName]
            if features.allowReplace:
                return
            msg = "Domain class '%s' is already defined: %s" % (
                domainClassName, existingClass
            )
            raise Exception, msg 

        # Create meta domain object for submitted domain class.
        if not domainClass.__dict__.get('meta', None):
            domainClass.meta = domainClass.metaClass(domainClassName)
        if not domainClass.meta.dbName:
            if domainClass.dbName:
                domainClass.meta.dbName = domainClass.dbName

        # For temporal objects, infer temporal history attribute.
        if domainClass.isTemporal:
            temporalClassName = self.makeTemporalRevisionClassName(domainClass.meta)
            domainClass.temporalHistory = HasMany(temporalClassName, 'id', 'parent', isHidden=True)

        # Set model attributes of domain class on meta domain object.
        # Implements 'Concrete Table Inheritance' (Martin Fowler).
        # http://martinfowler.com/eaaCatalog/concreteTableInheritance.html
        self.setModelAttributesFromClass(domainClass, domainClass.meta)
       
        # Set meta model attributes of domain class on meta domain object.
        domainClass.meta.isUnique = domainClass.isUnique
        isCached = False
        if domainClass.isConstant == True:
            isCached = True
        elif bool(self.dictionary[MODEL_CACHE_IS_ENABLED]):
            cachedClasses = self.dictionary[MODEL_CACHE_CLASSES]
            cachedClasses = cachedClasses.split(',')
            cachedClasses = [i.strip() for i in cachedClasses if i.strip()]
            if not cachedClasses:
                isCached = True
            elif domainClassName in cachedClasses:
                isCached = True
        self.log.debug("Domain class '%s' is %s in model in pid %s." % (domainClassName, isCached and 'cached' or 'NOT cached', os.getpid()))

        domainClass.meta.isCached = isCached
        domainClass.meta.isTemporal = domainClass.isTemporal
        domainClass.meta.setSortOnAttr(domainClass.sortOnName)
        domainClass.meta.sortCaseInsensitive = domainClass.sortCaseInsensitive
        domainClass.meta.sortAscending = domainClass.sortAscending

        # Add domain class to register.
        classRegister[domainClassName] = domainClass
        domainClass.isRegistered = True

        # Initialise reflection into the persistence layer.
        self.createPersistenceClass(domainClass.meta)

        # Go ahead with any attributes that depend on the submitted class.
        self.setDeferredAttributesOnRegisteredClasses(domainClass)
        for name in classRegister:
            self.checkHasAsForHasManys(classRegister[name])

        # For temporal objects, create temporal history domain class.
        if domainClass.isTemporal:
            # Group temporal propertes on revision object.
            metaAttrs = []
            for attrMeta in domainClass.meta.attributes:
                if attrMeta.isTemporal:
                    metaAttrs.append(attrMeta)
            parentMeta = domainClass.meta
            self.generateTemporalRevisionClass(parentMeta, metaAttrs)
        else:
            # Look for independently temporal properties.
            for attrMeta in domainClass.meta.attributes:
                if attrMeta.isTemporal:
                    if attrMeta.isAssociateList:
                        raise Exception, "No support for independently temporal associate lists at this time. Try setting the class isTemporal to true? %s on %s" % (attrMeta, domainClass.meta)
                    else:
                        parentMeta = domainClass.meta
                        self.generateTemporalPropertyClass(parentMeta, attrMeta)

        # Set domain class properties from meta attributes.
        if not domainClass.meta.isCached:
            self.setDomainClassProperties(domainClass)

    def setDomainClassProperties(self, domainClass):
        for attrMeta in domainClass.meta.attributes:
            if attrMeta.isAssociateList:
                self.setDomainClassProperty(domainClass, attrMeta)

    def setDomainClassProperty(self, domainClass, attrMeta):
        classProperty = property(attrMeta.createRegister)
        setattr(domainClass, attrMeta.name, classProperty)

    def makeTemporalRevisionClassName(self, classMeta):
        return TemporalRevision.makeTemporalName(classMeta.name)

    def generateTemporalRevisionClass(self, parentMeta, metaAttrs):
        # No support for bitemporal object revisions yet!
        temporalBase = TemporalRevision
        temporalClassName = self.makeTemporalRevisionClassName(parentMeta)
        temporalMeta = temporalBase.metaClass(temporalClassName)
        deferredParams = []
        for metaAttr in metaAttrs:
            if metaAttr.isAssociateList:
                if not metaAttr.getDomainRegister().isStateful:
                    msg = "Associated class '%s' must be stateful for " % (
                        metaAttr.typeName,
                    )
                    msg += "attribute '%s' on class '%s'." % (
                        metaAttr.name, parentMeta.name
                    )
                    # Todo: Figure if this can be avoided. Problem is that
                    # deleting the simple associated object leaves the list
                    # history in a mess. Could fix by deleting the history?
                    raise Exception, msg
                temporalListClassName = temporalBase.makeTemporalName(
                    parentMeta.name, metaAttr.name
                )
                deferredParams.append({
                    'temporalMeta': temporalMeta,
                    'metaAttr': metaAttr,
                    'temporalListClassName': temporalListClassName,
                })
                #self.generateTemporalAssociateListClass(
                #    temporalMeta, metaAttr, temporalListClassName
                #)
                newAttr = AggregatesMany(temporalListClassName,'id','parent')
            else:
                newAttr = metaAttr.duplicateTemporal()
            setattr(temporalMeta, metaAttr.name, newAttr)
        temporalClass = self.createDomainClass(temporalMeta, temporalBase)
        temporalClass.parent = HasA(parentMeta.name, isRequired=True)
        self.registerDomainClass(temporalClass)
        parentMeta.setTemporalDomainClass(temporalClass)
        for params in deferredParams:
            self.generateTemporalAssociateListClass(
                params['temporalMeta'],
                params['metaAttr'],
                params['temporalListClassName']
            )

    def generateTemporalAssociateListClass(self, parentMeta, attrMeta, temporalClassName):
        # No support for bitemporal associate lists yet!
        temporalBase = TemporalAssociateList
        temporalMeta = temporalBase.metaClass(temporalClassName)
        temporalClass = self.createDomainClass(temporalMeta, temporalBase)
        keyMeta = attrMeta.getKeyMetaAttribute()
        # N.B. Key meta for key name 'id' == None.
        if keyMeta:
            temporalClass.recordedKey = keyMeta.duplicateTemporal()
        else:
            temporalClass.recordedKey = Integer(isRequired=True)
        temporalClass.recordedValue = HasA(attrMeta.typeName, isRequired=True)
        temporalClass.parent = HasA(parentMeta.name, isRequired=True)
        self.registerDomainClass(temporalClass)
        attrMeta.setTemporalDomainClass(temporalClass)

    def generateTemporalPropertyClass(self, parentMeta, attrMeta):
        if attrMeta.isBitemporalActual:
            temporalBase = BitemporalActual
        elif attrMeta.isBitemporal:
            temporalBase = BitemporalProperty
        else:
            temporalBase = TemporalProperty
        temporalClassName = temporalBase.makeTemporalName(
            parentMeta.name, attrMeta.name
        )
        temporalMeta = temporalBase.metaClass(temporalClassName)
        temporalClass = self.createDomainClass(temporalMeta, temporalBase)
        temporalClass.recordedValue = attrMeta.duplicateTemporal()
        temporalClass.parent = HasA(parentMeta.name, isRequired=True)
        self.registerDomainClass(temporalClass)
        attrMeta.setTemporalDomainClass(temporalClass)

    def getDomainClassRegister(self):
        if not self.domainClassRegister:
            self.domainClassRegister = DomainClassRegister()
        return self.domainClassRegister

    def registerCoreDomainClasses(self):
        pass
         
    def loadBackgroundObjects(self):
        "Creates and caches refs to all background domain objects."
        pass
        
    def createDomainClass(self, metaDomainObject, baseClass=DomainObject):
        return metaDomainObject.createDomainClass(baseClass)

    def isDomainClassRegistered(self, className):
        if className.__class__.__name__ != 'str':
            message = 'className is not a str: %s' % str(className)
            raise Exception, message
        classRegister = self.getDomainClassRegister()
        if className in classRegister:
            return classRegister[className].isRegistered
        else:
            return False
    
    def getDomainClass(self, className):
        classRegister = self.getDomainClassRegister()
        if not className in classRegister:
            # Todo: Use a specific error type here, so excepts can be selective.
            raise Exception, "Domain class '%s' is not defined." % className
        return classRegister[className]

    def setModelAttributesFromClass(self, domainClass, domainClassMeta):
        className = domainClass.__name__
        classAttrs = inspect.getmembers(domainClass)
        for (attrName, classAttr) in classAttrs:
            if issubclass(classAttr.__class__, MetaDomainAttr):
                defaultInstanceName = className[0].lower() + className[1:]
                if classAttr.typeName == className:
                    if attrName == defaultInstanceName:
                        raise Exception, "Usage of name '%s' for attribute HasA('%s') on '%s' class is not supported (the generated SQL confuses the database at the moment). Please use an attribute name that is case-insensitively distinct from the attribute's class name." % (attrName, className, className)
                # fix up 'owner' for lists of associates
                if issubclass(classAttr.__class__, AssociateList):
                    if classAttr.owner == '':
                        classAttr.owner = defaultInstanceName
                if issubclass(classAttr.__class__, HasA):
                    if self.isDomainClassRegistered(classAttr.typeName):
                        domainClassMeta.__setattr__(attrName, classAttr)
                    else:
                        domainClassMeta.attributesDeferred[attrName] = classAttr
                elif issubclass(classAttr.__class__, HasMany):
                    if self.isDomainClassRegistered(classAttr.typeName):
                        domainClassMeta.__setattr__(attrName, classAttr)
                    else:
                        domainClassMeta.attributesDeferred[attrName] = classAttr
                else:
                    domainClassMeta.__setattr__(attrName, classAttr)

    def createPersistenceClass(self, metaDomainObject):
        self.database.createPersistenceClass(metaDomainObject)

    def setDeferredAttributesOnRegisteredClasses(self, domainClass):
        """
        Sets attributes that were deferred because the given domainClass was
        not registered at the time the attribute's class was registered.
        """
        classRegister = self.getDomainClassRegister()
        for className in classRegister:
            registeredClass = classRegister[className]
            deferredAttrs = registeredClass.meta.attributesDeferred
            newAttributes = {}
            for attrName in deferredAttrs:
                    deferredAttr = deferredAttrs[attrName]
                    if issubclass(deferredAttr.__class__, MetaDomainAttr):
                        if ((deferredAttr.typeName == domainClass.__name__) or (deferredAttr.typeName == className)):
                            if issubclass(deferredAttr.__class__, HasA):
                                registeredClass.meta.__setattr__(attrName, deferredAttr)
                                self.addPersistenceAttribute(className, deferredAttr)
                                newAttributes[attrName] = deferredAttr
                            elif issubclass(deferredAttr.__class__, HasMany):
                                registeredClass.meta.__setattr__(attrName, deferredAttr)
                                if not registeredClass.meta.isCached:
                                    self.setDomainClassProperty(registeredClass, deferredAttr)
                                newAttributes[attrName] = deferredAttr
            for attrName in newAttributes:
                del(deferredAttrs[attrName])

# todo: if domainClass has a HasMany.name == classAttr.owner, then:
#  - create and register a attribute-free join class, 
#  - fixup both HasMany typeNames, 
#  - add HasA attributes to join class for both HasMany attributes. :-)
        
    def checkHasAsForHasManys(self, domainClass):
        for attrName in domainClass.meta.attributeNames:
            domainClassAttr = domainClass.meta.attributeNames[attrName]
            if issubclass(domainClassAttr.__class__, HasMany):
                classRegister = self.getDomainClassRegister()
                if domainClassAttr.typeName in classRegister:
                    registeredClass = classRegister[domainClassAttr.typeName]
                    if not domainClassAttr.owner:
                        continue
                    expectedClass = domainClass
                    if domainClassAttr.ownerAsOwnerAttr: # Rename and comment.
                        ownerAttr = domainClass.meta.attributeNames[domainClassAttr.ownerAsOwnerAttr]
                        expectedClass = classRegister[ownerAttr.typeName]
                    if domainClassAttr.owner in registeredClass.meta.attributeNames:
                        hasA = registeredClass.meta.attributeNames[domainClassAttr.owner]
                        if not issubclass(hasA.__class__, HasA):
                            raise Exception, "Mismatched domain object attribute definitions: HasMany('%s') on class '%s' expected a HasA('%s') called '%s', not '%s'." % (domainClassAttr.typeName, domainClass.__name__, expectedClass.__name__, domainClassAttr.owner, hasA.__class__.__name__)
                        if hasA.typeName != expectedClass.__name__:
                            raise Exception, "Mismatched domain object attribute definitions: HasMany('%s') on class '%s' expected a HasA('%s') called '%s', not HasA('%s')." % (domainClassAttr.typeName, domainClass.__name__, expectedClass.__name__, domainClassAttr.owner, hasA.typeName)
                    else:
                        raise Exception, "Missing domain object attribute definition: HasMany('%s') on class '%s' expected a HasA('%s') called '%s' on class '%s'. Attribute names are: %s" % (domainClassAttr.typeName, domainClass.__name__, expectedClass.__name__, domainClassAttr.owner, domainClassAttr.typeName, registeredClass.meta.attributeNames.keys() )
        
    def addPersistenceAttribute(self, className, attribute):
        self.database.addPersistenceAttribute(className, attribute)

    def loadBackgroundRegister(self, register):
        "Creates and caches refs to given register."
        for key in register.keys():
            object = register[key]
            self.backgroundObjectCache.append(object)

    def dereference(self, path, **kwds):
        """
        Creates and returns a 'Dereference' instance for given path with 'target' and 'context' attributes.
        """
        return Dereference(self.registry, path, **kwds)

    def retrieveItem(self, key):
        return getattr(self, key)


class RegistryPathGetter(object):

    registry = RequiredFeature('DomainRegistry')

    def __init__(self, registryPath):
        self.registryPathNames = None
        self.registryPath = registryPath

    def getDomainObject(self):
        objectRegister = self.getRegister()
        optionsRegister = objectRegister.getOptionsRegister()
        optionKey = self.getRegistryPathNames()[-1]
        selectedOption = optionsRegister[optionKey]
        return objectRegister[selectedOption]

    def getRegister(self):
        if self.isRegistryPathToRegister():
            registerPathNames = self.getRegistryPathNames()[:]
        else:
            registerPathNames = self.getRegistryPathNames()[:-1]
        owner = self.registry
        register = self.registry
        for name in registerPathNames:
            if owner:
                if not name:
                    msg = "Path names error: %s" % str(registerPathNames)
                    raise Exception, msg
                register = getattr(owner, name)
                owner = None
            else:
                owner = register[name]
        return register

    def isRegistryPathToRegister(self):
        return self.countRegistryPathNames() % 2

    def countRegistryPathNames(self):
        return len(self.getRegistryPathNames())

    def getRegistryPathNames(self):
        if self.registryPathNames == None:
            if self.registryPath:
                self.registryPathNames = self.registryPath.split('/')
            else:
                self.registryPathNames = []
        return self.registryPathNames


class ModelPath(object):

    def __init__(self, modelRegistry):
        self.registry = weakref.ref(modelRegistry)

    def open(self, registryPath):
        """
        Return model object for model path.
        """
        modelObj = self.registry()
        for pathPart in registryPath.split('/'):
            if pathPart == '':
                continue
            modelObj = modelObj.resolvePathPart(pathPart)
        return modelObj


class Dereference(object):

    def __init__(self, registry, path, **kwds):
        self.target = registry
        self.path = path
        self.context = None
        for name in self.path.split('/'):
            if name == '':
                continue
            else:
                self.context = self.target
                self.target = self.target.resolvePathPart(name, **kwds)

