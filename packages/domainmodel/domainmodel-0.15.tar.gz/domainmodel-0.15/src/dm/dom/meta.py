"""
Meta classes describe the DomainObject classes.
"""

# Todo: Rename convertor to converter (spelling).

from dm.ioc import *
from dm.messagedigest import hmac
from dm.messagedigest import sha256
from dm.messagedigest import md5
from dm.datetimeconvertor import DateTimeConvertor
from dm.datetimeconvertor import RDateTimeConvertor
from dm.datetimeconvertor import RNSDateTimeConvertor
from dm.datetimeconvertor import DateConvertor
from dm.datetimeconvertor import RDateConvertor
from dm.datetimeconvertor import DateOfBirthConvertor
from dm.dictionarywords import IMAGES_DIR_PATH
from dm.dictionarywords import DB_MIGRATION_IN_PROGRESS
from dm.dictionarywords import PASSWORD_DIGEST_SECRET
import os
import inspect
from dm.exceptions import *
moddebug = False
import traceback
import weakref

# todo: Add Email attribute meta class.

class AttributeValidator(object):

    def __init__(self, metaAttr, objectData, domainObject, objectRegister):
        self.metaAttr = metaAttr
        self.objectData = objectData
        self.domainObject = domainObject
        self.objectRegister = objectRegister
        self.validate()

    def validate(self):
        raise Exception, "Method not implemented on %s" % self.__class__


class NotDefined(object):
    "Internal 'null' value."
    pass


class BaseDomainMeta(object):
    "Domain model meta supertype."

    registry = RequiredFeature('DomainRegistry')
    dictionary = RequiredFeature('SystemDictionary')
    logger = RequiredFeature('Logger')
    debug = RequiredFeature('Debug')

    def resolvePathPart(self, pathPart, **kwds):
        return pathPart

    def calcTitle(self):
        if self.title:
            return self.title
        else:
            return self.spaceFromCamel(self.name)

    def spaceFromCamel(self, camel):
        AtoZ = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        spaceSep = ''
        lastChar = ''
        for char in camel:
            if lastChar and (char in AtoZ) and not (lastChar in AtoZ):
            #if lastChar and (char in AtoZ):
                spaceSep += ' ' + char.lower()
            else:
                spaceSep += char
            lastChar = char
        return spaceSep

    def setTemporalDomainClass(self, domainClass):
        self.temporalDomainClass = domainClass

    def createTemporalCollection(self, domainObject):
        if not domainObject:
            raise Exception, "Need a domain object! %s" % domainObject
        register = self.temporalDomainClass.createRegister(
            ownerName='parent',
            owner=domainObject,
            metaAttr=self
        )
        return register
        
    
class MetaDomainObject(BaseDomainMeta):
    "Models a domain object."
    # Todo: Rename to DomainObjectMeta?

    reservedAttrNames = ('id', 'record', 'registerCache', 'projectUrls', 'paths', 'pluginController', 'metaClass', 'meta', 'registerKeyName', 'registerClass', 'registry') 

    def __init__(self, name, dbName='', isUnique=True, isCached=False, title='', comment='', isEditable=True, isHidden=False):
        self.name = name          # object class name
        self.dbName = dbName      # object persistent name
        self.attributes = []      # list of meta attribute objects list
        self.attributeNames = {}  # meta attribute objects keyed by name
        self.isUnique = isUnique  # can't create if match exists
        self.isCached = isCached  # hold in memory
        self.title = title        # presentable name
        #if not self.title:
        #    self.title = self.spaceFromCamel(self.name)
        #self.title = self.spaceFromCamel(self.name)
        self.comment = comment    # presentable explanation
        self.isEditable = isEditable
        self.isHidden = isHidden
        if self.isHidden:
            self.isEditable = False
        self.attributesDeferred = {}
        self.isTemporal = False
        self.sortOn = None

    def setSortOnAttr(self, sortOnName):
        if sortOnName and sortOnName != 'id':
            sortOn = self.attributeNames[sortOnName]
            super(MetaDomainObject, self).__setattr__('sortOn', sortOn)

    def __setattr__(self, attrName, attrVal):
        if issubclass(attrVal.__class__, MetaDomainAttr):
            if attrName in self.getReservedAttrNames():
                msg = "Domain attribute name '%s' is reserved." % attrName
                raise Exception(msg)
            metaAttr = attrVal
            if attrName in self.attributeNames:
                msg = "Domain attribute '%s' somehow already set on '%s' meta object. Attribute names: %s" % (attrName, self.name, self.attributeNames.keys())
                raise Exception(msg)
            metaAttr.setName(attrName)
            self.attributes.append(metaAttr)
            self.attributeNames[attrName] = metaAttr
        else:
            super(MetaDomainObject, self).__setattr__(attrName, attrVal)

    def getReservedAttrNames(self):
        from dm.dom.base import DomainObject
        return [i[0] for i in inspect.getmembers(DomainObject)]

    def createDomainClass(self, baseClass):
        className = self.name
        classAttrs = {
            'meta': self,
        }
        return self.createClass(className, baseClass, classAttrs)

    def createClass(self, name, base, attrs):
        return type(name, (base,), attrs)

    def hasDeferredAttributes(self):
        return len(self.attributesDeferred) != 0

    def getAttr(self, attrName):
        if not attrName in self.attributeNames:
            msg = "Attribute '%s' not defined on domain class '%s'." % (
                attrName, self.name
            )
            raise Exception(msg)
        return self.attributeNames[attrName]


