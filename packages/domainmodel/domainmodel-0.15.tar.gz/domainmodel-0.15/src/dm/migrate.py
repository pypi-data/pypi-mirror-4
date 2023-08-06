from dm.ioc import RequiredFeature
from dm.view.manipulator import DomainObjectManipulator
from dm.util.datastructure import MultiValueDict
from dm.exceptions import DataMigrationError
from dm.dictionarywords import DB_MIGRATION_IN_PROGRESS
from dm.strategy import BaseStrategy
import os
import sys
from dm.on import json
from dm.dom.pickers import GetMigrationAttributes

# Todo: Support for merging data sets (id-fidelity is enforced now).
# Todo: Add support for comments in plan files!

class DomainModelDumper(object):

    def __init__(self):
        self.registry = RequiredFeature("DomainRegistry")
        self.dictionary = RequiredFeature("SystemDictionary")
        # Load plugin model classes into domain class register.
        self.pluginController = RequiredFeature("PluginController")
        self.pluginController.getPlugins() 
        self.jsonDataDump = ''
        self.dataDump = None

    def dumpData(self):
        self.dictionary.set(DB_MIGRATION_IN_PROGRESS, '1')
        self.dataDump = {}
        domainClassRegister = self.registry.getDomainClassRegister()
        # Dump all classes.
        for className in domainClassRegister.keys():
            classData = {}
            domainClass = domainClassRegister[className]
            #print "Dumping register %s" % className
            # Dump class meta data.
            picker = GetMigrationAttributes(domainClass.meta)
            migrationAttrs = picker.pick()
            metaClassData = {}
            for attr in migrationAttrs:
                metaClassData[attr.name] = attr.typeName
            classData['metaData'] = metaClassData
            # Dump all instances.
            classRegister = domainClass.createRegister()
            if classRegister.isStateful:
                classRegister = classRegister.getAll()
            for domainObject in classRegister:
                manipulator = DomainObjectManipulator(classRegister, domainObject, pickerClass=GetMigrationAttributes)
                domainObjectData = manipulator.domainObjectAsDictValues()
                for (name, value) in domainObjectData.items():
                    if type(value) == unicode:
                        value = value.encode('utf8', 'ignore')
                        domainObjectData[name] = value
                classData[domainObject.id] = domainObjectData
            self.dataDump[className] = classData
        self.dictionary.set(DB_MIGRATION_IN_PROGRESS, '')
        return self.dataDump

    def dumpDataAsJson(self):
        self.dumpData()
        self.jsonDataDump = json.dumps(self.dataDump)
        return self.jsonDataDump

    def dumpDataToFile(self, dumpFilePath):
        dumpFile = open(dumpFilePath, 'w')
        dumpFileContent = self.dumpDataAsJson()
        dumpFile.write(dumpFileContent)


