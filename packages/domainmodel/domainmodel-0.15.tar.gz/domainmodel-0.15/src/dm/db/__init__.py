"""Model Persistence Data Mapper. Follows 'Data Mapper (165)', [Fowler, 2003]
    
This module provides persistence data mapping services to the domain model.

Responsible for moving values between domain model and persistence objects.

This module works by using domain model meta data objects to construct data
mapper meta data objects which then control SQLObject classes. A database
facade presents methods for defining data mappers, and for creating and
retrieving records from the object relational mapper.

This module avoids collisions of domain model names with database keywords,
and translates between names of the domain model and names of the database.
It also provides various features for making selections from the domain model,
such as after-before intervals for times, and search for text attributes.
The temporal aspects of domain models are also provided by this module, which
has the opportunity to direct persistence of temporal values to the temporal
model, confusing this with neither the domain model or the ORM.

At the moment SQLObject is used as an object-relational mapper to move between
database objects and a relational database management system. We want to add
support for other Object Relational Mappers (such as SQLAlchemy and Elixir).

This module is a Model Persistence Mapper (MPM), and although there are 
similar aspects to both MPMs and ORMs, this module does not build or execute
SQL statements and so cannot be classified as an ORM. Instead, this module
depends on an ORM to move values from the persistence model to the RDBMS.

"""

from dm.exceptions import *

import sqlobject
sqoVer = None
isSqoSupported = False
sqoVers = ['0.7', '0.8', '0.9', '0.10', '0.11', '0.12', '0.13', '0.14', '0.15', '1.0', '1.1', '1.2', '1.3']
if hasattr(sqlobject, 'version'):
    sqoVerSplit = sqlobject.version.split('.')
    if len(sqoVerSplit) >= 2:
        sqoVer = ".".join(sqoVerSplit[0:2])
elif sqlobject.__doc__ != None:
    sqoDocSplit = sqlobject.__doc__.split(' ')
    if len(sqoDocSplit) > 1:
        sqoVerSplit = sqoDocSplit[1].split('.')
        if len(sqoVerSplit) >= 2:
            sqoVer = ".".join(sqoVerSplit[0:2])

if sqoVer in sqoVers:
    isSqoSupported = True
if not isSqoSupported:
    msg = "Imported SQLObject (%s) not supported by dm." % sqoVer
    msg += "\nImported SQLObject package doc: %s" % sqlobject.__doc__
    msg += "Imported SQLObject package path: %s" % sqlobject.__path__
    msg += "\nNeeds latest version of any of: %s." % ", ".join(sqoVers)
    raise ORMError, msg 

from sqlobject import *
from sqlobject.sqlbuilder import func
from sqlobject.converters import sqlrepr
from dm.ioc import *
import dm.dom.meta
import sqlobject.main
from dm.ioc import *
from dm.dictionarywords import *
import datetime
import weakref
import traceback

debug = RequiredFeature('Debug')
logger = RequiredFeature('Logger')
dictionary = RequiredFeature('SystemDictionary')

moddebug = False

class ConnectionFacade(object):
    "Presents database connection."

    dictionary = RequiredFeature('SystemDictionary')

    def __init__(self):
        dbType = dictionary[DB_TYPE]
        dbUser = dictionary[DB_USER]
        dbPass = dictionary[DB_PASS]
        dbHost = dictionary[DB_HOST]
        dbName = dictionary[DB_NAME]
        DB_NAME.test(dbName, dictionary)
        if dictionary.get(DB_URI, None):
            uri = dictionary[DB_URI]
        elif dbType == 'sqlite':
            uri = "sqlite://%s" % dbName
        else:
            uri = "%s://%s:%s@%s/%s" % (dbType, dbUser, dbPass, dbHost, dbName)
        uriParams = {}
        #uriParams['debug'] = '1'
        uriParams['loglevel'] = dictionary[LOG_LEVEL].lower()
        uriParams['logger'] = dictionary[SYSTEM_NAME]
        uriParams['cache'] = '0'
        if dbType == 'postgres':
            uriParams['driver'] = 'psycopg2,psycopg1,psycopg,pygresql'
            #uriParams['autoCommit'] = '0'
        if uriParams:
            uri += "?%s" % "&".join(["=".join(item) for item in uriParams.items()])
        logger.info('Database: Connecting to DB URI: %s' % uri)
        try:
            self.connection = connectionForURI(uri)
            sqlhub.processConnection = self.connection
        except Exception, inst:
            msg = "Database: Could not make a connection using DB URI '%s': %s" % (uri, inst)
            msg += traceback.format_exc()
            logger.critical(msg)
            raise Exception, "Could not make a database connection (see system log for DB URI and exception: %s)." % self.dictionary[LOG_PATH]
        # Todo: Check connection.dbEncoding == 'UTF8'.
    
    def getConnection(self):
        return self.connection
    
    def beginTransaction(self):
        "Begin a new transaction."
        return self.connection.transaction()