class MetaDomainAttr(BaseDomainMeta):
    "Models a domain object attribute."

    isValueRef = False
    isDomainObjectRef = False
    isAssociateList = False
    isImageFile = False

    def __init__(self, typeName='', name='', dbName='', default=NotDefined, title='', comment='', isHidden=False, isEditable=True, isRequired=True, isSystem=False, getChoices=None, isTemporal=False, isBitemporal=False, isIndexed=False, isUnique=False, isImmutable=False, validators=[], **kwds):
        self.typeName = typeName
        self.dbName = dbName or name
        self.setName(name)
        if default != NotDefined:
            self.default = default
        self.title = title        # presentable name
        #if not self.title:
        #    self.title = self.spaceFromCamel(self.name)
        #self.title = self.spaceFromCamel(self.name)
        self.comment = comment
        self.isHidden = isHidden     # Don't present it (users unable to: init, read, update).
        self.isEditable = isEditable # Allow edits (users can update).
        if self.isHidden:
            self.isEditable = False
        self.isRequired = isRequired # Require a value.
        self.isSystem = isSystem     # Value controlled by system, not even admins can edit...
        if self.isSystem:
            self.isEditable = False  # ...so users also can't edit.
        self.getChoices = getChoices
        self.isIndexed = isIndexed
        self.isTemporal = isTemporal
        if self.isIndexed and self.isTemporal:
            raise Exception, "Can't be indexed and temporal, at the mo."
        self.isBitemporal = isBitemporal
        if self.isBitemporal:
            self.isTemporal = True
        self.isBitemporalActual = False
        self.isUnique = isUnique
        self.isImmutable = isImmutable
        self.validators = validators

    def setName(self, name):
        self.name = name
        if not self.dbName:
            self.dbName = name

    def __repr__(self):
        return "<%s typeName='%s' name='%s'>" % (self.__class__.__name__, self.typeName, self.name)

    def isValueObject(self):
        return False

    def isList(self):
        return self.isAssociateList

    def isPaged(self):
        return False

    def isAggregation(self):
        return False

    def isComposition(self):
        return False

    def setInitialValue(self, domainObject):
        initialValue = self.createInitialValue(domainObject)
        if not initialValue == NotDefined:
            setattr(domainObject, self.name, initialValue) 
    
    def createInitialValue(self, domainObject):
        return None

    def createObjectRepr(self, domainObject):
        try:
            valueRepr = self.createValueRepr(domainObject)
        except Exception, inst:
            valueRepr = "!!VALUE_REPR_ERROR: %s!!" % inst
        return "%s=%s" % (self.name, repr(valueRepr))

    def createSortableRepr(self, domainObject):
        return self.createValueRepr(domainObject)

    def createLabelValue(self, domainObject):
        return unicode(getattr(domainObject, self.name))
    # Todo: Replace createValueRepr() with createLabelValue() everywhere.
    def createValueRepr(self, domainObject, absoluteUriPrefix=None):
        return self.createLabelValue(domainObject)

    def createLabelRepr(self, domainObject):
        return self.createValueRepr(domainObject).encode('utf-8')

    def createAssociatedNamedValues(self, domainObject):
        raise Exception('No createAssociatedNamedValues method on %s' % self)

    def setAttributeFromMultiValueDict(self, domainObject, multiValueDict):
        try:
            attrValue = self.makeValueFromMultiValueDict(multiValueDict)
        except Exception, inst:
            msg = "Exception making '%s' value from multi-value dict: %s" % (
                self.name, multiValueDict
            )
            self.logger.error(msg)
            raise
        if attrValue != self.getAttributeValue(domainObject):
            msg = "Setting '%s' attribute to '%s'." % (self.name, attrValue)
            self.logger.debug(msg)
            self.setAttributeValue(domainObject, attrValue)

    def makeValueFromMultiValueDict(self, multiValueDict):
        raise Exception, "Abstract method not implemented on '%s'." % self.__class__

    def setAttributeValue(self, domainObject, attrValue):
        setattr(domainObject, self.name, attrValue)
        
    def getAttributeValue(self, domainObject):
        return getattr(domainObject, self.name)
        
    def getRegistryAttrName(self, domainObject):
        return None

    def setAttributeValueDb(self, domainObject, attrValue):
        self.setAttributeValue(
            domainObject, self.convertFromDbValue(attrValue)
        )
        
    def getAttributeValueDb(self, domainObject):
        return self.convertToDbValue(
            self.getAttributeValue(domainObject)
        )

    def convertFromDbValue(self, dbValue):
        domainValue = dbValue
        return domainValue
        
    def convertToDbValue(self, domainValue):
        dbValue = domainValue
        return dbValue

    def duplicateTemporal(self):
        attrMeta = self.duplicateSelf()
        if self.isBitemporal:
            attrMeta.isBitemporal = False
            attrMeta.isBitemporalActual = True
            attrMeta.isTemporal = True
        else:
            attrMeta.isTemporal = False
        attrMeta.isRequired = self.isRequired
        return attrMeta

    def duplicateSelf(self):
        return type(self)()

    def validateValue(self, objectData, domainObject, objectRegister):
        self.validateUniqueness(objectData, domainObject, objectRegister)
        for validator in self.validators:
            validator(self, objectData, domainObject, objectRegister)

    def validateUniqueness(self, objectData, domainObject, objectRegister):
        if self.isUnique and self.name in objectData:
            attrValue = self.makeValueFromMultiValueDict(objectData)
            #attrValue = objectData[self.name]
            kwds = { self.name: attrValue }
            # It's either an update with an unchanged value.
            if domainObject and getattr(domainObject, self.name) == attrValue:
                pass
            # Otherwise, an existing object indicates a conflict.
            elif objectRegister.findDomainObjects(**kwds):
                msg = self.formatUniquenessErrorMsg(attrValue)
                raise ValidationError(msg)

    def formatUniquenessErrorMsg(self, attrValue):
        return "The %s '%s' is already being used." % (self.name, attrValue)


