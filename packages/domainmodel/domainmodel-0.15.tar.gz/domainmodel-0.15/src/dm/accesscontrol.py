from dm.ioc import RequiredFeature
from dm.strategy import MakeProtectedNames, FindProtectionObjects
from dm.dictionarywords import MEMOS_LIMIT, MEMOS_EXPIRE, MEMOS_ENABLED
from dm.dictionarywords import VISITOR_NAME
from dm.exceptions import *
import dm.times
import traceback
moddebug = False


class AttrDict(dict):
    """
    Dictionary where members can be accessed as attributes
    """
    def __init__(self, **kwds):
        dict.__init__(self, kwds)

    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError(item)

    def __setattr__(self, item, value):
        if self.__dict__.has_key(item):
            dict.__setattr__(self, item, value)
        else:
            self.__setitem__(item, value)


class AccessControlRequest(AttrDict):

    def __init__(self, person, actionName, protectedObject, **kwds):
        super(AccessControlRequest, self).__init__(person=person,
            actionName=actionName, protectedObject=protectedObject, **kwds)

    def validate(self):
        if not self.person:
            raise AccessIsForbidden("missing person")
        if not self.actionName:
            raise AccessIsForbidden("missing action")
        if not self.protectedObject:
            raise AccessIsForbidden("missing protected object")

    def summarise(self):
        summaryInfo = {
            'person': self.summarisePerson(),
            'action': self.actionName.lower(),
            'protectedObject': self.summariseProtectedObject(),
        }
        return "%(person)s to %(action)s %(protectedObject)s" % summaryInfo

    def summarisePerson(self):
        return self.person and self.person.name or 'None'

    def summariseProtectedObject(self):
        if type(self.protectedObject) == type:
            return "%s objects" % self.protectedObject.__name__
        elif hasattr(self.protectedObject, 'getRegisterKeyValue'):
            return "%s %s" % (
                type(self.protectedObject).__name__,
                self.protectedObject.getRegisterKeyValue(),
            )
        else:
            return repr(self.protectedObject)
    

class AccessControlResult(object):

    logger = RequiredFeature('Logger')

    def __init__(self, request):
        self.request = request
        self.permissions = None
        self.protectionObjects = None

    def isPermissionSet(self, permissions, polarity, msg):
        isSet = False
        for permission in self.getPermissions():
            if permission in permissions:
                isSet = True
        if isSet:
            if moddebug:
                msg = "access %s by %s" % (polarity, msg)
                self.logger.info("AccessController: %s" % msg)
            return True
        else:
            if moddebug:
                msg = "access not %s by %s" % (polarity, msg)
                self.logger.info("AccessController: %s" % msg)
            return False

    def getPermissions(self):
        if self.permissions == None:
            self.permissions = []
            for protectionObject in self.getProtectionObjects():
                try:
                    permission = protectionObject.permissions[self.action]
                    self.permissions.append(permission)
                except KforgeRegistryKeyError:
                    msg = "No permission '%s' on protection object '%s'." % (
                        self.action.name, protectionObject.name)
                    self.logger.warn("AccessController: %s" % msg)
        return self.permissions

    def getProtectionObjects(self):
        if self.protectionObjects == None:
            findCmd = FindProtectionObjects(self.request.protectedObject)
            self.protectionObjects = findCmd.find()
        return self.protectionObjects


