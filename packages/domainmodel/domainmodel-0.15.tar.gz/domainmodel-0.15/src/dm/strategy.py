from dm.ioc import RequiredFeature
from dm.dictionarywords import DJANGO_SECRET_KEY
from dm.exceptions import KforgeSessionCookieValueError 
from dm.exceptions import KforgeRegistryKeyError
from dm.messagedigest import md5
from dm.dom.base import DomainObject, DomainObjectRegister
moddebug = False
import string

class BaseStrategy(object):

    registry = RequiredFeature('DomainRegistry')
    dictionary = RequiredFeature('SystemDictionary')
    debug = RequiredFeature('Debug')
    logger = RequiredFeature('Logger')
    
    def __init__(self):
        pass


class EpochFromDateTime(BaseStrategy):

    def __init__(self, dateTime):
        super(EpochFromDateTime, self).__init__()
        self.dateTime = dateTime
        
    def seconds(self):
        return int(self.dateTime)


# Todo: Split up making protected names, to be more explicit about whether the names
# are for the instance, the class, the register, or just a name. Need to remove
# protection objects for instances without risking removing protection object for class
# and this code doesn't quite eliminate that risk. It's not broken though, but still... 

class MakeProtectedNames(BaseStrategy):

    def __init__(self, protectedObject):
        super(MakeProtectedNames, self).__init__()
        self.protectedObject = protectedObject

    def make(self):
        protectedNames = []
        if self.protectedObject.__class__ == type:
            if moddebug and self.debug:
                self.logger.debug('Making protected name for class: %s' % self.protectedObject)
            className = self.protectedObject.__name__
            protectedNames.append(className)
        elif isinstance(self.protectedObject, DomainObjectRegister):
            if moddebug and self.debug:
                self.logger.debug('Making protected name for register: %s' % self.protectedObject)
            className = self.protectedObject.typeName
            protectedNames.append(className)
        elif isinstance(self.protectedObject, DomainObject):
            if moddebug and self.debug:
                self.logger.debug('Making protected names for instance: %s' % self.protectedObject)
            keyValue = self.protectedObject.id
            className = self.protectedObject.__class__.__name__
            instanceName = className + "." + str(keyValue)
            protectedNames.append(instanceName)
            protectedNames.append(className)
        elif isinstance(self.protectedObject, (str, unicode)):
            protectedNames.append(self.protectedObject)
        else:
            protectedNames.append('System')
        if moddebug and self.debug:
            self.logger.debug('Made protected names: %s' % protectedNames)
        return protectedNames


class MakeProtectedName(BaseStrategy):

    def __init__(self, protectedObject):
        super(MakeProtectedName, self).__init__()
        self.protectedObject = protectedObject

    def make(self):
        makeNames = MakeProtectedNames(self.protectedObject)
        protectedNames = makeNames.make()
        return protectedNames[0]
        

class FindProtectionObjects(BaseStrategy):

    def __init__(self, protectedObject):
        super(FindProtectionObjects, self).__init__()
        self.protectedObject = protectedObject

    def find(self):
        if moddebug and self.debug:
            self.logger.debug('Finding protection objects for: %s' % self.protectedObject)
        makeNames = MakeProtectedNames(self.protectedObject)
        protectedNames = makeNames.make()
        protectionObjects = []
        for name in protectedNames:
            try:
                protection = self.registry.protectionObjects[name]
                protectionObjects.append(protection)
            except KforgeRegistryKeyError:
                pass
        return protectionObjects


class FindInstanceProtectionObject(FindProtectionObjects):
    """Returns protection object for the domain object instance (and not for
    the class as a whole)."""

    def find(self):
        protectionObjects = super(FindInstanceProtectionObject, self).find()
        # Todo: Make sure the protection object has no dots? Or search for
        # protection objects that match the protected name of the instance?
        if len(protectionObjects) == 2:
            return protectionObjects[0]
        else:
            return None
            


class FindProtectionObject(BaseStrategy):

    def __init__(self, protectedObject):
        super(FindProtectionObject, self).__init__()
        self.protectedObject = protectedObject

    def find(self):
        makeNames = MakeProtectedNames(self.protectedObject)
        protectedNames = makeNames.make()
        for name in protectedNames:
            if name in self.registry.protectionObjects:
                return self.registry.protectionObjects[name]
        raise Exception("No protection object for %s (protected names: %s)" % (
            self.protectedObject, protectedNames
        ))


class CreateProtectionObject(BaseStrategy):

    def __init__(self, protectedObject):
        super(CreateProtectionObject, self).__init__()
        self.protectedObject = protectedObject

    def create(self):
        makeName = MakeProtectedName(self.protectedObject)
        protectedName = makeName.make()
        if not protectedName in self.registry.protectionObjects:
            return self.registry.protectionObjects.create(protectedName)
        else:
            return self.registry.protectionObjects[protectedName]


class MakeCheckString(BaseStrategy):

    def __init__(self, plainString):
        super(MakeCheckString, self).__init__()
        self.plainString = plainString

    def make(self):
        plainString = self.plainString
        secretString = self.dictionary[DJANGO_SECRET_KEY]
        inputString = plainString + secretString + 'auth'
        checkString = md5(inputString).hexdigest()
        return checkString


class MakeCookieString(BaseStrategy):

    def __init__(self, plainString):
        super(MakeCookieString, self).__init__()
        self.plainString = plainString

    def make(self):
        if len(self.plainString) != 32:
            msg = "Length of plain string '%s' is not 32." % self.plainString
            raise CookieStringError(msg)
        checkStringStrategy = MakeCheckString(self.plainString)
        checkString = checkStringStrategy.make()
        cookieString = self.plainString + checkString
        return cookieString


class CookieStringError(KforgeSessionCookieValueError): pass


class ValidateCookieString(BaseStrategy):

    def __init__(self, cookieString):
        super(ValidateCookieString, self).__init__()
        self.cookieString = cookieString

    def validate(self):
        if len(self.cookieString) != 64:
            msg = "Length of '%s' is not 64." % self.cookieString
            raise CookieStringError(msg)
        plainString = self.cookieString[:32]
        cookieStringStrategy = MakeCookieString(plainString)
        cookieString = cookieStringStrategy.make()
        if self.cookieString != cookieString:
            msg = "Cookie string '%s' didn't check out." % self.cookieString
            raise CookieStringError(msg)
        return plainString