class ValueObjectAttr(MetaDomainAttr):
    "Models a domain object value attribute."

    isValueRef = True
    isString = False
    isBoolean = False
    isNumber = False
    isDateTime = False
    isBLOB = False

    def __init__(self, **kwds):
        typeName = self.__class__.__name__
        super(ValueObjectAttr, self).__init__(typeName=typeName, **kwds)

    def isValueObject(self):
        return True 

    def createInitialValue(self, domainObject):
        if hasattr(self, 'default'):
            return self.default
        return NotDefined  # todo: support 'null' default, or forget distinction

    def createSortableRepr(self, domainObject):
        value = getattr(domainObject, self.name)
        return value

    def makeValueFromMultiValueDict(self, multiValueDict):
        attrValue = multiValueDict.get(self.name, '')
        if moddebug and self.debug:
            msg = "Made %s value: %s" % (self.name, attrValue)
            self.logger.debug(msg)
        return attrValue


class String(ValueObjectAttr):
    "Models a domain object string attribute."

    isString = True

    def __init__(self, default='', regex=None, minLength=None, maxLength=None, **kwds):
        self.regex = regex
        self.minLength = minLength
        self.maxLength = maxLength
        super(String, self).__init__(default=default, **kwds)


class Text(String):
    "Models a domain object textual attribute (multi-line)."

    def __init__(self, default='', **kwds):
        super(Text, self).__init__(default=default, **kwds)


from markdown import Markdown
class MarkdownText(Text):
    "Models a 'markdown' textual attribute."

    def createLabelRepr(self, domainObject):
        # Render for reading.
        attrValue = getattr(domainObject, self.name)
        if attrValue:
            md = Markdown(safe_mode='escape')
            return md.convert(attrValue)
        else:
            return ''


class Url(String):
    "Models a domain object url attribute."

    def __init__(self, isRequired=False, **kwds):
        super(Url, self).__init__(isRequired=isRequired, **kwds)