class BaseAccessController(object):
    """Template class for controlling access to protected objects.

    Client objects will call the isAccessAuthorised() method with keywords:
    
        canUpdateAccount = accessController.isAccessAuthorised(
            person=john,
            actionName='Update',
            protectedObject=account
        )
    
    This method effectively implements "bool(not bars and grants)" for the
    union of all pertaining bars and the union of all pertaining grants.

    It's critical to check all the ways access could be barred, before
    checking all the ways access could be authorised. It doesn't matter which
    bar triggers a denial or which grant causes an authorisation, but it does
    matter that bars trigger denials before grants trigger authorisations.

    Access is denied by raising the AccessIsForbidden exception in any of the
    methods called by isAccessAuthorised(). They are request.validate(),
    assertAccessNotBarred(), and assertAccessNotAuthorised(). Likewise, access
    is authorised by raising the AccessIsAuthorised exception within those
    methods. By default, access is not authorised.

    Any access controller derived from this class can involve other domain
    objects having grants or bars in their access control scheme by extending
    the assertAccessNotBarred() or assertAccessNotAuthorised() methods, and 
    checking the involved object by calling the assertRoleNotBarred(object) or
    assertRoleNotAuthorised(object) methods.
    """
    
    dictionary = RequiredFeature('SystemDictionary')
    registry = RequiredFeature('DomainRegistry')
    logger = RequiredFeature('Logger')
    debug = RequiredFeature('Debug')

    def __init__(self):
        self.visitor = None
        self.memosEnabled = bool(self.dictionary[self.dictionary.words.MEMOS_ENABLED])
        self.memosExpire = int(self.dictionary[self.dictionary.words.MEMOS_EXPIRE])
        self.memosLimit = int(self.dictionary[self.dictionary.words.MEMOS_LIMIT])
        self.usingMemos = self.memosEnabled and (self.memosLimit > 0) and (self.memosExpire > 0)
        self.memosCache = {}
        self.memosFifo = []
        self.memosAge = {}
        self.logger.info("AccessController: Initialised %s memoisation (settings: enabled = %s, expire = %s, limit = %s)." % (self.usingMemos and "with" or "without", self.memosEnabled, self.memosExpire, self.memosLimit))

    def isAccessAuthorised(self, person=None, actionName=None, protectedObject=None, avoidMemos=False, **kwds):
        request = None
        isAuthorised = False
        memoizeResult = False
        memoName = None
        if not person:
            person = self.getVisitor()
        request = self.buildRequest(person=person, actionName=actionName, protectedObject=protectedObject, **kwds)
        try:
            request.validate()
            if moddebug:
                self.logRequest(request)
            result = AccessControlResult(request=request)
            if self.usingMemos and not avoidMemos:
                memoName = self.makeMemoName(request)
                self.assertNotMemoized(memoName)
                memoizeResult = True
            self.setAction(result)
            self.assertAccessNotBarred(result)
            self.assertAccessNotAuthorised(result) 
            raise AccessIsForbidden("default")
        except AccessIsAuthorised, inst:
            msg = "AccessController: Allowing %s: by %s." % (
                request.summarise(), inst
            )
            self.logger.info(msg)
            isAuthorised = True
        except AccessIsForbidden, inst:
            msg = "AccessController: Denying %s: by %s." % (
                request.summarise(), inst
            )
            self.logger.info(msg)
        except Exception, inst:
            msg = "AccessController: Error whilst checking access for"
            msg += " %s: %s" % (
                request.summarise(), inst
            )
            msg += "\n" + traceback.format_exc()
            self.logger.error(msg)
        if memoizeResult:
            self.storeMemo(memoName, isAuthorised)
        return isAuthorised

    def buildRequest(self, person=None, actionName=None, protectedObject=None, **kwds):
        return AccessControlRequest(person=person, actionName=actionName,
            protectedObject=protectedObject, **kwds)

    def logRequest(self, request):
        msg = "Deciding access for %s." % request.summarise()
        self.logger.info("AccessController: %s" % msg)

    def makeMemoName(self, request):
        personTag = request.person and request.person.id or 'None'
        actionTag = request.actionName
        protectedTag = MakeProtectedNames(request.protectedObject).make()[0]
        return "Person.%s-%s-%s" % (personTag, actionTag, protectedTag)

    def assertNotMemoized(self, memoName):
        if moddebug:
            self.logger.info("AccessController: Checking %s memos for '%s' result." % (len(self.memosFifo), memoName))
        if memoName not in self.memosCache:
            return
        isAuthorised = self.memosCache.get(memoName, None)
        isExpired = False
        ageDelta = None
        if memoName in self.memosAge:
            ageDelta = dm.times.getUniversalNow() - self.memosAge[memoName]
            isExpired = ageDelta.days >= 1 or ageDelta.seconds >= self.memosExpire
        if isExpired:
            if memoName in self.memosFifo:
                self.memosFifo.remove(memoName)
            wasAuthorised = self.memosCache.pop(memoName, None)
            wasStored = self.memosAge.pop(memoName, None)
            self.logger.info("AccessController: Expired memo '%s' was %s at %s (age: %s)" % (memoName, wasAuthorised, wasStored, ageDelta))
            return
        if isAuthorised == True:
            raise AccessIsAuthorised('memo of previous check')
        elif isAuthorised == False:
            raise AccessIsForbidden('memo of previous check')

    def storeMemo(self, memoName, isAuthorised):
        if moddebug:
            self.logger.info("AccessController: Storing memo '%s': %s" % (memoName, isAuthorised))
        if memoName in self.memosFifo:
            self.memosFifo.remove(memoName)
        if len(self.memosFifo) >= self.memosLimit:
            # Drop the last one.
            retiredName = self.memosFifo.pop()
            wasAuthorised = self.memosCache.pop(retiredName, None)
            wasStored = self.memosAge.pop(retiredName, None)
            self.logger.info("AccessController: Retired oldest memo '%s' was %s at %s" % (retiredName, wasAuthorised, wasStored))
        self.memosFifo.insert(0, memoName)
        self.memosCache[memoName] = isAuthorised
        self.memosAge[memoName] = dm.times.getUniversalNow()

    def setAction(self, result):
        try:
            result.action = self.registry.actions[result.request.actionName]
        except KforgeRegistryKeyError:
            raise AccessIsForbidden("invalid action")

    def assertAccessNotBarred(self, result):
        pass

    def assertAccessNotAuthorised(self, result):
        pass

    def assertRoleNotBarred(self, result, role, msg=''):
        if moddebug:
            self.logger.info("AccessController: Checking '%s' not barred." % role)
        if result.isPermissionSet(role.bars, 'barred', msg):
            raise AccessIsForbidden(msg)

    def assertRoleNotAuthorised(self, result, role, msg=''):
        if moddebug:
            self.logger.info("AccessController: Checking '%s' not authorised." % role)
        if result.isPermissionSet(role.grants, 'authorised', msg):
            raise AccessIsAuthorised(msg)

    def alsoCheckVisitor(self, result):
        return self.getVisitor() and result.request.person != self.getVisitor()

    def getVisitor(self):
        if self.visitor == None:
            visitorName = self.dictionary[VISITOR_NAME]
            try:
                self.visitor = self.registry.people[visitorName]
            except KforgeRegistryKeyError:
                pass
        return self.visitor


class SystemAccessController(BaseAccessController):
    "Introduces personal and system roles to base access controller."

    def assertAccessNotBarred(self, result):
        self.assertPersonNotBarred(result)

    def assertPersonNotBarred(self, result):
        self.assertRoleNotBarred(result, result.request.person, 'personal role')

    def assertAccessNotAuthorised(self, result):
        self.assertSystemRoleNotAuthorised(result)
        self.assertPersonNotAuthorised(result)
        
    def assertSystemRoleNotAuthorised(self, result):
        self.assertPersonSystemRoleNotAuthorised(result)
        if self.alsoCheckVisitor(result):
            self.assertVisitorSystemRoleNotAuthorised(result)

    def assertPersonSystemRoleNotAuthorised(self, result):
        role = result.request.person.role
        self.assertRoleNotAuthorised(result, role, "system %s role" % role.name.lower())

    def assertVisitorSystemRoleNotAuthorised(self, result):
        role = self.getVisitor().role
        self.assertRoleNotAuthorised(result, role, "visitor's system %s role" % role.name.lower())

    def assertPersonNotAuthorised(self, result):
        self.assertRoleNotAuthorised(result, result.request.person, 'personal role')

