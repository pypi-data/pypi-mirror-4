"""System exception classes."""

# todo: Rename Kforge out of this module.

class DomainModelApplicationError(StandardError): pass

class MissingConfigurationPath(DomainModelApplicationError): pass

class FilePermissionError(DomainModelApplicationError): pass

class ORMError(DomainModelApplicationError): pass

class DictionaryDefinitionError(DomainModelApplicationError): pass

class InvalidSystemDictionary(DomainModelApplicationError): pass

class AccessControlException(DomainModelApplicationError): pass

class AccessIsAuthorised(AccessControlException): pass

class AccessIsForbidden(AccessControlException): pass

class DataMigrationError(DomainModelApplicationError): pass

class MissingMethodError(DomainModelApplicationError): pass

class MissingPluginSystem(DomainModelApplicationError): pass

class WebkitError(DomainModelApplicationError): pass

class ValidationError(DomainModelApplicationError): pass

class FormError(DomainModelApplicationError):

    def __init__(self, errors, isSystemError=False):
        self.errors = errors
        self.isSystemError = isSystemError

    def __repr__(self):
        return "FormError(%s, isSystemError=%s)" % (self.errors, self.isSystemError)

    def __str__(self):
        return str(self.errors)

# todo: Rework the KForge exception classes.
class KforgeError(DomainModelApplicationError):
    "Kforge exception superclass."
    pass

class KforgeAbstractMethodError(KforgeError):
    "Unimplemented abstract method exception class."
    pass

class KforgeCommandError(KforgeError):
    "Command exception class."
    pass

class KforgePersonActionObjectDeclined(KforgeCommandError):
    "Access control denied class."
    pass
    
class KforgeRegistryKeyError(KforgeError, KeyError):
    "Registry exception class."
    pass
    
class KforgeAttributeError(KforgeError, AttributeError):
    "Registry exception class."
    pass
    
class KforgeSessionCookieValueError(KforgeError):
    "Session cookie exception class."
    pass
    
class KforgeDomError(KforgeError):
    "Domain layer exception class."
    pass

class DomainClassRegistrationError(KforgeDomError):
    "Domain class registration exception class."
    pass
    
class KforgeDbError(KforgeError):
    "Database layer exception class."
    pass

class DbObjectNotFound(KforgeDbError):
    "Exception class raised when a requested object is not found in the database."
    pass

class KforgePluginMethodNotImplementedError(KforgeAbstractMethodError):
    "Missing plugin method exception class."
    pass

class MissingPluginSystem(KforgeError):
    "Missing plugin system exception."

class MultiplePluginSystems(KforgeError):
    "Multiple plugin system exception."