class DatabaseFacade(object):
    "Presents database records."
    
    class __singletonDatabaseFacade(object):

        hasMapperClasses = False
        mappers = {}

        def __init__(self):
            "Initialises ConnectionFacade composite."
            self.connection = ConnectionFacade()
        
        def getConnection(self):
            return self.connection.getConnection()
        
        def beginTransaction(self):
            "Begin a transaction."
            return self.connection.beginTransaction()

        def findRecord(self, className, *args, **kwds):
            "Retreive record of domain object."
            record = None
            if moddebug:
                logger.info('Database: Finding %s record in database.' % (className))
            if 'id' in kwds:
                objectId = kwds['id']
                try:
                    record = self.get(className, objectId)
                except SQLObjectNotFound, inst:
                    msg = "Can't find %s record with id %s." \
                        % (className, kwds)
                    raise DbObjectNotFound, msg
            else:
                records = self.findRecords(className, **kwds)
                if hasattr(records, 'count'):
                    try:
                        record = records[0]
                    except:
                        msg = "Can't find %s record with params %s %s." \
                            % (className, args, kwds)
                        raise DbObjectNotFound, msg
                else:
                    record = records
            if record == None:
                msg = "Could't determine %s record with params %s %s." \
                    % (className, args, kwds)
                raise Exception, msg
            return record
        
        def isSelectById(self, kwds):
            if 'id' in kwds:
                return True
            return False

        def isSelectByTimeInterval(self, kwds):
            if '__startsAfter__' in kwds:
                return True
            if '__startsBefore__' in kwds:
                return True
            if '__endsAfter__' in kwds:
                return True
            if '__endsBefore__' in kwds:
                return True
            if '__dateCreatedAfter__' in kwds:
                return True
            if '__dateCreatedOnOrBefore__' in kwds:
                return True
            if '__dateCreatedBefore__' in kwds:
                return True
            if '__lastModifiedAfter__' in kwds:
                return True
            if '__lastModifiedBefore__' in kwds:
                return True
            if '__bookingDateAfter__' in kwds:
                return True
            if '__bookingDateBefore__' in kwds:
                return True
            return False

        def get(self, className, id):
            "Retreive record of domain object."
            try:
                id = int(id)
            except:
                msg = "Couldn't cast %s id to int: '%s'" % (className, id)
                raise KforgeRegistryKeyError, msg
            recordClass = self.getRecordClass(className)
            return recordClass.get(id)  # todo: pass transaction

        def findRecords(self, className, *args, **kwds):
            "Retreive records of domain objects."
            if moddebug:
                logger.info('Database: Finding %s records in database: %s %s' % (className, args, kwds))
            recordClass = self.getRecordClass(className)
            return recordClass.selectByKwds(**kwds)

        def startsWith(self, className, value, attributeName, **kwds):
            recordClass = self.getRecordClass(className)
            kwds['__startsWith__'] = value
            kwds['__startsWithAttribute__'] = attributeName
            return recordClass.selectByKwds(**kwds)

        def search(self, className, userQuery, attributeNames, spaceSplit=True, **kwds):
            recordClass = self.getRecordClass(className)
            kwds['__searchQuery__'] = userQuery
            kwds['__searchQueryAttributes__'] = attributeNames
            kwds['__searchQuerySpaceSplit__'] = spaceSplit
            return recordClass.selectByKwds(**kwds)

        def countRecords(self, className, *args, **kwds):
            "Counts recorded domain objects."
            results = self.listRecords(className, *args, **kwds)
            return results.count()
       
        def listRecords(self, className, *args, **kwds):
            "Returns list of recorded domain objects."
            if kwds:
                records = self.findRecords(className, *args, **kwds)
            else:
                records = self.getRecordClass(className).select()
            if moddebug and debug:
                logger.debug('Database: Listed %s records from database.' % (className))
            return records
       
        def createDomainObject(self, className, __loadedList__=None, *args, **kwds):
            "Create new recorded domain object."
            newRecord = self.createRecord(className, *args, **kwds)
            if moddebug and debug:
                message = "Database: Created new record: %s" % newRecord
                logger.debug(message)
            newObject = newRecord.getDomainObject(loadedList=__loadedList__)
            return newObject
          
        def createRecord(self, className, *args, **kwds):
            "Create record of domain object."
            recordClass = self.getRecordClass(className)
            if not self.connection.dictionary[DB_MIGRATION_IN_PROGRESS]:
                recordClass.assertCreateParams(*args, **kwds)
            if debug:
                message = "Database: Creating new %s record with %s" % (className, kwds)
                logger.debug(message)
            try:
                newRecord = recordClass(*args, **kwds)
            except Exception, inst:
                msg = "Can't create new %s record with params %s: %s"  \
                    % (className, kwds, inst)
                raise KforgeDbError, msg 
            else:
                return newRecord
       
        def getRecordClass(self, className):
            "Returns record class for domain object type name."
            if not className:
                raise Exception, "Can't get record class without class name."
            try:
                mapperClass = self.mappers[className]
            except Exception, inst:
                raise Exception, "Mapper class '%s' not defined in: %s. (%s)" % (
                    className,
                    str(self.mappers),
                    str(inst)
                )
            else:
                return mapperClass

        getRecordClass = classmethod(getRecordClass)
        
        def createMapperClass(self, metaDomainObject):
            baseClass = dm.db.Mapper
            className = metaDomainObject.name
            if className not in self.mappers:
                metaMapper = MetaMapper(metaDomainObject)
                mapperClass = metaMapper.createMapperClass(baseClass)
                self.mappers[className] = mapperClass
                self.checkMapperClassTable(className)
            elif not features.allowReplace:
                raise Exception, "Mapper for '%s' already defined." % className

        createMapperClass = classmethod(createMapperClass)

        def createPersistenceClass(self, metaDomainObject):
            self.createMapperClass(metaDomainObject)

        createPersistenceClass = classmethod(createPersistenceClass)

        def checkMapperClassTable(self, className):
            mapperClass = self.getRecordClass(className)
            try:
                mapperClass.select().count()
            except:
                try:
                    mapperClass.createTable()
                except Exception, inst:
                    msg = "Database: "
                    msg += "Couldn't create table for class '%s': " % className 
                    msg += "Error: %s. " % inst
                    attributes = str(mapperClass.meta.dom.attributeNames)
                    msg += "Attributes are: %s" % attributes
                    logger.error(msg)
                    raise Exception, msg
                else: 
                    mapperClass.select().count()
                    msg = "Database: Added %s table." % (
                        mapperClass.meta.dbName
                    )
                    logger.info(msg)
            return 1
            
        checkMapperClassTable = classmethod(checkMapperClassTable)

        def addPersistenceAttribute(self, className, domAttribute):
            mapperClass = self.getRecordClass(className)
            mapperAttribute = mapperClass.meta.addAttribute(domAttribute)
            sqlAttribute = mapperAttribute.createNamedMapperClassAttribute()
            if sqlAttribute == None:
                return
            # Todo: Perhaps just? addColumn = mapperClass.sqlmeta.addColumn
            if hasattr(mapperClass.sqlmeta, 'addColumn'):
                addColumn = mapperClass.sqlmeta.addColumn
            else:
                raise ORMError, "No 'addColumn' method on SQLObject sqlmeta."
            if hasattr(mapperClass.sqlmeta, 'delColumn'):
                delColumn = mapperClass.sqlmeta.delColumn
            else:
                raise ORMError, "No 'delColumn' method on SQLObject sqlmeta."
            try:    
                addColumn(sqlAttribute, changeSchema=False)
            except:
                if features.allowReplace:
                    return
                raise
            try:
                list(mapperClass.select())
            except:
                delColumn(sqlAttribute, changeSchema=False)
                addColumn(sqlAttribute, changeSchema=True)
                list(mapperClass.select())
                msg = "Database: Added %s field to %s table." % (
                    mapperAttribute.dbName,
                    mapperClass.meta.dbName
                )
                logger.info(msg)

    __instance = __singletonDatabaseFacade()

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)


# todo: take reserved names from there pages:
# http://developer.mimer.com/validator/parser200x/vendor-reserved-words-sql200x.tml