class DomainModelLoader(object):

    def __init__(self, isMerge=False):
        self.isMerge = isMerge
        self.logger = RequiredFeature("Logger")
        self.registry = RequiredFeature("DomainRegistry")
        self.dictionary = RequiredFeature("SystemDictionary")
        self.jsonDataDump = ''
        self.dataDump = None
        if not self.isMerge and self.registry.states:
            raise Exception, "Database is already initialised."

    def loadDataFromFile(self, dumpFilePath):
        # Todo: Wrap file access in try/except block.
        dumpFile = open(dumpFilePath, 'r')
        dumpFileContent = dumpFile.read()
        self.loadDataAsJson(dumpFileContent)

    def loadDataAsJson(self, jsonDataDump):
        self.jsonDataDump = jsonDataDump
        try:
            dumpedData = json.loads(self.jsonDataDump)
        except Exception, inst:
            msg = "Couldn't parse JSON string: %s: %s" % (
                self.jsonDataDump, inst
            )
            raise Exception, msg
        self.loadData(dumpedData)

    def loadData(self, dataDump):
        self.dataDump = dataDump
        self.migrateDataDump()
        self.dictionary.set(DB_MIGRATION_IN_PROGRESS, '1')
        self.identifyReferences(self.dataDump.keys())
        self.determineImportOrder()
        self.importObjectRecords()
        # Plugin system domain model classes won't be registered first time.
        if self.unresolvedClassNames:
            self.identifyReferences(list(self.unresolvedClassNames))
            self.determineImportOrder()
            self.importObjectRecords()
            if self.unresolvedClassNames:
                raise Exception("Error: Couldn't find domain classes for: %s" % self.unresolvedClassNames)
        self.dictionary.set(DB_MIGRATION_IN_PROGRESS, '')

    def migrateDataDump(self):
        pass

    def getDumpVersion(self):
        return self.dataDump['System']['1']['version']

    def setDumpVersion(self, version):
        self.dataDump['System']['1']['version'] = version

    def deleteDomainClass(self, domainClassName):
        if domainClassName in self.dataDump:
            del(self.dataDump[domainClassName])

    def findInstances(self, domainClassName, **kwds):
        instances = {}
        if domainClassName in self.dataDump:
            for (id, data) in self.dataDump[domainClassName].items():
                if id == 'metaData':
                    continue
                isMatch = True
                for name, value in kwds.items():
                    if data[name] != value:
                        isMatch = False
                        break
                if isMatch:
                    instances[id] = data
        return instances

    def addInstance(self, domainClassName, **data):
        newId = self.getNewId(domainClassName)
        self.dataDump[domainClassName][str(newId)] = data
        return newId

    def deleteInstance(self, domainClassName, oldId):
        del(self.dataDump[domainClassName][str(oldId)])

    def getNewId(self, domainClassName):
        ids = self.getDomainClassIds(domainClassName)
        return (len(ids) and ids[0] or 0) + 1

    def getDomainClassIds(self, domainClassName):
        ids = [int(i) for i in self.dataDump[domainClassName].keys() if i != 'metaData']
        ids.sort(reverse=True)
        return ids

    def identifyReferences(self, classNames):
        "Looks for HasA attrs on classes, collects by referenced class."
        self.unresolvedClassNames = []
        self.classReferences = {}
        self.outstandingReferences = {}
        for className in classNames:
            try:
                domainClass = self.registry.getDomainClass(className)
            except Exception, inst:
                self.unresolvedClassNames.append(className)
                continue
            attrReferences = {}
            for attr in domainClass.meta.attributes:
                if attr.isDomainObjectRef:
                    attrReferences[attr.name] = attr.typeName 
                #elif attr.isAssociateList:
                #    attrReferences[attr.name] = attr.typeName
            self.classReferences[className] = attrReferences
            self.outstandingReferences[className] = attrReferences
                    
    def hasOutstandingReferences(self, className):
        "Checks whether named class references outstanding classes."
        classRefs = self.outstandingReferences[className]
        for attrTypeName in classRefs.values():
            if attrTypeName == className:
                continue
            if attrTypeName in self.outstandingReferences:
                return True
        return False
        
    def determineImportOrder(self):
        "Determines import order based on id reference dependencies."
        self.importOrder = []
        while(True):
            unreferencingClassName = ''
            unreferencedClassName = ''
            for className in self.outstandingReferences.keys():
                if not self.hasOutstandingReferences(className):
                    unreferencingClassName = className
                    break
            if unreferencingClassName:
                self.importOrder.append(className)
                if className in self.outstandingReferences.keys():
                    del(self.outstandingReferences[className])
                    if not len(self.outstandingReferences):
                        break
                else:
                    msg = "Class name %s not in outstanding list: %s" % (
                        className,
                        self.outstandingReferences.keys()
                    )
                    raise Exception(msg)
            else:
                break
        if self.outstandingReferences:
            msg = "Classes outstanding when determining import order: %s" % (
                self.outstandingReferences
            )
            raise DataMigrationError(msg)
       
    def importObjectRecords(self):
        # Add each object to database
        # substitute ids where changed
        # store new id
        self.idMap = {}
        #print "Import order:", self.importOrder
        for className in self.importOrder:
            sys.stdout.write('\rImporting %s objects' % (className))
            sys.stdout.flush()
            classData = self.dataDump[className]
            objectCount = len(classData.keys()) - 1
            domainClass = self.registry.getDomainClass(className)
            classRegister = domainClass.createRegister()
            #del(self.dataDump[className])
            manipulator = DomainObjectManipulator(classRegister, pickerClass=GetMigrationAttributes)
            for objectId in classData.keys():
                if objectId == 'metaData':
                    continue
                objectData = classData[objectId]
                del(classData[objectId])
                objectIdInt = int(objectId)
                classData[objectIdInt] = objectData
            classDataKeys = classData.keys()
            classDataKeys.remove('metaData')
            classDataKeys.sort()
            #print "Iterating over %s %s" % (className, classDataKeys)
            reflexiveClassData = {}
            freshDomainObjects = {}
            importCount = 0
            isCatchingUp = False
            isLoadingClass = False
            for objectId in classDataKeys:
                #if objectId == 'metaData':
                #    continue
                objectData = classData[objectId]
                #del(classData[objectId])
                msg = "Importing %s #%s using %s" % (
                    className, objectId, objectData
                )
                self.logger.info(msg)
                strObjectData = {}
                reflexiveStrObjectData = {}
                for attr in domainClass.meta.attributes:
                    if attr.isAssociateList:
                        continue
                    elif attr.isImageFile:
                        continue
                    elif objectData.has_key(attr.name):
                        value = objectData[attr.name]
                        if attr.isDomainObjectRef and value.__class__ in [int, long]:
                            idMapKey = "%s %s" % (attr.typeName, value)
                            if idMapKey in self.idMap.keys():
                                mappedValue = self.idMap[idMapKey]
                                #msg = "Updating %s %s from %s to %s" % (
                                #    className,
                                #    attr.name,
                                #    value,
                                #    mappedValue,
                                #)
                                #print msg
                                value = mappedValue
                        if attr.isDomainObjectRef and (attr.typeName==className):
                            reflexiveStrObjectData[attr.name] = value
                        else:
                            strObjectData[attr.name] = value
                if reflexiveStrObjectData:
                    reflexiveClassData[objectId] = reflexiveStrObjectData
                objectDict = {} #MultiValueDict()
                objectDict.update(strObjectData)
                behindWithId = True
                sacrificialRecords = []
                try:
                    while(behindWithId):
                        try:
                            manipulator.create(objectDict)
                        except:
                            print objectDict
                            raise
                        if manipulator.manipulationErrors:
                            msg = "There were errors creating %s object: %s: %s" % (className, strObjectData, manipulator.manipulationErrors)
                            if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
                                print "Warning: %s" % msg
                                break
                            else:
                                raise Exception(msg)
                        domainObject = manipulator.domainObject
                        if not domainObject:
                            raise Exception("Manipulator has no domain object.")
                        #print "Created %s" % domainObject
                        if domainObject.id > objectId:
                            msg = "Index id %s is ahead of import id %s (%s). Perhaps database already exists?" % (
                                domainObject.id, objectId, className
                            )
                            #print "Warning: %s" % msg
                            raise Exception, msg
                        elif domainObject.id == objectId or not domainClass.isObjectIdSignificant:
                            #print "Perfect ID match!"
                            behindWithId = False
                            #if isCatchingUp:
                            #    sys.stdout.write('\n')
                            #    sys.stdout.flush()
                            #    isCatchingUp = False
                            #isLoadingClass = True
                            importCount += 1
                            sys.stdout.write('\rImporting %s %s objects: %s          ' % (objectCount, className, importCount))
                            sys.stdout.flush()
                        elif domainObject.id < objectId:
                            #if isLoadingClass:
                            #    sys.stdout.write('\n')
                            #    sys.stdout.flush()
                            #    isLoadingClass = False
                            #isCatchingUp = True
                            sys.stdout.write('\rCatching up with %s object ID %s: %s ' % (className, objectId, domainObject.id))
                            sys.stdout.flush()
                            sacrificialRecords.append(domainObject)
                            #msg = "Skipping #%s to catch up with index." % (
                            #    domainObject.id
                            #)
                            #print msg
                finally:
                    for domainObject in sacrificialRecords:
                        #print "Dropping sacrificial record: %s" % domainObject
                        self.dropRecord(domainObject)
                        
                domainObject = manipulator.domainObject
                newObjectId = domainObject.id
                freshDomainObjects[newObjectId] = domainObject
                if newObjectId != objectId:
                    idMapKey = "%s %s" % (className, objectId)
                    self.idMap[idMapKey] = newObjectId
                msg = "Importing %s #%s OK" % (
                    className, objectId
                )

            reflexiveIds = reflexiveClassData.keys()
            reflexiveIds.sort()
            for id in reflexiveIds:
                reflexiveStrObjectData = reflexiveClassData[id]
                domainObject = freshDomainObjects.pop(id)
                objectDict = {}
                objectDict.update(reflexiveStrObjectData)
                for attrName in reflexiveStrObjectData:
                    metaAttr = domainObject.meta.attributeNames[attrName]
                    refObject = metaAttr.makeValueFromMultiValueDict(objectDict)
                    setattr(domainObject, attrName, refObject)
                    domainObject.save()

            sys.stdout.write("\rImporting %s %s objects: OK                     " % (objectCount, className))
            sys.stdout.flush()
            sys.stdout.write('\n')
            sys.stdout.flush()
            #print "Importing %s objects completed OK." % className
        #print "Imported all domain objects records OK."

    def dropRecord(self, domainObject):
        domainObject.delete()
        if hasattr(domainObject, 'purge'):
            domainObject.purge()


