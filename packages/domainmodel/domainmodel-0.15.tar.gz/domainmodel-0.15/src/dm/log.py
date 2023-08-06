"""
System logger.

"""

import logging
import logging.handlers
import os
from dm.ioc import RequiredFeature
from dm.dictionarywords import *

# Todo: Fix this up more.

class UmaskRotatingFileHandler(logging.handlers.RotatingFileHandler):

    def _open(self):
        dictionary = RequiredFeature('SystemDictionary')
        umask = dictionary.getUmask()
        prevumask = os.umask(umask)
        rtv = logging.handlers.RotatingFileHandler._open(self)
        os.umask(prevumask)
        return rtv


def initLogging():
    dictionary = RequiredFeature('SystemDictionary')
    logPath = os.path.abspath(dictionary[LOG_PATH])
    dirPath = os.path.dirname(logPath)
    if not os.path.exists(dirPath):
        # Need parents to have permission 750.
        umask = os.umask(0o027)
        try:
            if not os.path.exists(os.path.dirname(dirPath)):
                os.makedirs(os.path.dirname(dirPath))
            # But need log directory to have permission 770.
            os.umask(0o007)
            os.makedirs(dirPath)
        finally:
            os.umask(umask)
    logLevel = logging.INFO
    logLevels = {
        'DEBUG'    : logging.DEBUG,
        'INFO'     : logging.INFO,
        'WARNING'  : logging.WARNING,
        'ERROR'    : logging.ERROR,
        'CRITICAL' : logging.CRITICAL
    }
    logLevelName = dictionary[LOG_LEVEL].upper()
    if logLevelName in logLevels:
        logLevel = logLevels[logLevelName]
    elif logLevelName:
        raise Exception, "Logging level not in valid list: %s" % (
            " ".join(logLevels.keys())
        )
    
    #fileFormat = '%(name)s:%(levelname)s %(module)s:%(lineno)d: %(message)s'
    fileFormat = '[%(asctime)s] %(message)s'
    fileFormatter = logging.Formatter(fileFormat)
    
    #fileHandler = logging.handlers.RotatingFileHandler(
    fileHandler = UmaskRotatingFileHandler(
        logPath,
        mode='a+',
        maxBytes=10000000,
        backupCount=5
    )
    fileHandler.setFormatter(fileFormatter)
    fileHandler.setLevel(logLevel)
    
    systemLogger = getLogger()
    systemLogger.addHandler(fileHandler)
    systemLogger.setLevel(logLevel)
    LOG_PATH.test(logPath, dictionary)
    
def getLogger():
    dictionary = RequiredFeature('SystemDictionary')
    systemName = dictionary[SYSTEM_NAME]
    return logging.getLogger(systemName)
 
initLogging()
log = getLogger()
log.info('Logger: Logging initialised.')