class ReservedNames(object):

    reservedNames = None
    dictionary = RequiredFeature('SystemDictionary')

    sqlKeywordLists = {
        'common': [
            'ABSOLUTE', 'ADD', 'ADMIN', 'AFTER',
            'AND', 'ANY', 'ARE', 'ARRAY', 'AS',
            'ASC', 'ASSERTION', 'AT', 'AUTHORIZATION', 'BEFORE',
            'BEGIN', 'BINARY', 'BIT', 'BLOB', 'BOOLEAN',
            'BOTH', 'BREADTH', 'BY', 'CALL', 'CASCADE',
            'CASCADED', 'CASE', 'CAST', 'CATALOG', 'CHAR',
            'CHARACTER', 'CHECK', 'CLASS', 'CLOB', 'CLOSE',
            'COLLATE', 'COLLATION', 'COLUMN', 'COMMIT', 'COMPLETION',
            'CONNECT', 'CONNECTION', 'CONSTRAINT', 'CONSTRAINTS',
            'CONSTRUCTOR', 'CONTINUE', 'CORRESPONDING', 'CREATE', 'CROSS',
            'CUBE', 'CURRENT', 'CURRENT_DATE', 'CURRENT_PATH', 'CURRENT_ROLE',
            'CURRENT_TIME', 'CURRENT_TIMESTAMP', 'CURRENT_USER', 'CURSOR',
            'CYCLE', 'DATA', 'DATE', 'DAY', 'DEALLOCATE', 'DEC', 'DECIMAL',
            'DECLARE', 'DEFAULT', 'DEFERRABLE', 'DEFERRED', 'DELETE',
            'DEPTH', 'DEREF', 'DESC', 'DESCRIBE', 'DESCRIPTOR', 'DESTROY',
            'DESTRUCTOR', 'DETERMINISTIC', 'DICTIONARY', 'DIAGNOSTICS',
            'DISCONNECT', 'DISTINCT', 'DOMAIN', 'DOUBLE', 'DROP',
            'DYNAMIC', 'EACH', 'ELSE', 'END', 'END_EXEC',
            'EQUALS', 'ESCAPE', 'EVERY', 'EXCEPT', 'EXCEPTION',
            'EXEC', 'EXECUTE', 'EXTERNAL', 'FALSE', 'FETCH',
            'FIRST', 'FLOAT', 'FOR', 'FOREIGN', 'FOUND',
            'FROM', 'FREE', 'FULL', 'FUNCTION', 'GENERAL',
            'GET', 'GLOBAL', 'GO', 'GOTO', 'GRANT',
            'GROUP', 'GROUPING', 'HAVING', 'HOST', 'HOUR',
            'IDENTITY', 'IGNORE', 'IMMEDIATE', 'IN', 'INDICATOR',
            'INITIALIZE', 'INITIALLY', 'INNER', 'INOUT', 'INPUT',
            'INSERT', 'INT', 'INTEGER', 'INTERSECT', 'INTERVAL',
            'INTO', 'IS', 'ISOLATION', 'ITERATE', 'JOIN',
            'LANGUAGE', 'LARGE', 'LAST', 'LATERAL',
            'LEADING', 'LEFT', 'LESS', 'LEVEL', 'LIKE',
            'LIMIT', 'LOCAL', 'LOCALTIME', 'LOCALTIMESTAMP', 'LOCATOR',
            'MAP', 'MATCH', 'MINUTE', 'MODIFIES', 'MODIFY',
            'MODULE', 'MONTH', 'NAMES', 'NATIONAL', 'NATURAL',
            'NCHAR', 'NCLOB', 'NEW', 'NEXT', 'NO',
            'NONE', 'NOT', 'NULL', 'NUMERIC', 'OBJECT',
            'OF', 'OFF', 'OLD', 'ON', 'ONLY',
            'OPEN', 'OPERATION', 'OPTION', 'OR', 'ORDER',
            'ORDINALITY', 'OUT', 'OUTER', 'OUTPUT', 'PAD',
            'PARAMETER', 'PARAMETERS', 'PARTIAL', 'POSTFIX',
            'PRECISION', 'PREFIX', 'PREORDER', 'PREPARE', 'PRESERVE',
            'PRIMARY', 'PRIOR', 'PRIVILEGES', 'PROCEDURE', 'PUBLIC',
            'READ', 'READS', 'REAL', 'RECURSIVE', 'REF',
            'REFERENCES', 'REFERENCING', 'RELATIVE', 'RESTRICT', 'RESULT',
            'RETURN', 'RETURNS', 'REVOKE', 'RIGHT',
            'ROLLBACK', 'ROLLUP', 'ROUTINE', 'ROW', 'ROWS',
            'SAVEPOINT', 'SCHEMA', 'SCROLL', 'SCOPE', 'SEARCH',
            'SECOND', 'SECTION', 'SELECT', 'SEQUENCE',
            'SESSION_USER', 'SET', 'SETS', 'SIZE', 'SMALLINT',
            'SOME', 'SPACE', 'SPECIFIC', 'SPECIFICTYPE', 'SQL',
            'SQLEXCEPTION', 'SQLSTATE', 'SQLWARNING', 'START', 
            'STATEMENT', 'STATIC', 'STRUCTURE', 'SYSTEM_USER', 'TABLE',
            'TEMPORARY', 'TERMINATE', 'THAN', 'THEN', 'TIME',
            'TIMESTAMP', 'TIMEZONE_HOUR', 'TIMEZONE_MINUTE', 'TO', 'TRAILING',
            'TRANSACTION', 'TRANSLATION', 'TREAT', 'TRIGGER', 'TRUE',
            'UNDER', 'UNION', 'UNIQUE', 'UNKNOWN', 'UNNEST',
            'UPDATE', 'USAGE', 'USER', 'USING', 'VALUE',
            'VALUES', 'VARCHAR', 'VARIABLE', 'VARYING', 'VIEW',
            'WHEN', 'WHENEVER', 'WHERE', 'WITH', 'WITHOUT',
            'WORK', 'WRITE', 'YEAR', 'ZONE',
        ],
        'postgres': [
        ],
        'sqlite': [
        ],
        'mysql': [
            'KEY',
        ],
        'default': [
            'ACTION', 'KEY', 'PATH', 'ROLE', 'SESSION', 'STATE',
        ],
    }

    def getReservedNames(self):
        if self.reservedNames == None:
            self.reservedNames = self.sqlKeywordLists['common']
            dbType = dictionary[DB_TYPE]
            if dbType in self.sqlKeywordLists:
                self.reservedNames += self.sqlKeywordLists[dbType]
        return self.reservedNames

    getReservedNames = classmethod(getReservedNames)