class Password(String):
    "Models a domain object password attribute."

    def __init__(self, isRequired=False, **kwds):
        super(Password, self).__init__(isRequired=isRequired, **kwds)

    def createValueRepr(self, domainObject, absoluteUriPrefix=None):
        # Don't represent the password digest...
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            # ...unless data migration is in progress, when it's required.
            return super(Password, self).createValueRepr(domainObject)
        else:
            return u""

    def makeValueFromMultiValueDict(self, multiValueDict):
        passwordText = multiValueDict.get(self.name, 'pass')
        # Make a digest of the password...
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            # ...unless data migration is in progress, it's already digested.
            attrValue = passwordText
        elif passwordText:
            attrValue = self.makeDigest(passwordText)
        else:
            # Disable digest matching, nothing digests to '' right?
            attrValue = ''  
        if moddebug and self.debug:
            msg = "Made %s value: %s" % (self.name, attrValue)
            self.logger.debug(msg)
        return attrValue

    def makeDigest(self, clearText):
        clearText = unicode(clearText).encode('utf-8')
        # First follow original method (migrated passwords rehashed in v0.19).
        md5hexdigest = md5(clearText).hexdigest() 
        # Now protect passwords better than just using MD5 once. The aim
        # is to put the password digests beyond the scope of rainbow tables
        # so that if the database is stolen, it will be more difficult to
        # obtain passwords (users sometimes register email account passwords).
        key = self.dictionary[PASSWORD_DIGEST_SECRET]
        return hmac(key=key, msg=md5hexdigest, digestmod=sha256).hexdigest()

    def setAttributeValue(self, domainObject, attrValue):
        if attrValue:
            setattr(domainObject, self.name, attrValue)
        

class DateTime(ValueObjectAttr):
    "Models a date-time concern (no timezone)."

    convertor = DateTimeConvertor()
    isDateTime = True

    def __init__(self, default=None, **kwds):
        super(DateTime, self).__init__(default=default, **kwds)

    def makeValueFromMultiValueDict(self, multiValueDict):
        dateTimeString = multiValueDict[self.name]
        attrValue = self.convertor.fromHTML(dateTimeString)
        if moddebug and self.debug:
            msg = "Made %s value: %s" % (self.name, attrValue)
            self.logger.debug(msg)
        return attrValue

    def createValueRepr(self, domainObject, absoluteUriPrefix=None):
        dateTimeObject = getattr(domainObject, self.name)
        dateTimeString = self.convertor.toHTML(dateTimeObject)
        return dateTimeString
            
    def createLabelRepr(self, domainObject):
        dateTimeObject = getattr(domainObject, self.name)
        dateTimeString = self.convertor.toLabel(dateTimeObject)
        return dateTimeString


class RDateTime(DateTime):
    "Models a domain object date attribute."
    
    convertor = RDateTimeConvertor()


class RNSDateTime(DateTime):
    "Models a domain object date attribute."
    
    convertor = RNSDateTimeConvertor()


class Date(DateTime):
    "Models a domain object date attribute."
    
    convertor = DateConvertor()


class RDate(Date):
    "Models a domain object date attribute, but with 'reverse' ANSI format."
    
    convertor = RDateConvertor()


class DateOfBirth(RDate):
    "Models a date of birth."
    
    convertor = DateOfBirthConvertor()


class Boolean(ValueObjectAttr):
    "Models a domain object boolean attribute."

    isBoolean = True
    trueStrings = ['on', 'true', 't', '1', 'yes', 'y']

    def __init__(self, default=False, isRequired=False, **kwds):
        super(Boolean, self).__init__(
            default=default, isRequired=isRequired, **kwds
        )

    def makeValueFromMultiValueDict(self, multiValueDict):
        if self.name not in multiValueDict:
            attrValue = False
        else:
            boolVal = multiValueDict[self.name]
            if boolVal.__class__ == False.__class__:
                attrValue = boolVal
            else:
                attrValue = str(boolVal).lower() in self.trueStrings
            if moddebug and self.debug:
                msg = "Made %s value: %s" % (self.name, attrValue)
                self.logger.debug(msg)
        return attrValue

    def createValueRepr(self, domainObject, absoluteUriPrefix=None):
        attrValue = getattr(domainObject, self.name)
        if attrValue:
            return u'on'
        else:
            return u''

    def createLabelRepr(self, domainObject):
        attrValue = getattr(domainObject, self.name)
        if attrValue:
            return 'On'
        else:
            return 'Off'


