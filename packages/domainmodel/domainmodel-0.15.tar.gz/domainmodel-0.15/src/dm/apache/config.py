from dm.ioc import RequiredFeature
from dm.dictionarywords import *
from dm.environment import SystemEnvironment
import commands
import os
import sys
from subprocess import Popen, PIPE
import shlex

class ApacheConfigBuilder(object):

    filesystem = RequiredFeature('FileSystem')
    registry = RequiredFeature('DomainRegistry')
    dictionary = RequiredFeature('SystemDictionary')
    logger = RequiredFeature('Logger')
    debug = RequiredFeature('Debug')

    def __init__(self):
        self.initEnvironment()
        self.initConfigEnvVarName()
        self.initConfigFilePath()

    def initEnvironment(self):
        systemName = self.dictionary[SYSTEM_NAME]
        self.environment = SystemEnvironment(systemName)

    def initConfigEnvVarName(self):
        varName = self.environment.getConfigFilePathEnvironmentVariableName()
        self.systemConfigEnvVarName = varName

    def initConfigFilePath(self):
        self.systemConfigFilePath = self.environment.getConfigFilePath()

    def buildAndReload(self):
        self.buildAll()
        self.reloadConfig()

    def buildAll(self):
        self.buildLocksDir()
        self.buildConfigFile()
        self.buildWsgiFile()
        self.buildCgiFile()

    def buildLocksDir(self):
        pass

    def buildConfigFile(self):
        """
        Creates config content, and writes to config file.
        """
        configPath = self.getConfigPath()
        if not configPath:
            msg = "No Apache configuration file path has been provided. Try setting '%s' in the configuration file: %s" % (APACHE_CONFIG_PATH, self.dictionary.configFilePath)
            raise Exception(msg)
        configContent = self.createConfigContent()
        self.filesystem.writeFile(configPath, configContent, '%s Apache config file' % self.dictionary[SYSTEM_TITLE], umask=0o007)

    def getConfigPath(self):
        return self.dictionary[APACHE_CONFIG_PATH]

    def createConfigContent(self):
        modWsgiWebuiConfig = self.createModWsgiWebuiConfig()
        modPythonWebuiConfig = self.createModPythonWebuiConfig()
        mediaConfig = self.createMediaConfig()
        configContents = {
            'modWsgiWebuiConfig': modWsgiWebuiConfig,
            'modPythonWebuiConfig': modPythonWebuiConfig,
            'mediaConfig': mediaConfig,
        }
        apacheConfigTmpl = """
<IfModule !mod_wsgi.c>
<IfModule mod_python.c>
%(modPythonWebuiConfig)s
</IfModule>
</IfModule>
%(mediaConfig)s
<IfModule mod_wsgi.c>
%(modWsgiWebuiConfig)s
</IfModule>
"""
        return apacheConfigTmpl % configContents


    def createMediaConfig(self):
        configVars = self.getConfigVars()
        apacheConfigTmpl = ''
        if configVars['MEDIA_PREFIX']:
            apacheConfigTmpl += """
# %(SYSTEM_TITLE)s static media files.
Alias %(URI_PREFIX)s%(MEDIA_PREFIX)s/ %(MEDIA_PATH)s/
<Location "%(MEDIA_PREFIX)s/">
  SetHandler None
  Order Deny,Allow
  Allow from all
</Location>

Alias /favicon.ico %(MEDIA_PATH)s/images/favicon.ico
<Location /favicon.ico">
  SetHandler None
  Order Deny,Allow
  Allow from all
</Location>

            """
        return apacheConfigTmpl % configVars

    def createWebuiConfig(self):
        if self.dictionary[APACHE_PYTHON_MODULE] == 'mod_wsgi':
            apacheConfig = self.createModWsgiWebuiConfig()
        elif self.dictionary[APACHE_PYTHON_MODULE] == 'mod_python':
            apacheConfig = self.createModPythonWebuiConfig()
        return apacheConfig

    def createModWsgiWebuiConfig(self):
        apacheConfigTmpl = """
# %(SYSTEM_TITLE)s Web user interface.
WSGIScriptAlias %(WSGI_SCRIPT_ALIAS)s %(WSGI_SCRIPT_PATH)s 
WSGIApplicationGroup %%{GLOBAL}                                                         
WSGIProcessGroup %(WSGI_PROCESS_GROUP)s
"""
        return apacheConfigTmpl % self.getConfigVars()

    def createModPythonWebuiConfig(self):
        apacheConfigTmpl = """
# %(SYSTEM_TITLE)s Web user interface.
<LocationMatch "%(WEBUI_PATH_PATTERNS)s" >
  SetEnv %(CONFIG_ENV_VAR_NAME)s %(SYSTEM_CONFIG_PATH)s
  SetEnv PYTHONPATH %(PYTHON_PATH)s
  SetEnv DJANGO_SETTINGS_MODULE %(DJANGO_SETTINGS_MODULE)s
  SetHandler python-program
  PythonPath "'%(PYTHON_PATH)s'.split(':') + sys.path"
  PythonHandler %(MODPYTHON_HANDLER_MODULE)s
  PythonDebug %(PYTHON_DEBUG)s
</LocationMatch>
"""
        return apacheConfigTmpl % self.getConfigVars()

    def getConfigVars(self):
        if not hasattr(self, 'configVars'):
            self.configVars = self.createConfigVars()
        return self.configVars

    def createConfigVars(self):
        # Assemble variables.
        configVars = {}
        configVars['CONFIG_ENV_VAR_NAME'] = self.environment.getConfigFilePathEnvironmentVariableName()
        configVars['SYSTEM_TITLE'] = self.dictionary[SYSTEM_TITLE]
        configVars['SYSTEM_CONFIG_PATH'] = self.dictionary[SYSTEM_CONFIG_PATH]
        configVars['WSGI_SCRIPT_PATH'] = self.dictionary[WSGI_SCRIPT_PATH]
        configVars['WSGI_PROCESS_GROUP'] = self.dictionary[WSGI_PROCESS_GROUP]
        configVars['WSGI_SCRIPT_ALIAS'] = self.noSlash(self.dictionary[URI_PREFIX]) or '/'
        configVars['PYTHON_PATH'] = self.noSlash(self.dictionary[PYTHONPATH])
        configVars['DJANGO_SETTINGS_MODULE'] = '%s.django.settings.main' % self.dictionary[SYSTEM_NAME]
        configVars['PYTHON_DEBUG'] = self.getPythonDebugMode()
        configVars['URI_PREFIX'] = self.noSlash(self.dictionary[URI_PREFIX])
        configVars['MEDIA_PREFIX'] = self.noSlash(self.dictionary[MEDIA_PREFIX])
        configVars['MEDIA_PATH'] = self.noSlash(self.dictionary[MEDIA_PATH])
        configVars['MODPYTHON_HANDLER_MODULE'] = self.getModPythonHandlerModule()
        configVars['WEBUI_PATH_PATTERNS'] = self.getWebuiPathPatterns()
        configVars['HTTP_AUTH_REALM'] = self.dictionary[HTTP_AUTH_REALM]
        return configVars

    def getWebuiPathPatterns(self):
        return "^%s.*" % self.noSlash(self.dictionary[URI_PREFIX]) + '/'

    def getModPythonHandlerModule(self):
        systemName = self.dictionary[SYSTEM_NAME]
        if self.dictionary[VIRTUALENVBIN_PATH]:
            moduleName = self.getModPythonHandlerModuleNormal()
        else:
            moduleName = self.getModPythonHandlerModuleVirtualenv()
        return moduleName

    def getModPythonHandlerModuleNormal(self):
        return '%svirtualenvhandlers::djangohandler' % self.dictionary[SYSTEM_NAME]

    def getModPythonHandlerModuleVirtualenv(self):
        return '%s.handlers.modpython' % self.dictionary[SYSTEM_NAME]

    def getPythonDebugMode(self):
        return self.isPythonDebugMode() and 'On' or 'Off'

    def isPythonDebugMode(self):
        return self.dictionary[SYSTEM_MODE] == 'development'

    def noSlash(self, path):
        if path and path[-1] == '/':
            path.pop()
        return path

    def buildWsgiFile(self):
        wsgiScriptPath = self.dictionary[WSGI_SCRIPT_PATH]
        wsgiScriptContent = self.createWsgiScriptContent()
        purpose = '%s WSGI script' % self.dictionary[SYSTEM_TITLE]
        self.filesystem.writeWsgiFile(wsgiScriptPath, wsgiScriptContent, purpose)

    def buildCgiFile(self):
        # Todo: CGI script for KForge?
        pass

    def createWsgiScriptContent(self):
        pythonVirtualenvActivation = ''
        pythonPathActivation = ''
        # Determine whether code is running in a virtualenv.
        if self.dictionary[VIRTUALENVBIN_PATH]:
            hasVirtualenv = True
            activateThisPath = os.path.join(self.dictionary[VIRTUALENVBIN_PATH], 'activate_this.py')
        else:
            modulePath = os.path.dirname(sys.modules['dm'].__file__)
            relBinPath = '../../../../bin'
            binPath = os.path.join(modulePath, relBinPath)
            activateThisPath = os.path.join(binPath, 'activate_this.py')
            activateThisPath = os.path.abspath(activateThisPath)
            hasVirtualenv = os.path.exists(activateThisPath)
        if hasVirtualenv:
            # Todo: Revisit in favour of 
            # http://code.google.com/p/modwsgi/wiki/VirtualEnvironments.
            # would just need to know "the full path to the 'site-packages'
            # directory for the virtual environment", but that is available 
            # as os.path.dirname(os.__file__)? Need to baseline WSGI with
            # WSGIPythonHome /usr/local/pythonenv/BASELINE in main Apache
            # configuration. So would have to add that to install guides?
            pythonVirtualenvActivation = """activate_this = '"""+activateThisPath+"""'
execfile(activate_this, dict(__file__=activate_this))"""

        elif self.dictionary[PYTHONPATH]:
            pythonPathActivation = """
for path in %(PYTHON_PATH_LIST)s:
    if path not in sys.path:
        sys.path.append(path)

"""         % {
                'PYTHON_PATH_LIST': self.dictionary[PYTHONPATH].split(':'),
            }
        wsgiScriptBody = """
# %(SYSTEM_TITLE)s auto-generated WSGI File.

import os
import sys

%(PYTHON_PATH_ACTIVATION)s
os.environ['DJANGO_SETTINGS_MODULE'] = '%(SYSTEM_PACKAGE_NAME)s.django.settings.main'
os.environ['%(CONFIG_ENV_VAR_NAME)s'] = '%(SYSTEM_CONFIG_PATH)s'

import %(WSGI_HANDLER_MODULE)s
application = %(WSGI_HANDLER_MODULE)s.WSGIHandler()

"""     % {
            'SYSTEM_TITLE': self.dictionary[SYSTEM_TITLE],
            'SYSTEM_PACKAGE_NAME': self.dictionary[SYSTEM_PACKAGE_NAME],
            'CONFIG_ENV_VAR_NAME': self.environment.getConfigFilePathEnvironmentVariableName(),
            'SYSTEM_CONFIG_PATH': self.dictionary[SYSTEM_CONFIG_PATH],
            'PYTHON_VIRTUALENV_ACTIVATION': pythonVirtualenvActivation,
            'PYTHON_PATH_ACTIVATION': pythonPathActivation,
            'WSGI_HANDLER_MODULE': self.getWsgiHandlerModule(),
        }
        wsgiScriptContent = pythonVirtualenvActivation + wsgiScriptBody
        return wsgiScriptContent

    def getWsgiHandlerModule(self):
        return 'django.core.handlers.wsgi'

    def reloadConfig(self):
        """
        Reloads config into Apache.
        """
        if not self.dictionary[ENABLE_RELOAD_APACHE]:
            msg = "Not reloading Apache since '%s' is not set in configuration." % ENABLE_RELOAD_APACHE
            self.logger.info(msg)
        elif not self.dictionary[APACHE_RELOAD_CMD]:
            msg = "Not reloading Apache since '%s' is not set in configuration." % APACHE_RELOAD_CMD
            self.logger.warning(msg)
        else:
            cmd = self.dictionary[APACHE_RELOAD_CMD]
            msg = "Attempting to reload Apache with command: %s" % cmd
            self.logger.info(msg)
            try:
                self.runPopen(cmd, shell=True)
            except Exception, inst:
                self.logger.error('Exception on reload of apache: %s' % inst)

    def runPopen(self, cmd, stdindata=None, shell=False):
        stdin = PIPE if stdindata != None else None
        try:
            p = Popen(cmd, stdin=stdin, stdout=PIPE, stderr=PIPE, shell=shell)
        except Exception, inst:
            msg = "Error: Popen cmd '%s' caused error: %s" % (cmd, repr(inst))
            self.logger.error(msg)
            raise Exception(msg)

