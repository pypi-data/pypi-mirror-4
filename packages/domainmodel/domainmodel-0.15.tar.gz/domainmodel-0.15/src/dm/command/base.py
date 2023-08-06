from dm.ioc import *
from dm.exceptions import *
import sys
import traceback

debug = RequiredFeature('Debug')

class Command(object):
    """
    Command supertype.
    'Service Layer' [Fowler, 2003]
    'Command (233)' [GoF, 1995]
    """

    registry   = RequiredFeature('DomainRegistry')
    dictionary = RequiredFeature('SystemDictionary')
    logger     = RequiredFeature('Logger')
    exceptionClass = KforgeCommandError

    def __init__(self, isTransaction=False, **kwds):
        self.isTransaction = isTransaction
        if self.isTransaction:
            self.transaction = self.registry.database.beginTransaction()
        self.kwds = kwds
        self.logger = RequiredFeature('Logger')

    def execute(self):
        if debug:
            #message = "Command: "+ self.getCommandName() +" "+ str(self.kwds)
            message = "Executed command: "+ self.getCommandName()
            self.logger.debug(message)

    def getCommandName(self):
        return self.__class__.__name__

    def commitSuccess(self):
        "Commit any transaction."
        if self.isTransaction:
            self.transaction.commit()

    def raiseError(self, message, inst=None):
        "Raise command error exception."
        if self.isTransaction:
            self.transaction.rollback()
        if debug:
            self.logger.debug("Command error: " + message)
        if inst and hasattr(sys, 'last_traceback') and sys.last_traceback:
            tbStr = traceback.format_tb(sys.last_traceback)
            message += '\n\n' + tbStr + '\n\n'
        exceptionClass = self.exceptionClass
        raise exceptionClass(message)


class MacroCommand(Command):
    "Execute a sequence of commands."

    def execute(self):
        "Make them so."
        commands = self.getCommands()
        for command in commands:
            command.execute()

    def getCommands(self):
        "List of commands."
        return []


class DomainObjectCommand(Command):

    # todo: rename: objectId -> domainObjectKey

    def __init__(self, typeName=None, objectId=None, objectKwds={}, **kwds):
        super(DomainObjectCommand, self).__init__(**kwds)
        if not typeName:
            raise KforgeCommandError("No typeName parameter for %s" % str(self))
        self.typeName = typeName
        self.objectId = objectId
        self.objectKwds = objectKwds

    def assertDomainClassRegistered(self):
        if not self.registry.isDomainClassRegistered(self.typeName):
            message = "Domain class not registered: %s" % self.typeName
            self.raiseError(message)

    def getDomainClass(self):
        return self.registry.getDomainClass(self.typeName)
        
    def createRegister(self):
        self.assertDomainClassRegistered()
        objectClass = self.getDomainClass()
        return objectClass.principalRegister or objectClass.createRegister()

# todo: rename following <Action>DomainObject (e.g. "Create [a] domain object!")

class DomainObjectList(DomainObjectCommand):

    def __init__(self, userQuery='', startsWith='', startsWithAttributeName='', **kwds):
        super(DomainObjectList, self).__init__(**kwds)
        self.userQuery= userQuery
        self.startsWith = startsWith
        self.startsWithAttributeName = startsWithAttributeName

    def execute(self):
        super(DomainObjectList, self).execute()
        domainObjectRegister = self.createRegister()
        if self.startsWith:
            selectedDomainObjects = domainObjectRegister.startsWith(
                value=self.startsWith,
                attributeName=self.startsWithAttributeName
            )
            self.results = [p for p in selectedDomainObjects]
        elif self.userQuery:
            selectedDomainObjects = domainObjectRegister.search(
                userQuery=self.userQuery
            )
            self.results = [p for p in selectedDomainObjects]
        else:
            self.results = [p for p in domainObjectRegister]


class DomainObjectCreate(DomainObjectCommand):

    def execute(self):
        register = self.createRegister()
        objectKwds = self.objectKwds
        try:
            if self.objectId:
                self.object = register.create(self.objectId, **objectKwds)
            else:
                self.object = register.create(**objectKwds)
        #except KforgeDomError, inst:
        #except Exception, inst:
        except DomainModelApplicationError, inst:
            message = "Can't create domain object: %s " % str(inst)
            trace = traceback.format_exc()
            self.logger.error(message + trace)
            self.raiseError(message, inst)


class DomainObjectRead(DomainObjectCommand):

    def execute(self):
        register = self.createRegister()
        objectKwds = self.objectKwds
        try:
            if self.objectId:
                self.object = register.read(self.objectId, **objectKwds)
            else:
                self.object = register.read(**objectKwds)
        except KforgeError, inst:
            self.raiseError(str(inst))
 
 
# todo:
class DomainObjectUpdate(DomainObjectCommand):
    pass


# todo:
class DomainObjectDelete(DomainObjectCommand):
    pass