class NumberObjectAttr(ValueObjectAttr):

    isNumber = True
    numberType = None

    def __init__(self, default=0, minValue=None, maxValue=None, **kwds):
        self.minValue = minValue
        self.maxValue = maxValue
        super(NumberObjectAttr, self).__init__(default=default, **kwds)

    def resolvePathPart(self, pathPart, **kwds):
        return self.numberType(pathPart)

    def makeValueFromMultiValueDict(self, multiValueDict):
        if multiValueDict[self.name]:
            attrValue = self.numberType(multiValueDict[self.name])
        else:
            if hasattr(self, 'default'):
                attrValue = self.default
            else:
                attrValue = 0
        if moddebug and self.debug:
            msg = "Made %s value: %s" % (self.name, attrValue)
            self.logger.debug(msg)
        return attrValue

    def createValueRepr(self, domainObject, absoluteUriPrefix=None):
        return getattr(domainObject, self.name)

    def createLabelRepr(self, domainObject):
        attrValue = getattr(domainObject, self.name)
        return str(attrValue)


class Integer(NumberObjectAttr):
    "Models a domain object integer attribute."

    numberType = int


class Float(NumberObjectAttr):
    "Models a domain object floating-type number attribute."

    numberType = float


class BLOB(ValueObjectAttr):
    "Models any binary large object attribute."

    isBLOB = True

    def makeValueFromMultiValueDict(self, multiValueDict):
        return multiValueDict[self.name]


class Pickle(BLOB):
    "Models any Python object attribute."

    pass
    

class ImageFile(MetaDomainAttr):
    "Models an image attribute."
    
    isImageFile = True

    def __init__(self, default='', maxWidth=None, **kwds):
        super(ImageFile, self).__init__(default=default, typeName='ImageFile', **kwds)
        self.maxWidth = maxWidth

    def getFileContent(self, mapper):
        filePath = self.getFilepath(mapper)
        if filePath and os.path.exists(filePath):
            file = open(filePath)
            content = file.read()
            file.close()
            return content
        else:
            return None

    def setFileContent(self, mapper, content):
        if mapper:
            filePath = self.getFilepath(mapper)
            if filePath:
                file = open(filePath, 'wb')
                file.write(content)
                file.close()
            if self.maxWidth != None:
                import Image  # Not ideal: avoids dependency when not needed.
                image = Image.open(filePath)
                (width, height) = image.size
                if width > self.maxWidth:
                    widthToHeightRatio = float(width) / height
                    newWidth = self.maxWidth
                    newHeight = newWidth / widthToHeightRatio
                    newSize = (newWidth, newHeight)
                    newImage = image.resize(newSize, Image.ANTIALIAS)
                    newImage.save(filePath)

    def getFilepath(self, mapper):
        # Extn .png doesn't break PIL Image.save() after resize; no extn does.
        fileName = "%s%s.png" % (mapper.__class__.__name__, mapper.id)
        dirPath = self.dictionary[IMAGES_DIR_PATH]
        return os.path.join(dirPath, fileName)


class DomainObjectAssociation(MetaDomainAttr):
    "Associates domain objects with other domain objects."

    def getAllChoices(self, objectRegister, domainObject):
        if callable(self.getChoices):
            choices = self.getChoices(objectRegister, domainObject)
        else:
            choices = []
            try:
                associateRegister = self.getAssociatedObjectRegister(domainObject)
                objectList = []
                if associateRegister != []:
                    objectList = associateRegister.getSortedList()
                for associateObject in objectList:
                    uri = associateObject.getUri()
                    label = associateObject.getLabelValue()
                    choice = (uri, label)
                    choices.append(choice)
                return choices
            except Exception, inst:
                trace = traceback.format_exc()
                self.logger.error("Error: %s: %s" % (inst, trace))
                message = "Couldn't get choices for %s: %s" % (
                   self.typeName, unicode(inst)
                )
                raise Exception(message)
        self.logger.debug("Choices for '%s': %s" % (self.name, choices))
        return choices

    def getAssociatedObjectRegister(self, domainObject):
        return self.getDomainRegister()

    def getDomainRegister(self):
        domainClass = self.getDomainClass()
        return domainClass.principalRegister or domainClass.createRegister()

    def getDomainClass(self):
        return self.registry.getDomainClass(self.typeName)
        
    def getObjectByKey(self, key, **kwds):
        domainRegister = self.getDomainRegister()
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            # Need all objects when migrating.
            if domainRegister.isStateful:
                domainRegister = domainRegister.getAll()
        return domainRegister.find(key, **kwds)

    def resolvePathPart(self, pathPart, **kwds):
        return self.getObjectByKey(pathPart, **kwds)