class MetaBase(object):
    "Data mapper meta supertype."

    logger     = RequiredFeature('Logger')
    registry   = RequiredFeature('DomainRegistry')
    dictionary = RequiredFeature('SystemDictionary')
    reservedNames = ReservedNames()
    
    def makeSafeTableName(self, naiveName):
        naiveName = self.makeSafeDbName(naiveName)
        style = self.getSQLStyle()
        safeName = style.pythonClassToDBTable(naiveName)
        if moddebug and debug:
            self.logger.debug("Database: Made safe table name: %s" % safeName)
        return safeName
    
    def makeSafeFieldName(self, naiveName):
        naiveName = self.makeSafeDbName(naiveName)
        style = self.getSQLStyle()
        safeName = style.pythonAttrToDBColumn(naiveName)
        if moddebug and debug:
            self.logger.debug("Database: Made safe column name: %s" % safeName)
        return safeName

    def makeSafeDbName(self, name):
        if name.upper() in self.getReservedNames():
            name = 'x' + name.lower()
            if name != self.makeSafeDbName(name):
                raise Exception, "Can't make this name safe: %s" % name
        return name

    def getReservedNames(self):
        return self.reservedNames.getReservedNames()

    def getSQLStyle(self):
        # Version < 0.13.
        if hasattr(SQLObject, 'sqlmeta'):
            if hasattr(SQLObject.sqlmeta, 'style') and SQLObject.sqlmeta.style:
                return SQLObject.sqlmeta.style
        # Version >= 0.13.
        if hasattr(styles, 'defaultStyle') and styles.defaultStyle:
             return styles.defaultStyle
        raise Exception, "Can't find SQLObject's default style object."
            

class MetaMapper(MetaBase):
    "Describes a Mapper with MetaMapperAttributes."

    def __init__(self, metaDomainObject):
        self.dom = metaDomainObject
        self.isUnique = self.dom.isUnique
        self.isCached = self.dom.isCached
        dbName = self.makeSafeTableName(self.dom.dbName or self.dom.name)
        if sqoVer == '0.7':
            self.domName = self.dom.name
            self.dbName = dbName
        else:
            self.domName = dbName
            self.dbName = dbName
        self.attributeDomNames = {}
        self.attributeDbNames = {}
        self.attributes = []
        for domAttr in self.dom.attributes:
            if not domAttr.isList():
                self.addAttribute(domAttr)
        self.sortOnDbName = None
        if self.dom.sortOn:
            self.sortOnDbName = self.makeSafeFieldName(self.dom.sortOn.dbName)
        self.sortAscending = self.dom.sortAscending
        self.sortCaseInsensitive = self.dom.sortCaseInsensitive

    def getAttribute(self, attrName):
        if not attrName in self.attributeDomNames:
            msg = "Attribute '%s' not defined on mapper for class '%s': %s" % (
                attrName, self.domName, self.attributeDomNames.keys()
            )
            raise Exception(msg)
        return self.attributeDomNames[attrName]

    def hasAttribute(self, attrName):
        return attrName in self.attributeDomNames

    def addAttribute(self, metaDomainAttribute):
        metaAttribute = MetaMapperAttribute(metaDomainAttribute)
        self.attributes.append(metaAttribute)
        self.attributeDomNames[metaAttribute.domName] = metaAttribute
        self.attributeDbNames[metaAttribute.dbName] = metaAttribute
        return metaAttribute

    def createMapperClass(self, baseClass):
        mapperAttributes = self.getSQLObjectAttributes()
        mapperAttributes['meta'] = self
        mapperAttributes['map'] = {}
        mapperAttributes['map']['isUnique'] = self.isUnique
        mapperAttributes['map']['isCached'] = self.isCached
        mapperAttributes['_connection'] = DatabaseFacade().getConnection()
        # Set mapper class name from domName, and table attribute from dbName.
        mapper = self.createClass(self.domName, baseClass, mapperAttributes)
        if sqoVer == '0.7' and self.dbName:
            mapper.sqlmeta.table = self.dbName
        if self.isCached:
            mapper.sqlmeta.cacheValues = False
        if self.sortOnDbName:
            defaultOrder = getattr(mapper.q, self.sortOnDbName)
            if self.sortCaseInsensitive:
                defaultOrder = func.lower(defaultOrder)
            if not self.sortAscending:
                defaultOrder = DESC(defaultOrder)
            mapper.sqlmeta.defaultOrder = defaultOrder
        # Todo: Figure indexes in sqlmeta.
        #indexes = self.getSQLObjectIndexes()
        #if indexes:
        #    mapper.indexes = indexes
        return mapper

    def getSQLObjectAttributes(self):
        mapperAttributes = {}
        dbType = dictionary[DB_TYPE]
        for a in self.attributes:
            if a.dom.isTemporal:
                # We don't persist temporal attributes on the parent.
                # Todo: Perhaps we should?
                continue
            mapperClassAttribute = a.createMapperClassAttribute()
            if mapperClassAttribute:
                mapperAttributes[a.dbName] = mapperClassAttribute
            elif a.dom.isImageFile:
                setMethodName = '_set_%s' % a.dbName
                getMethodName = '_get_%s' % a.dbName
                setMethod = a.dom.setFileContent
                getMethod = a.dom.getFileContent
                mapperAttributes[setMethodName] = setMethod
                mapperAttributes[getMethodName] = getMethod
            if a.dom.isIndexed:
                # Indexes are tripping up MySQL.
                if dbType not in ['mysql']:
                    indexName = "%sIndex" % a.dbName
                    index = DatabaseIndex(mapperClassAttribute)
                    mapperAttributes[indexName] = index
        return mapperAttributes

    def getSQLObjectIndexes(self):
        indexes = []
        for mapperAttr in self.attributes:
            if mapperAttr.dom.isIndexed:
                indexes.append(DatabaseIndex(mapperAttr.dbName))
        return indexes

    def createClass(self, name, base, attrs):
        newClass = type(name, (base,), attrs)
        return newClass


