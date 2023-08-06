import os
import getpass
from dm.exceptions import *

class SystemEnvironment(object):
    "Boundary object encapsulating environment variables."

    DJANGO_SETTINGS_MODULE = 'DJANGO_SETTINGS_MODULE'

    def __init__(self, systemName):
        self.systemName = systemName
        if self.systemName == 'domainmodel':
            self.systemPyName = 'dm'
        else:
            self.systemPyName = self.systemName

    def assertDjangoSettingsModule(self):
        "Raises exception if DJANGO_SETTINGS_MODULE not set in environment."
        if self.DJANGO_SETTINGS_MODULE in os.environ:
            djangoSettingsModuleName = os.environ[self.DJANGO_SETTINGS_MODULE]
        else:
            raise Exception, "Variable '%s' not set in environment." % (
                self.DJANGO_SETTINGS_MODULE
            )
        if djangoSettingsModuleName:
            firstPackageName = djangoSettingsModuleName.split('.')[0]
            if firstPackageName != self.systemPyName:
                msg = "In environment, %s %s looks wrong for %s system." % (
                    self.DJANGO_SETTINGS_MODULE, 
                    djangoSettingsModuleName, self.systemPyName
                )
                raise Exception, msg
        else:
            raise Exception, "%s value in environment not valid: '%s'" % (
                self.DJANGO_SETTINGS_MODULE,
                djangoSettingModuleName
            )

    def getConfigFilePath(self):
        "Reads path to system's configuration file from environment variable."
        name = self.getConfigFilePathEnvironmentVariableName()
        if name in os.environ:
            path = os.environ[name]
        else:
            message = "Environment variable '%s' not set." % name
            raise EnvironmentError, message
        path = os.path.abspath(path)
        return path
        
    def getSystemUserName(self):
        "Reads system username from environment variable."
        return getpass.getuser()
        
    def getPythonPath(self):
        "Reads path to system's python library from environment variable."
        return os.environ.get('PYTHONPATH', '')
        
    def getConfigFilePathEnvironmentVariableName(self):
        name = self.systemName.upper() + '_SETTINGS'
        return name

    def isAvoidingEnablingModelCache(self):
        return os.environ.get('AVOID_ENABLING_MODEL_CACHE', '')

    def setTimezone(self, timezone):
        os.environ['TZ'] = timezone