class DomainObjectRef(DomainObjectAssociation):
    "Associates a domain object with a single aquaintance."

    isDomainObjectRef = True

    def __init__(self, className='', isSimpleOption=False, **kwds):
        self.isSimpleOption = isSimpleOption
        if not className:
            raise Exception, "No className for DomainObjectRef instance."
        super(DomainObjectRef, self).__init__(typeName=className, **kwds)
    
    def formatUniquenessErrorMsg(self, attrValue):
        return "There is already one for '%s'." % attrValue.getLabelValue()

    def getAquaintance(self, domainObject):
        return getattr(domainObject, self.name)
        
    def getRegistryAttrName(self, domainObject):
        aquintanceClass = self.getDomainClass()
        return aquintanceClass.getRegistryAttrName()

    def createInitialValue(self, domainObject):
        if hasattr(self, 'default'):
            if self.default:
                return self.getObjectByKey(self.default)
        return None

    def createValueRepr(self, domainObject, absoluteUriPrefix=None):
        value = getattr(domainObject, self.name)
        if value:
            return value.getUri(absoluteUriPrefix=absoluteUriPrefix)
        else:
            return value
       
    def createLabelRepr(self, domainObject):
        value = getattr(domainObject, self.name)
        if value == None:
            return ""
        elif value:
            return value.getLabelValue()
        else:
            return value
       
    def makeValueFromMultiValueDict(self, multiValueDict):
        refValue = multiValueDict[self.name]
        if refValue:
            if self.dictionary[DB_MIGRATION_IN_PROGRESS] and (isinstance(refValue, int) or (isinstance(refValue, basestring) and refValue[0] != '/')):
                attrValue = self.getObjectByKey(refValue)
            else:
                attrValue = self.registry.dereference(refValue).target
        elif hasattr(self, 'default'):
            attrValue = self.getObjectByKey(self.default)
        else:
            attrValue = None
        if moddebug and self.debug:
            msg = "Made %s value: %s" % (self.name, attrValue)
            self.logger.debug(msg)
        return attrValue

    def duplicateSelf(self):
        return type(self)(self.typeName)


class Aggregation(object):
    "Causes deletion of aggregatee by aggregator when aggregator is deleted."

    def isAggregation(self):
        return True


class Composition(Aggregation):
    "Causes creation of aggregatee by aggregator when aggregator is created."

    def isComposition(self):
        return True


class Associate(DomainObjectRef):
    "Models aquaintance with a domain object."
    pass


class Aggregate(Aggregation, Associate):
    "Models aggregation of a domain object."
    pass


class Composite(Composition, Aggregate):
    "Models composition of a domain object."
    pass


class TemporalRegisterMixin(object):
    "Use real register if in real time, otherwise use temporal history."

    # When using real register, call super methods with given params.
    # To use temporal history, get parent's revision object and pull
    # keys and values from it's register.

    timepoint = RequiredFeature('Timepoint')

    # Todo: Fix this before using temporal properties on HasMany attrs!


    # Methods interrupted.

    def __iter__(self):
        if self.timepoint.isReset(): 
            return super(TemporalRegisterMixin, self).__iter__()
        else:
            return iter(self.getCurrentValues())

    def keys(self, **kwds):
        if self.timepoint.isReset(): 
            return super(TemporalRegisterMixin, self).keys(**kwds)
        else:
            return self.getCurrentKeys()

    def has_key(self, key):
        if self.timepoint.isReset(): 
            return super(TemporalRegisterMixin, self).has_key(key)
        else:
            return key in self.getCurrentKeys()

    def find(self, key):
        if self.timepoint.isReset(): 
            return super(TemporalRegisterMixin, self).find(key)
        else:
            return self.getCurrentDict()[key]

    def count(self):
        if self.timepoint.isReset(): 
            return super(TemporalRegisterMixin, self).count()
        else:
            return len(self.getCurrentAssociations())


    # Methods introduced.


    def isRealTime(self):
        if self.timepoint.isReset():
            return True
        elif not self.owner:
            raise Exception, "Temporal registers need an owner for versions!"
        else:
            return False

    def getCurrentDict(self):
        associations = self.getCurrentAssociations()
        currentDict = {}
        for a in associations:
            currentDict[a.recordedKey] = a.recordedValue
        return currentDict
           
    def getCurrentKeys(self):
        associations = self.getCurrentAssociations()
        return [a.recordedKey for a in associations]
           
    def getCurrentValues(self):
        associations = self.getCurrentAssociations()
        return [a.recordedValue for a in associations]
           
    def getCurrentAssociations(self):
        currentVersion = self.getCurrentVersion()
        return getattr(currentVersion, self.metaAttr.name)

    def getCurrentVersion(self):
        return self.owner.temporalHistory.getCurrent()