class MetaMapperAttribute(MetaBase):
    "Governs the attributes of a Mapper."

    class UndefinedDefault(object):
        pass

    def __init__(self, metaDomainAttribute):
        self.dom = metaDomainAttribute
        self.domName  = self.dom.name
        self.isValueRef = self.dom.isValueRef
        self.isAssociateList = self.dom.isAssociateList
        self.isDomainObjectRef = self.dom.isDomainObjectRef
        if sqoVer in ['0.8', '0.9', '0.10', '0.11', '0.12', '0.13', '0.14', '0.15', '1.0', '1.1', '1.2'] and self.isDomainObjectRef:
            self.typeName = self.makeSafeFieldName(self.dom.typeName)
        else:
            self.typeName = self.dom.typeName
        self.dbName = self.makeSafeFieldName(self.dom.dbName or self.dom.name)
        if self.dom.isValueRef and hasattr(self.dom, 'default'):
            self.default = self.dom.default
        elif self.isDomainObjectRef:
            if hasattr(self.dom, 'default') and not self.dom.default:
                self.default = None
            elif not self.dom.isRequired:
                self.default = None

    def createMapperClassAttribute(self):
        "Creates SQLObject columns for new SQLObject classes."
        if issubclass(self.dom.__class__, dm.dom.meta.String):
            if hasattr(self, 'default'):
                return UnicodeCol(default=self.default)
            else:
                return UnicodeCol()
        elif issubclass(self.dom.__class__, dm.dom.meta.DateTime):
            if hasattr(self, 'default'):
                return DateTimeCol(default=self.default)
            else:
                return DateTimeCol()
        elif issubclass(self.dom.__class__, dm.dom.meta.Boolean):
            if hasattr(self, 'default'):
                return BoolCol(default=self.default)
            else:
                return BoolCol()
        elif issubclass(self.dom.__class__, dm.dom.meta.Integer):
            if hasattr(self, 'default'):
                return IntCol(default=self.default)
            else:
                return IntCol()
        elif issubclass(self.dom.__class__, dm.dom.meta.Float):
            if hasattr(self, 'default'):
                return FloatCol(default=self.default)
            else:
                return FloatCol()
        elif issubclass(self.dom.__class__, dm.dom.meta.BLOB):
            if hasattr(self, 'default'):
                return BLOBCol(default=self.default)
            else:
                return BLOBCol()
        elif issubclass(self.dom.__class__, dm.dom.meta.Pickle):
            if hasattr(self, 'default'):
                return PickleCol(default=self.default)
            else:
                return PickleCol()
        elif issubclass(self.dom.__class__, dm.dom.meta.ImageFile):
            return None
        elif issubclass(self.dom.__class__, dm.dom.meta.DomainObjectRef):
            if hasattr(self, 'default'):
                return ForeignKey(self.typeName, default=self.default)
            else:
                return ForeignKey(self.typeName)
        else:
            raise Exception, "Unknown domain attribute: %s" % self.dom

    def createNamedMapperClassAttribute(self):
        "Creates SQLObject columns for existing SQLObject classes."
        if issubclass(self.dom.__class__, dm.dom.meta.String):
            if hasattr(self, 'default'):
                return UnicodeCol(name=self.dbName, default=self.default)
            else:
                return UnicodeCol(name=self.dbName)
        elif issubclass(self.dom.__class__, dm.dom.meta.DateTime):
            if hasattr(self, 'default'):
                return DateTimeCol(default=self.default)
            else:
                return DateTimeCol()
        elif issubclass(self.dom.__class__, dm.dom.meta.Boolean):
            if hasattr(self, 'default'):
                return BoolCol(default=self.default)
            else:
                return BoolCol()
        elif issubclass(self.dom.__class__, dm.dom.meta.Integer):
            if hasattr(self, 'default'):
                return IntCol(default=self.default)
            else:
                return IntCol()
        elif issubclass(self.dom.__class__, dm.dom.meta.Float):
            if hasattr(self, 'default'):
                return FloatCol(default=self.default)
            else:
                return FloatCol()
        elif issubclass(self.dom.__class__, dm.dom.meta.BLOB):
            if hasattr(self, 'default'):
                return BLOBCol(default=self.default)
            else:
                return BLOBCol()
        elif issubclass(self.dom.__class__, dm.dom.meta.Pickle):
            if hasattr(self, 'default'):
                return PickleCol(default=self.default)
            else:
                return PickleCol()
        elif issubclass(self.dom.__class__, dm.dom.meta.ImageFile):
            return None
        elif issubclass(self.dom.__class__, dm.dom.meta.DomainObjectRef):
            if sqoVer in ['0.8', '0.9', '0.10', '0.11', '0.12', '0.13', '0.14', '0.15', '1.0', '1.1', '1.2']:
                dbName = self.dbName
            elif sqoVer in ['0.7']:
                dbName = self.dbName + 'ID'
            else:
                raise ORMError, "No support for SQLObject version %s." % sqoVer
            if hasattr(self, 'default'):
                return KeyCol(foreignKey=self.typeName, name=dbName,
                    default=self.default)
            else:
                return KeyCol(foreignKey=self.typeName, name=dbName)
        else:
            raise Exception, "Unknown domain attribute: %s" % self.dom


class Mapper(SQLObject):
    "Maps values between DomainObject and a database."

    class sqlmeta:
        cacheValues = False
        lazyUpdate = True

    domainObject = None

    def __init__(self, **kwds):
        self.coerceKwds(kwds)
        super(Mapper, self).__init__(**kwds)

    def isUnique(self):
        if 'isUnique' in self.map:
            return self.map['isUnique']
        else:
            return False

    isUnique = classmethod(isUnique)
    
    def isCached(self):
        if 'isCached' in self.map:
            isCached = self.map['isCached']
        else:
            isCached = False
        return isCached

    isCached = classmethod(isCached)
    
    def assertCreateParams(self, *args, **kwds):
        if self.isUnique():
            self.assertUnique(*args, **kwds)
        
    assertCreateParams = classmethod(assertCreateParams)
    
    def assertUnique(self, *args, **kwds):
        "Raises exception unless no record exists with given parameters."
        if not kwds:
            return
        if moddebug and debug:
            msg = "Database: Asserting kwds are unique: %s" % kwds
            logger.debug(msg)
        if self.selectByKwds(**kwds).count():
            msg = "'%s' record already exists for: %s" % (self.__name__, kwds)
            logger.info(msg)
            raise KforgeDbError, msg

    assertUnique = classmethod(assertUnique)
    
    def getDomainObject(self, loadedList=None):
        "Method to 'Lazy Load' mapped domain object."
        if moddebug:
            msg = "Database: Getting %s #%s domain object from record." % (self.getClassName(), self.id)
            logger.info(msg)
        if loadedList == None:
            loadedList = set()
        #logger.info("Loaded list: %s" % loadedList)
        if not self.domainObject or not self.domainObject():
            if moddebug:
                msg = "Database: - no object, so recreating domain object."
                logger.info(msg)
            #print "Domain object (1): %s" % self.domainObject
            domainObject = self.getDomainClass()()
            domainObject.record = self
            self.domainObject = weakref.ref(domainObject)
            #print "Domain object (2): %s" % self.domainObject
            self.loadDomainObject(loadedList, loadMapper=False)
        else:
            if moddebug:
                msg = "Database: - yes object, but checking whether to reload values."
                logger.info(msg)
            if not self.isCached():
                if not self.domainObject() in loadedList:
                    if moddebug:
                        msg = "Database: --- not in 'just loaded' list, so reloading values."
                        logger.info(msg)
                    self.loadDomainObject(loadedList)
                else:
                    if moddebug:
                        msg = "Database: --- in 'just loaded' list, so skipping reload."
                        logger.info(msg)
            else: 
                if moddebug:
                    msg = "Database: --- cached type, so skipping reload."
                    logger.info(msg)
        return self.domainObject()