class FilesDumper(object):

    def __init__(self):
        self.registry = RequiredFeature("DomainRegistry")
        self.dictionary = RequiredFeature("SystemDictionary")

    def dumpInDir(self, filesDumpDirPath):
        self.filesDumpDirPath = filesDumpDirPath
        self.assertDirExists()

    def assertDirExists(self):
        if not os.path.exists(self.filesDumpDirPath):
            raise Exception("Files dump dir not found: %s" % (
                self.filesDumpDirPath
            ))


class UndefinedDomainModelValue(object):
    pass


class DomainModelMigrator(BaseStrategy):
    "Migrates dumped data structure according to plan steps."

    def __init__(self, dumpedData, planSteps):
        """
        Constructs data migration strategy.
        
        dumpedData is a dict of dicts of dicts. The first level contains
        class data and is keyed by class name, the second level contains
        domain objects of each class and is keyed by integer id, and the
        third level contain the attribes of each domain object and is
        keyed by the attribute names of that class. The domain objects
        are accompanied by a class definition keyed by 'metaData' which
        contains the attribute types keyed by attribute name.
        
        For example:
        
        
        dumpedData = {
            'Person': {
                'metaData': {
                    'name': 'String',
                    'email': 'Email',
                },
                '1': {
                    'name': 'fred',
                    'email': 'fred@domain.com',
                },
                '2': {
                    'name': 'jill',
                    'email': 'jill@domain.com',
                },
                '3': {
                    'name': 'joe',
                    'email': 'joe@domain.com',
                },
            },
            'Project': {
                'metaData': {
                    'name': 'String',
                    'description': 'String',
                },
                '1': {
                    'name': 'yellow',
                    'description': 'yellow yellow yellow',
                },
                '2': {
                    'name': 'red',
                    'description': 'red red red',
                },
            },
            'Place': {
                'metaData': {
                    'title': 'String',
                    'location': 'String',
                    'image': 'String'
                    'discovered': 'DateTime'
                },
                '1': {
                    'title': 'Hill Top',
                    'location': 'GR465798',
                    'image': ''
                }
            }
        }

        planSteps is an array of strings. Each string is a migration step
        defining a single change required of the dumped data. For example:

        planSteps = [
            'drop class Project',
            'move class Person User',
            'add class TrainingSession',
            'drop attribute Place image',
            'move attribute Place title officalname'
            'add attribute Place latitude',
            'convert attribute Place discovered datetime_to_date',
        ]
        """
        self.dumpedData = dumpedData
        self.planSteps = planSteps

    def migrate(self):
        if 'classNames' in self.dumpedData:
            del(self.dumpedData['classNames'])
        for planStep in self.planSteps:
            #print "Raw plan step: %s" % planStep
            parts = planStep.split(' ')
            action = parts[0]
            object = parts[1]
            className = parts[2]
            if object == 'class':
                if action == 'add':
                    #print "  adding class %s" % className
                    pass
                elif action == 'drop':
                    #print "  droping class %s" % className
                    del(self.dumpedData[className])
                elif action == 'move':
                    classRename = parts[3]
                    #print "  moving class %s to %s" % (className, classRename)
                    classData = self.dumpedData[className]
                    del(self.dumpedData[className])
                    self.dumpedData[classRename] = classData
                else:
                    msg = "Unsupported action: %s" % action
                    raise DataMigrationError(msg)
            elif object == 'attribute':
                attrName = parts[3]
                if action == 'add':
                    #print "  adding class attribute %s %s" % (
                    #    className, attrName
                    #)
                    pass
                elif action == 'drop':
                    #print "  dropping class attribute %s %s" % (
                    #    className, attrName
                    #)
                    classData = self.dumpedData[className]
                    for key in classData.keys():
                        domainObjectData = classData[key]
                        del(domainObjectData[attrName])
                elif action == 'move':
                    attrRename = parts[4]
                    #print "  moving class attribute %s %s to %s" % (
                    #    className, attrName, attrRename
                    #)
                    classData = self.dumpedData[className]
                    for key in classData.keys():
                        domainObjectData = classData[key]
                        attrData = domainObjectData[attrName]
                        del(domainObjectData[attrName])
                        domainObjectData[attrRename] = attrData
                elif action == 'convert':
                    conversionName = parts[4]
                    #print "  converting class attribute %s %s with %s" % (
                    #    className, attrName, conversionName
                    #)
                    classData = self.dumpedData[className]
                    conversionMethod = None

                    def convertDateTimeToDate(dateTimeString):
                        if dateTimeString in ['', None]:
                            return UndefinedDomainModelValue
                        from dm.datetimeconvertor import DateTimeConvertor
                        dateTimeConvertor = DateTimeConvertor()
                        dateTime = dateTimeConvertor.fromHTML(dateTimeString)
                        import datetime
                        date = datetime.date(
                            dateTime.year, dateTime.month, dateTime.day
                        )
                        from dm.datetimeconvertor import DateConvertor
                        dateConvertor = DateConvertor()
                        dateString = dateConvertor.toHTML(date)
                        return dateString
                        
                    if conversionName == 'datetime_to_date':
                        conversionMethod = convertDateTimeToDate
                    else:
                        msg = "Unsupported conversion: '%s' in plan step %s" % (
                            conversionName, planStep
                        )
                        raise DataMigrationError(msg)
                    for key in classData.keys():
                        if key == 'metaData':
                            continue
                        domainObjectData = classData[key]
                        attrData = domainObjectData[attrName]
                        #print "    converting %s %s attribute value %s" % (
                        #    className, attrName, attrData
                        #)
                        del(domainObjectData[attrName])
                        attrData = conversionMethod(attrData)
                        if attrData != UndefinedDomainModelValue:
                            domainObjectData[attrName] = attrData
            else:
                msg = "Unsupported plan object: '%s' in plan step %s" % (
                    object, planStep
                )
                raise DataMigrationError(msg)