class AssociateList(DomainObjectAssociation):
    "Models aquaintance with several domain objects."

    isAssociateList = True
    isPagedList = False
    registerClass = None

    def __init__(self, className='', key='', owner='', ownerAsOwnerAttr='', isRequired=False, **kwds):
        super(AssociateList, self).__init__(typeName=className, isRequired=isRequired, **kwds)
        self.key = key # Todo: Rename to keyName.
        # Register key name defaults to the domainClass registerKeyName attribute.
        self.owner = owner # Todo: Rename to ownerName.
        self.ownerAsOwnerAttr = ownerAsOwnerAttr # Todo: Rename.
   
    def getKey(self):
        if not self.key:
            domainClass = self.getDomainClass()
            self.key = domainClass.registerKeyName
        return self.key

    def createInitialValue(self, domainObject):
        # Just instantiate a register for this attribute on this object.
        if type(domainObject).meta.isCached:
            return self.createRegister(domainObject)
        return NotDefined

#    def setInitialValue(self, domainObject):
#        pass

    def createRegister(self, domainObject):
        #self.logger.info("Model: Creating %s register (in meta) with owner: %s" % (self.typeName, domainObject))
        #self.logger.info("Model: Creating %s register (in meta) with owner." % (self.typeName))
        domainClass = self.registry.getDomainClass(self.typeName)
        registerClass = domainClass.registerClass
        if self.isTemporal:
            className = "Temporal%s" % registerClass.__name__
            classBases = (TemporalRegisterMixin, registerClass)
            registerClass = type(className, classBases, {})
        register = registerClass(
            typeName=self.typeName,
            keyName=self.getKey(),
            ownerName=self.owner,
            owner=domainObject,
            ownerAsOwnerAttrName=self.ownerAsOwnerAttr,
            metaAttr=self,
            isCached=domainClass.meta.isCached,
        )
        return register

    def createValueRepr(self, domainObject, absoluteUriPrefix=None):
        register = self.getAssociationObjectRegister(domainObject)
        if self.getDomainClass().isImplicitAssociation:
            return register.getUris(absoluteUriPrefix)
        else:
            return register.getUri(absoluteUriPrefix)

    def createLabelRepr(self, domainObject):
        register = self.getAssociationObjectRegister(domainObject)
        labelsList = []
        if self.isKeyDomainObject():
            labelsList = [unicode(register.getRegisterKey(i).getLabelValue()) for i in register.getSortedList()]
            labelsList = ", ".join(labelsList)
        else:
            labelsList = [unicode(i.getLabelValue()) for i in register.getSortedList()]
            labelsList = ", ".join(labelsList)
        return labelsList or "_"

    def createValueLabelList(self, domainObject):
        register = self.getAssociationObjectRegister(domainObject)
        valueLabels = []
        isKeyDomainObject = self.isKeyDomainObject()
        for domainObject in register.getSortedList():
            registerKey = register.getRegisterKey(domainObject)
            valueLabel = {}
            if isKeyDomainObject:
                value = registerKey.getRegisterKeyValue() 
                label = unicode(registerKey.getLabelValue())
            else:
                value = registerKey
                label = unicode(domainObject.getLabelValue())
            valueLabel['value'] = value
            valueLabel['label'] = label
            valueLabel['associationObject'] = register[registerKey]
            valueLabels.append(valueLabel)
        return valueLabels

    def createAssociatedNamedValues(self, domainObject):
        associatedNamedValues = []
        associationRegister = self.getAssociationObjectRegister(domainObject)
        if self.isKeyDomainObject():  # Non-bomb proof implied many-many, fix.
            associationObjects = associationRegister.getSortedList()
            for associationObject in associationObjects:
                associatedObject = associationRegister.getRegisterKey(
                    associationObject
                )
                namedValue = {}
                keyValue = associatedObject.getRegisterKeyValue() 
                namedValue['key'] = keyValue
                labelValue = unicode(associatedObject.getLabelValue())
                namedValue['label'] = labelValue
                namedValue['associatedObject'] = associatedObject
                namedValue['associationObject'] = associationObject
                associatedNamedValues.append(namedValue)
        else:
            for associatedObject in associationRegister.getSortedList():
                namedValue = {}
                keyValue = associatedObject.getRegisterKeyValue() 
                namedValue['key'] = keyValue
                labelValue = unicode(associatedObject.getLabelValue())
                namedValue['label'] = labelValue
                namedValue['associatedObject'] = associatedObject
                namedValue['associationObject'] = associatedObject
                associatedNamedValues.append(namedValue)
        return associatedNamedValues

    def setAttributeFromMultiValueDict(self, domainObject, multiValueDict):
        if hasattr(multiValueDict, 'getlist'):
            # It's a MultiValueDict (Django 0.96).
            associatedObjectUris = multiValueDict.getlist(self.name)
        else:
            # It's just a dict (Django 1.0).
            associatedObjectUris = multiValueDict[self.name]
        associatedObjectRegister = self.getAssociatedObjectRegister(domainObject) # e.g. licenses for a project
        associationObjectRegister = self.getAssociationObjectRegister(domainObject) # e.g. projectlicense "join table"
        # Delete where surplus.
        for associationObject in associationObjectRegister:
            if self.isKeyDomainObject():
                associatedObject = getattr(associationObject, self.getKey())
                associatedObjectUri = associatedObject.getUri()
            else:
                raise Exception, "Temporarily not supported."
            if not unicode(associatedObjectUri) in associatedObjectUris:
                associationObject.delete()
        # Create where missing.
        for associatedObjectUri in associatedObjectUris:
            if associatedObjectUri == None:
                continue
            if self.isKeyDomainObject():
                associatedObject = self.registry.dereference(associatedObjectUri).target
                if associatedObject and associatedObject not in associationObjectRegister:
                    associationObjectRegister.create(associatedObject)
            else:
                raise Exception, "Temporarily not supported."

    def isKeyDomainObject(self):
        if self.getKey() == 'id':
            return False
        keyAttr = self.getKeyMetaAttribute()
        return keyAttr.isDomainObjectRef
        
    def getKeyMetaAttribute(self):
        domainClass = self.getDomainClass()
        if self.getKey() in domainClass.meta.attributeNames:
            return domainClass.meta.attributeNames[self.getKey()]
        else:
            msg = "For class '%s', key '%s' not in attributes: %s." % (
                domainClass.meta.name,
                self.getKey(),
                domainClass.meta.attributeNames.keys(),
            )
            raise Exception(msg)
        
    def getAssociationObject(self, domainObject, keyValue):
        register = self.getAssociationObjectRegister(domainObject)
        keyValue = self.getKeyValue(keyValue)
        return register[keyValue]

    def getAssociationObjectRegister(self, domainObject):
        return getattr(domainObject, self.name)
        
    def getKeyValue(self, domainObject, keyValue):
        # If the key is a domain object, then the key value string needs to be
        # converted into a key value domain object.
        if self.isKeyDomainObject():
            keyMeta = self.getKeyMetaAttribute()
            associateClassName = keyMeta.typeName
            associateClass = self.registry.getDomainClass(associateClassName)
            associateRegister = associateClass.createRegister()
            keyValue = associateRegister[keyValue]
        return keyValue

    def getAssociatedObjectRegister(self, domainObject):
        # If the key is a domain object, then it is assumed that the
        # register keys are the associated objects in a many-many relationship,
        # and the association objects are being used to model to associations.
        # Otherwise the association objects are also the associated objects, 
        # and the association is modelled as an attribute on associated object.
        # Todo: Make this explicit somehow.
        register = None
        if self.isKeyDomainObject():
            keyMeta = self.getKeyMetaAttribute()
            associateClassName = keyMeta.typeName
            associateClass = self.registry.getDomainClass(associateClassName)
            register = associateClass.createRegister()
        else:
            if domainObject:
                register = self.getAssociationObjectRegister(domainObject)
            else:
                register = []
        return register   

    def makeValueFromMultiValueDict(self, multiValueDict):
        if self.name not in multiValueDict:
            attrValue = []
        else:
            refValue = multiValueDict[self.name]
            raise Exception, "Need to finish this?"
        return attrValue
        #if refValue:
        #    attrValue = self.getObjectByKey(refValue)
        #elif hasattr(self, 'default'):
        #    attrValue = self.getObjectByKey(self.default)
        #else:
        #    attrValue = None
        #if moddebug and self.debug:
        #    msg = "Made %s value: %s" % (self.name, attrValue)
        #    self.logger.debug(msg)
        #return attrValue


class HasA(Associate):
    "Models aquaintance with a domain object."
    pass


class HasMany(AssociateList):
    "Models aquaintance with several domain objects."
    pass


class AggregatesMany(Aggregation, HasMany):
    "Models aggregation of several domain objects."
    pass

