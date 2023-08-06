from dm.ioc import *
from dm.builder import ApplicationBuilder
from dm.dictionarywords import MODEL_CACHE_IS_ENABLED
from dm.dictionarywords import MODEL_CACHE_IS_PRELOADED
from dm.dictionarywords import DB_MIGRATION_IN_PROGRESS
from dm.dictionarywords import ENABLE_EMAIL_SENDING 

class Application(object):
    """Directs application and model builders for clients.
    
    Attributes
    ==========

    commands
    --------

    dictionary of available commands keyed by the name of the command. Commands
    are used to encapsulate more complex operations that may involve several
    domain objects.  
    
    dictionary
    ----------
    
    The system dictionary which includes all configuration information
    including that which may have been loaded from a configuration file.

    registry
    --------

    The DomainRegistry object which provides access to all objects in the
    domain model.

    logger
    ------

    An instance of the application logger

    debug
    -----

    A boolean storing whether the application is in debug mode. Used to allow
    conditional logging of debug information.
    """

    builderClass = ApplicationBuilder

    commands     = RequiredFeature('CommandSet')
    dictionary   = RequiredFeature('SystemDictionary')
    registry     = RequiredFeature('DomainRegistry')
    logger       = RequiredFeature('Logger')
    debug        = RequiredFeature('Debug')

    def __init__(self):
        super(Application, self).__init__()
        self.buildApplication()

    def buildApplication(self):
        appBuilder = self.builderClass()
        appBuilder.construct()
        if self.registry != None:
            domBuilder = RequiredFeature('ModelBuilder')
            domBuilder.construct()
            if self.dictionary[MODEL_CACHE_IS_ENABLED] and self.dictionary[MODEL_CACHE_IS_PRELOADED] and not self.dictionary[DB_MIGRATION_IN_PROGRESS]:
                domBuilder.preload()
        if not self.dictionary[ENABLE_EMAIL_SENDING]:
            self.logger.info("Warning: Email sending is not enabled.")