#    def createDomainObject(self):
#        "Reinstantiates pre-recorded domain object."
       
    def getClassName(self):
        return self.__class__.__name__
        
    def getDomainClassName(self):
        return self.meta.dom.name
        
    getDomainClassName = classmethod(getDomainClassName)

    def getDomainClass(self):
        "Returns mapper's synonymous domain model class."
        registry = RequiredFeature('DomainRegistry')
        return registry.getDomainClass(self.getDomainClassName())

    getDomainClass = classmethod(getDomainClass)

    def loadDomainObject(self, loadedList, loadMapper=True):
        loadedList.add(self.domainObject())
        if loadMapper:
            self.loadMapperAttributesFromRecord()
        self.loadDomainObjectFromMapperAttributes(loadedList)

    def loadMapperAttributesFromRecord(self):
        "Maps record values to mapper attributes."
        if moddebug:
            message = "Database: Pulling %s #%s attributes from database." % (self.__class__.__name__, self.id)
            logger.info(message)
        self.sync()

    def loadDomainObjectFromMapperAttributes(self, loadedList):
        if moddebug:
            msg = "Database: - loading %s #%s from mapper attributes..." % (
                self.getClassName(),
                self.id
            )
            logger.info(msg)
        currentVersion = None
        if not self.domainObject():
            raise Exception("Missing domain object reference on record.")
        #print "Domain object (3): %s" % self.domainObject
        if self.domainObject().meta.isTemporal:
            currentVersion = self.domainObject().temporalHistory.getCurrent()
        self.domainObject().id = self.id
        for metaAttr in self.meta.attributes:
            dbName = metaAttr.dbName
            domName = metaAttr.domName
            if False and moddebug:
                msg = "Database: - loading %s %s attribute." % (
                    self.getClassName(), domName,
                )
                logger.info(msg)
            if domName == 'parent' and metaAttr.isDomainObjectRef:
                # Continue if it's already loaded....
                if self.parent and self.parent.domainObject and self.parent.domainObject():
                    mapperValue = self.parent.domainObject()
                    self.domainObject().parent = mapperValue
                    continue
            if metaAttr.dom.isTemporal:
                # We don't persist temporal attributes on the parent.
                #     - we need to look in the temporal model.
                if self.domainObject().meta.isTemporal:
                    if currentVersion:
                        mappedValue = getattr(currentVersion, domName)
                    else:
                        mappedValue = metaAttr.dom.createInitialValue(
                            self.domainObject()
                        )
                else:
                    # Temporal property histories are virtual ATM.
                    p = metaAttr.dom.createTemporalCollection(self.domainObject())
                    currentPropertyVersion = p.findFirstDomainObject(loadedList)
                    if currentPropertyVersion:
                        mappedValue = currentPropertyVersion.recordedValue
                    else:
                        mappedValue = metaAttr.dom.createInitialValue(
                            self.domainObject()
                        )
            elif metaAttr.isDomainObjectRef:
                mapper = getattr(self, dbName)
                if mapper:
                    mappedValue = mapper.getDomainObject(loadedList)
                else:
                    mappedValue = None
            elif metaAttr.dom.isValueRef and metaAttr.dom.isDateTime:
                mappedValue = getattr(self, dbName)
                if (mappedValue != None) and (mappedValue != ''):
                    # Coerse to datetime.
                    # todo: stabilise SQLObject's date-time choice
                    mappedValue = datetime.datetime(
                        mappedValue.year,
                        mappedValue.month,
                        mappedValue.day,
                        mappedValue.hour,
                        mappedValue.minute,
                        mappedValue.second,
                    )
            elif metaAttr.dom.isImageFile:
                mappedValue = getattr(self, dbName)
            else:
                mappedValue = getattr(self, dbName)
                # Set empty strings (remedy for bug with SQLite and Python2.7).
                if mappedValue == None:
                    if metaAttr.dom.isString:
                        mappedValue = ''
            setattr(self.domainObject(), domName, mappedValue)
        if moddebug:
            msg = "Database: Done loading %s #%s from mapper attributes." % (
                self.getClassName(),
                self.id
            )
            logger.info(msg)

    def saveDomainObject(self):
        "Sets attributes of record object from domain object."
        isChanged = False
        isChangedTemporal = False
        currentVersion = None
        if self.domainObject().meta.isTemporal:
            currentVersion = self.domainObject().temporalHistory.getCurrent()
            if not currentVersion:
                isChangedTemporal = True
            if not isChangedTemporal:
                for metaAttr in self.domainObject().meta.attributes:
                    if metaAttr.isTemporal:
                        if metaAttr.isAssociateList:
                            recordedRegister = getattr(currentVersion, metaAttr.name)
                            recordedList = recordedRegister.getObjectList()
                            actualRegister = getattr(self.domainObject(), metaAttr.name)
                            actualList = actualRegister.getObjectList()
                            recordedLen = len(recordedList)
                            actualLen = len(actualList)
                            #print "Checking association list values for changes..."
                            #print "Recorded: %s, actual: %s)...." % (recordedLen, actualLen)
                            if recordedLen == actualLen:
                                for i in recordedList:
                                    if i.recordedValue not in actualList:
                                        #print "Missing item: %s" % i.recordedValue
                                        isChangedTemporal = True
                                        break
                                    #else:
                                    #    print "Found item in record: %s" % i.recordedValue
                                if isChangedTemporal:
                                    break
                            else:
                                #print "Length mismatch!"
                                isChangedTemporal = True
                                break
                        else:
                            domName = metaAttr.name
                            recordedValue = getattr(currentVersion, domName)
                            actualValue = getattr(self.domainObject(), domName)
                            if actualValue != recordedValue:
                                isChangedTemporal = True
                                break
            if isChangedTemporal:
                #print "Is changed!!!!!!! Creating new current version of associate list."
                loadedList = set([self.domainObject()])
                history = self.domainObject().temporalHistory
                currentVersion = history.create(loadedList=loadedList)

                for metaAttr in self.domainObject().meta.attributes:
                    if metaAttr.isTemporal and metaAttr.isAssociateList:
                        isListChanged = False
                        recordedRegister = getattr(currentVersion, metaAttr.name)
                        recordedList = recordedRegister.getObjectList()
                        actualRegister = getattr(self.domainObject(), metaAttr.name)
                        actualList = actualRegister.getObjectList()
                        recordedLen = len(recordedList)
                        actualLen = len(actualList)
                        #print "Checking association list values for changes..."
                        #print "Recorded: %s, actual: %s)...." % (recordedLen, actualLen)
                        if recordedLen == actualLen:
                            for i in recordedList:
                                if i.recordedValue not in actualList:
                                    #print "Missing item: %s" % i.recordedValue
                                    isListChanged = True
                                    break
                                #else:
                                #    print "Found item in record: %s" % i.recordedValue
                        else:
                            #print "Length mismatch!"
                            isListChanged = True
    
                        if isListChanged:
                            #print "List is changed...."
                            for item in actualRegister:
                                #print "Adding list item to temporal record: %s" % item
                                key = actualRegister.getRegisterKey(item)
                                try:
                                    listItem = recordedRegister.create(
                                        recordedValue=item,
                                        recordedKey=key
                                    )
                                    #print "Created: %s" % listItem

                                except TypeError, inst:
                                    msg = "Couldn't add item %s with key %s to temporal associate list register %s: %s" % (item, key, recordedRegister, inst)
                                    #print msg
                                    raise Exception, msg
                                #print "Recorded register now: %s" % [i for i in recordedRegister]

        for metaAttr in self.meta.attributes:
            domValue = getattr(self.domainObject(), metaAttr.domName)
            # Check value with most recent record.
            if metaAttr.dom.isTemporal:
                # We don't persist temporal attributes on the parent.
                #     - we need to look in the temporal model.
                if self.domainObject().meta.isTemporal:
                    setattr(currentVersion, metaAttr.domName, domValue)
                else:
                    # Temporal property histories are virtual ATM.
                    p = metaAttr.dom.createTemporalCollection(self.domainObject())
                    loadedList = set([self.domainObject()])
                    current = p.findFirstDomainObject(loadedList=loadedList)
                    if current == None or current.recordedValue != domValue:
                        p.create(recordedValue=domValue, loadedList=loadedList)
            elif metaAttr.isDomainObjectRef:
                domainObject = domValue
                if domainObject and hasattr(domainObject, 'record'):
                    domRecord = domainObject.record
                else:
                    domRecord = None
                dbRecord = getattr(self, metaAttr.dbName)
                if domRecord != dbRecord:
                    setattr(self, metaAttr.dbName, domRecord)
                    isChanged = True
            elif metaAttr.isValueRef:
                dbValue = getattr(self, metaAttr.dbName)
                if domValue != dbValue:
                    setattr(self, metaAttr.dbName, domValue)
                    isChanged = True

        if isChangedTemporal:
            currentVersion.save()
        if isChanged:
            if moddebug:
                message = "Database: Saving %s #%s values to database." % (self.__class__.__name__, self.id)
                logger.info(message)
            try:
                # Call SQLObject.
                self.syncUpdate()
            except Exception, inst:
                message = "Database: Failed to save database with %s #%s values." % (
                    self.meta.domName, self.id
                )
                logger.error(message)
                raise
            if moddebug:
                logger.info("Database: DONE")

    def coerceKwds(self, kwds):
        "Converting keyword names to database names."
        if 'id' in kwds:
            kwds['id'] = self.sqlIdValue(kwds['id'])
        for metaAttr in self.meta.attributes:
            if metaAttr.domName in kwds:
                if metaAttr.isDomainObjectRef:
                    mapper = kwds[metaAttr.domName]
                    del kwds[metaAttr.domName]
                    if sqoVer in ['0.10', '0.11', '0.12', '0.13', '0.14', '0.15', '1.0', '1.1', '1.2']:
                        dbName = metaAttr.dbName
                    elif sqoVer in ['0.7', '0.8', '0.9']:
                        dbName = metaAttr.dbName + 'ID'
                    if mapper:
                        if sqoVer in ['0.10', '0.11', '0.12', '0.13', '0.14', '0.15', '1.0', '1.1', '1.2']:
                            kwds[dbName] = mapper
                        elif sqoVer in ['0.7', '0.8', '0.9']:
                            kwds[dbName] = mapper.id
                    else:
                        kwds[dbName] = None
                else:
                    value = kwds[metaAttr.domName]
                    del kwds[metaAttr.domName]
                    kwds[metaAttr.dbName] = value

    coerceKwds = classmethod(coerceKwds)

    def selectByKwds(self, **kwds):
        self.coerceKwds(kwds)
        # The kwds may contain 'special' parameters to be interpretted.
        # Try to make SQL conditions from 'special' parameters.
        # If there are such conditions from 'special' parameters,
        # then make the normal kwds into SQL conditions.
        # Otherwise just do selectBy().
        sqlConditions = []
        # Pick off 'special' accessedBy kwds.
        #if 'name' in kwds and kwds['name'] == 'annakarenina':
        #    raise Exception, str(kwds)
        if '__accessedBy__' in kwds:
            accessedBy = kwds.pop('__accessedBy__')
            if not self.meta.hasAttribute('isHidden'):
                pass
            elif not self.meta.hasAttribute('readableBy'):
                pass
            else:
                sqlCondition = self.sqlAccessedBy(accessedBy)
                sqlConditions.append(sqlCondition)
        # Pick off 'special' search kwds.
        if '__searchQuery__' in kwds and '__searchQueryAttributes__' in kwds:
            sqlCondition = self.sqlSearch(
                kwds.pop('__searchQuery__'),
                kwds.pop('__searchQueryAttributes__'),
                kwds.pop('__searchQuerySpaceSplit__', True),
            )
            sqlConditions.append(sqlCondition)
        # Pick off 'special' startsWith kwds.
        if '__startsWith__' in kwds and '__startsWithAttribute__' in kwds:
            sqlCondition = self.sqlStartsWith(
                kwds.pop('__startsWithAttribute__'),
                kwds.pop('__startsWith__'),
            )
            sqlConditions.append(sqlCondition)
        # Pick off 'special' time interval kwds.
        for (name, value) in kwds.items():
            sqlSafeValue = self.sqlRepr(value)
            sqlCondition = self.sqlTimeInterval(name, sqlSafeValue)
            if sqlCondition:
                kwds.pop(name) 
                sqlConditions.append(sqlCondition)
        if sqlConditions:
            # Pick up remaining kwds.
            for (name, value) in kwds.items():
                sqlConditions.append(self.sqlEquals(name, value))
            # Select by condition.
            sqlCondition = "(%s)" % self.sqlAnd(sqlConditions)
            logger.debug("Database: Selecting '%s' records by SQL condition: %s" % (self.__name__, sqlCondition))
            selection = self.selectBySqlCondition(sqlCondition)
        else:
            # Default SQLObject selectBy() method.
            logger.debug("Database: Selecting '%s' records by kwds: %s" % (self.__name__, kwds))
            selection = self.selectBy(**kwds)
        logger.debug("Database: Selected %s '%s' records." % (selection.count(), self.__name__))
        return selection

    selectByKwds = classmethod(selectByKwds)

    def selectBySqlCondition(self, sqlCondition):
        # Todo: Write test to check special characters are handled OK.
        logger.debug("Database: Selecting records by SQL condition: %s" % sqlCondition)
        if type(sqlCondition) == unicode:
            sqlCondition = sqlCondition.encode('utf8')
        try:
            selection = self.select(sqlCondition)
        except Exception, inst:
            msg = "Couldn't execute select() with %s: %s" % (sqlCondition, inst)
            raise KforgeDbError, msg
        if moddebug:
            logger.info("Database: DONE")
        return selection

    selectBySqlCondition = classmethod(selectBySqlCondition)

    def getAttributeDbName(self, domName):
        return self.meta.getAttribute(domName).dbName

    getAttributeDbName = classmethod(getAttributeDbName)

    def sqlRepr(self, value):
        return sqlrepr(value, dictionary[DB_TYPE])

    sqlRepr = classmethod(sqlRepr)

    def dropQuotes(self, value):
        if value[0] == "'" and value[-1] == "'":
            return value[1:-1]
        else:
            raise Exception, "Not single quoted: %s" % value

    dropQuotes = classmethod(dropQuotes)

    def makeSqlName(self, name):
        if name[-2:] == 'ID':
            name = name[:-2] + '_id'
        return name

    makeSqlName = classmethod(makeSqlName)
    
    def sqlEquals(self, name, value):
        if self.meta.attributeDbNames[name].isDomainObjectRef:
            name += '_id'
        sqlSafeName = self.makeSqlName(name)
        sqlSafeValue = self.sqlRepr(value)
        if sqlSafeValue.upper() == 'NULL':
            sqlCondition = "%s IS %s" % (sqlSafeName, sqlSafeValue)
        else:
            sqlCondition = "%s = %s" % (sqlSafeName, sqlSafeValue)
        return sqlCondition

    sqlEquals = classmethod(sqlEquals)

    def sqlAnd(self, sqlConditions):
        return "(%s)" % ") AND (".join(sqlConditions)

    sqlAnd = classmethod(sqlAnd)

    def sqlOr(self, sqlConditions):
        return "(%s)" % ") OR (".join(sqlConditions)

    sqlOr = classmethod(sqlOr)

    def sqlTimeInterval(self, name, sqlSafeValue):
        sqlCondition = None
        if name == '__startsBefore__':
            sqlSafeName = self.makeSqlName('starts')
            sqlCondition = "%s < %s" % (sqlSafeName, sqlSafeValue)
        elif name == '__startsAfter__':
            sqlSafeName = self.makeSqlName('starts')
            sqlCondition = "%s > %s" % (sqlSafeName, sqlSafeValue)
        elif name == '__endsBefore__':
            sqlSafeName = self.makeSqlName('ends')
            sqlCondition = "%s < %s" % (sqlSafeName, sqlSafeValue)
        elif name == '__endsAfter__':
            sqlSafeName = self.makeSqlName('ends')
            sqlCondition = "%s > %s" % (sqlSafeName, sqlSafeValue)
        elif name == '__dateCreatedBefore__':
            sqlSafeName = self.makeSqlName('date_created')
            sqlCondition = "%s < %s" % (sqlSafeName, sqlSafeValue)
        elif name == '__dateCreatedOnOrBefore__':
            sqlSafeName = self.makeSqlName('date_created')
            sqlCondition = "%s <= %s" % (sqlSafeName, sqlSafeValue)
        elif name == '__dateCreatedAfter__':
            sqlSafeName = self.makeSqlName('date_created')
            sqlCondition = "%s > %s" % (sqlSafeName, sqlSafeValue)
        elif name == '__lastModifiedBefore__':
            sqlSafeName = self.makeSqlName('last_modified')
            sqlCondition = "%s < %s" % (sqlSafeName, sqlSafeValue)
        elif name == '__lastModifiedAfter__':
            sqlSafeName = self.makeSqlName('last_modified')
            sqlCondition = "%s > %s" % (sqlSafeName, sqlSafeValue)
        elif name == '__bookingDateBefore__':
            sqlSafeName = self.makeSqlName('booking_date')
            sqlCondition = "%s < %s" % (sqlSafeName, sqlSafeValue)
        elif name == '__bookingDateAfter__':
            sqlSafeName = self.makeSqlName('booking_date')
            sqlCondition = "%s > %s" % (sqlSafeName, sqlSafeValue)
        return sqlCondition

    sqlTimeInterval = classmethod(sqlTimeInterval)
    
    def sqlAccessedBy(self, accessedBy):
        sqlNotHidden = self.sqlEquals(self.getAttributeDbName('isHidden'), False)
        if accessedBy == None:
            accessedBy = ''
        sqlReadableBy = self.sqlSearchTerm('readableBy', ':%s:' % accessedBy)
        return self.sqlOr([sqlNotHidden, sqlReadableBy])
        
    sqlAccessedBy = classmethod(sqlAccessedBy)

    def sqlSearch(self, userQuery, attributeNames, spaceSplit):
        queryTerms = userQuery.split(' ') if spaceSplit else [userQuery]
        sqlConditions = []
        for queryTerm in queryTerms:
            if not queryTerm:
                continue
            if ':' in queryTerm:
                # Attribute specific term.
                name, value = queryTerm.split(':', 1)
                if name and value and name in attributeNames:
                    sqlCondition = self.sqlSearchTerm(name, value)
                    sqlConditions.append(sqlCondition)
            else:
                # Non-attribute specific term.
                subConditions = []
                for name in attributeNames:
                    value = queryTerm
                    subCondition = self.sqlSearchTerm(name, value)
                    subConditions.append(subCondition)
                if subConditions:
                    sqlCondition = self.sqlOr(subConditions)
                    sqlConditions.append(sqlCondition)
        if not len(sqlConditions):
            sqlConditions.append('id=NULL')
        #raise Exception, self.sqlAnd(sqlConditions)
        return self.sqlAnd(sqlConditions)
        
    sqlSearch = classmethod(sqlSearch)

    def sqlSearchTerm(self, attributeName, value):
        dbName = self.getAttributeDbName(attributeName)
        sqlSafeName = self.makeSqlName(dbName)
        sqlSafeValue = self.dropQuotes(self.sqlRepr(value))
        return "UPPER(%s) LIKE UPPER('%%%s%%')" % (sqlSafeName, sqlSafeValue)

    sqlSearchTerm = classmethod(sqlSearchTerm)

    def sqlStartsWith(self, attributeName, value):
        dbName = self.getAttributeDbName(attributeName)
        sqlSafeName = self.makeSqlName(dbName)
        sqlSafeValue = self.dropQuotes(self.sqlRepr(value))
        return "UPPER(%s) LIKE UPPER('%s%%')" % (sqlSafeName, sqlSafeValue)

    sqlStartsWith = classmethod(sqlStartsWith)

    def sqlIdValue(self, value):
        try:
            value = int(value)
        except:
            className = self.getDomainClassName()
            msg = "Couldn't cast %s id to int: '%s'" % (className, value)
            raise KforgeRegistryKeyError, msg  # Django templates to carry on.
        return value
   
    sqlIdValue = classmethod(sqlIdValue)


