import dm
from dm.config import ConfigFileReader
import os
import dm.dictionarywords
from dm.dictionarywords import *
from dm.environment import SystemEnvironment
import dm.times
from dm.exceptions import InvalidSystemDictionary
from dm.exceptions import MissingConfigurationPath
from dm.exceptions import FilePermissionError
import datetime
# Todo: Check Django settings has DEFAULT_CHARSET == 'utf-8'.
import stat


class SystemDictionary(dict):
    "Dictionary of system attributes."

    words = dm.dictionarywords 

    filePermissions = {
        'readable by others': stat.S_IROTH,
        'writable by others': stat.S_IWOTH,
        'executable by others': stat.S_IXOTH,
        'readable by group': stat.S_IRGRP,
        'writable by group': stat.S_IWGRP,
        'executable by group': stat.S_IXGRP,
        'readable by user': stat.S_IRUSR,
        'writable by user': stat.S_IWUSR,
        'executable by user': stat.S_IXUSR,
    }

    def __init__(self):
        super(SystemDictionary, self).__init__()
        self.assertSystemName()
        self.environment = SystemEnvironment(self.getSystemName())
        self.assertSystemEnvironment()
        self.setDefaultWords()
        self.initConfigFilePath()
        self.initFilesystemPath()
        self.assertConfigFileExists()
        self.makeConfigFileReader()
        self.readConfigFile()  # Todo: Validate configuration file items.
        self.setWordsFromConfigFile()
        self.setWordsFromWords()
        self.setConfigFilePathWord()
        self.setNewWordsFromOld()
        self.setWordsFromEnvironment()
        self.initTimezone()
        self.initUmask()
        self.validateDictionaryWords()
        self.assertWebkitEnvironment()
        self.setSystemStarted()

    def assertSystemName(self):
        if not self.getSystemName():
            raise Exception, "No system name!"
        
    def setSystemStarted(self):
        self[SYSTEM_STARTED] = dm.times.getUniversalNow()

    def assertSystemEnvironment(self):
        pass

    def assertWebkitEnvironment(self):
        if self[WEBKIT_NAME] == 'django':
            self.environment.assertDjangoSettingsModule()
        
    def initConfigFilePath(self):
        self.configFilePath = self.environment.getConfigFilePath().strip()

    def setDefaultWords(self):
        self[PYTHONPATH]          = '' #os.environ.get('PYTHONPATH', '')
        self[SYSTEM_NAME]         = self.getSystemName()
        self[SYSTEM_TITLE]        = self.getSystemTitle()
        self[SYSTEM_PACKAGE_NAME] = self.getSystemPackageName()
        self[SYSTEM_SERVICE_NAME] = self.getSystemServiceName()
        self[SYSTEM_MODE]         = 'production'
        self[SYSTEM_VERSION]      = self.getSystemVersion()
        self[SYSTEM_USER_NAME]    = self.getSystemUserName()
        self[UMASK]               = '0o007'
        self[FILESYSTEM_PATH]     = ''
        self[PASSWORD_DIGEST_SECRET] = 'not-a-secret'
        self[VISITOR_NAME]        = 'visitor'
        self[VISITOR_ROLE]        = 'Visitor'
        self[INITIAL_PERSON_ROLE] = 'Visitor'
        self[MODEL_CACHE_IS_ENABLED] = ''
        self[MODEL_CACHE_IS_PRELOADED] = ''
        self[MODEL_CACHE_CLASSES] = ''
        self[PLUGIN_PACKAGE_NAME] = 'dm.plugin'
        self[PLUGINS_AVAILABLE]   = 'example'
        self[CAPTCHA_IS_ENABLED]  = '' # False (ConfigParser only supports str)
        self[AUTH_COOKIE_NAME]    = '%s_auth' % self[SYSTEM_NAME]
        self[NO_AUTH_COOKIE_NAME] = '%s_no_auth' % self[SYSTEM_NAME]
        self[LOG_PATH]            = ''
        self[LOG_LEVEL]           = 'WARNING'
        self[APACHE_PYTHON_MODULE]= 'mod_wsgi'
        self[APACHE_IP_ADDRESS]   = '*'
        self[APACHE_CONFIG_PATH]  = ''
        self[APACHE_RELOAD_CMD]   = 'sleep 1 && sudo /etc/init.d/apache2 graceful'
        self[APACHE_WSGI_REDIRECT_DELAY] = '0'
        self[ENABLE_RELOAD_APACHE] = ''
        self[APACHE_CONFIGTEST_CMD] = '' #'sudo /etc/init.d/apache2 configtest'
        self[WSGI_SCRIPT_PATH]    = ''
        self[WSGI_PROCESS_GROUP]  = ''
        self[DNS_DOMAIN_NAME]     = self.getDnsDomainName()
        self[SITE_HOST]         = '%s.%s' % (self[SYSTEM_NAME], self[DNS_DOMAIN_NAME])
        self[HTTP_PORT]           = '80'
        self[HTTPS_PORT]          = '443'
        self[URL_SCHEME]          = 'http'
        self[URI_PREFIX]          = ''
        self[MEDIA_PATH]          = ''
        self[MEDIA_HOST]          = ''
        self[MEDIA_PORT]          = '' 
        self[MEDIA_PREFIX]        = '/media'
        # For values of the TIMEZONE word, please read the information
        # about the TZ environment variable in this tzset() reference:
        #     http://docs.python.org/lib/module-time.html
        self[TIMEZONE]            = '' # Defaults to unchanged environment.
        self[SERVICE_EMAIL]       = ''
        self[ENABLE_EMAIL_SENDING]  = ''
        self[SMTP_HOST]           = 'localhost'
        self[SMTP_PORT]           = ''
        self[SMTP_USER]           = ''
        self[SMTP_PASSWORD]       = ''
        self[SMTP_USE_TLS]        = ''
        self[EMAIL_NOTIFY_CHANGES]= ''
        self[IMAGES_DIR_PATH]     = ''
        # Potential values: 'mysql', 'postgres', 'sqlite', 'firebird', 'sybase', 'maxdb', 'mssql'.
        self[DB_TYPE]             = 'sqlite' 
        self[DB_HOST]             = 'localhost'
        self[DB_NAME]             = ''
        self[DB_USER]             = ''
        self[DB_PASS]             = ''
        self[DB_SUPER_USER]       = ''
        self[DB_SUPER_PASS]       = ''
        self[DB_CREATE_COMMAND]   = ''  # Default depends on DB_TYPE.
        self[DB_DELETE_COMMAND]   = ''  # Default depends on DB_TYPE.
        self[DB_MIGRATION_IN_PROGRESS] = ''
        self[DJANGO_SECRET_KEY]   = 'not-a-secret'
        self[DJANGO_TEMPLATES_DIR] = ''
        self[EDITOR]              = 'editor' # Debian specific...
        self[WEBKIT_NAME] = 'django' # No value other than 'django' supported.
        self[VIRTUALENVBIN_PATH]  = ''
        self[MEMOS_LIMIT]         = '3000'
        self[MEMOS_EXPIRE]        = '30'
        self[MEMOS_ENABLED]       = ''
        self[TEMPLATES_RESOURCE_PATH] = 'django/templates'
        self[MEDIA_RESOURCE_PATH] = 'django/media'
        self[HTTP_AUTH_REALM] = ''
        self[API_KEY_HEADER_NAME] = 'X-%s-API-Key' % self.getSystemTitle()

    def setConfigFilePathWord(self):
        self[SYSTEM_CONFIG_PATH] = os.path.abspath(self.configFilePath)

    def assertConfigFileExists(self):
        if not os.path.isfile(self.configFilePath):
            raise Exception("Configuration file not found on path: %s" % self.configFilePath)

    def initFilesystemPath(self):
        # FILESYSTEM_PATH ('master_dir')
        configDirPath = os.path.dirname(self.configFilePath)
        if os.path.basename(configDirPath) in ['etc', 'config']:
            filesystemPath = os.path.dirname(configDirPath)
        else:
            filesystemPath = configDirPath
        self[FILESYSTEM_PATH]     = filesystemPath

    def makeConfigFileReader(self):
        defaults = {}
        # Need to avoid setting defaults for sections (raises errors if not
        # found in config file).
        [defaults.__setitem__(i, self[i]) for i in self if '.' not in i] 
        self.configFileReader = ConfigFileReader(defaults=defaults)
        
    def readConfigFile(self):
        self.assertConfigFilePermissions()
        pathList = [self.configFilePath]
        try:
            self.configFileReader.read(pathList)
        except Exception, inst:
            msg = "Couldn't read configuration file: %s" % str(inst)
            raise Exception, msg
        
    def assertConfigFilePermissions(self):
        assert self.configFilePath
        try:
            mode = self.getFilePermissions(self.configFilePath)
            if not mode & stat.S_IRUSR:
                raise FilePermissionError, "file not readable by user: %s" % self.configFilePath
            if mode & stat.S_IXUSR:
                raise FilePermissionError, "file executable by user: %s" % self.configFilePath
            if not mode & stat.S_IRGRP:
                raise FilePermissionError, "file not readable by group: %s" % self.configFilePath
            if mode & stat.S_IWGRP:
                raise FilePermissionError, "file writable by group: %s" % self.configFilePath
            if mode & stat.S_IXGRP:
                raise FilePermissionError, "file executable by group: %s" % self.configFilePath
            if mode & stat.S_IROTH:
                raise FilePermissionError, "file readable by other: %s" % self.configFilePath
            if mode & stat.S_IWOTH:
                raise FilePermissionError, "file writable by other: %s" % self.configFilePath
            if mode & stat.S_IXOTH:
                raise FilePermissionError, "file executable by other: %s" % self.configFilePath
            child = self.configFilePath
            parent = os.path.dirname(child)
            while parent != child:
                mode = self.getFilePermissions(parent)
                if not mode & stat.S_IXUSR:
                    raise FilePermissionError, "directory not executable by user: %s" % parent
                if not mode & stat.S_IXGRP:
                    raise FilePermissionError, "directory not executable by group: %s" % parent
                if mode & stat.S_IWGRP:
                    raise FilePermissionError, "directory writable by group: %s" % parent
                if mode & stat.S_IWOTH:
                    raise FilePermissionError, "directory writable by other: %s" % parent
                child = parent
                parent = os.path.dirname(child)
        except FilePermissionError, inst:
            msg = "Config file permission error: %s" % inst
            raise FilePermissionError, msg

    def assertSqliteFilePermissions(self, path):
        DatabaseFileSetting(DB_NAME).test(path, self)

    def getFilePermissions(self, path):
        return os.stat(path).st_mode

    def assertFileFitsUmask(self, path):
        perms = os.stat(path).st_mode
        umask = self.getUmask()
        conflict = perms & 0777 & umask
        if conflict:
            names = []
            for name, value in self.filePermissions.items():
                if value & conflict:
                    names.append(name)
            names.sort()
            msg = "Umask setting '0o%o' conflicts with file permissions '0o%o' (conflicting bits '0o%o': %s): %s" % (umask, perms, conflict, "; ".join(names), path)
            raise FilePermissionError, msg

    def assertFilePermission(self, mask, permission, isRequired):
        flag = self.filePermissions[permission]
        if bool(mask & flag) != isRequired:
            isOrIsnot = isRequired and "is not" or "is"
            msg = "File %s %s" % (isOrIsnot, permission)
            raise FilePermissionError, msg

    def setWordsFromConfigFile(self):
        configWords = self.configFileReader.keys()
        definedWords = self.listDefinedWords()
        for configWord in configWords:
            if configWord not in definedWords:
                continue
            configValue = self.configFileReader[configWord].strip()
            # Todo: Interestingly, converting all dict values to 
            # unicode breaks things quite a lot. Find out why!
            #if type(configValue) == str:
                #configValue = configValue.decode('utf-8')
                #print "%s %s" % (configWord, repr(configValue))
            self[configWord] = configValue

    def listDefinedWords(self):
        words = self.words.__dict__.items()
        words = [i[1] for i in words if i[0] == i[0].upper()]
        return words

    def setWordsFromWords(self):
        # Filesystem paths.
        if not self[FILESYSTEM_PATH]:
            configDirPath = os.path.dirname(self.configFilePath)
            if os.path.basename(configDirPath) in ['etc', 'config']:
                self[FILESYSTEM_PATH] = os.path.dirname(configDirPath)
            else:
                self[FILESYSTEM_PATH] = configDirPath

        if not self[LOG_PATH]:
            logFilePath = os.path.join('var', 'log', '%s.log' % self[SYSTEM_NAME])
            self[LOG_PATH] = os.path.join(self[FILESYSTEM_PATH], logFilePath)

        if not self[MEDIA_PATH]:
            self[MEDIA_PATH] = os.path.join(self[FILESYSTEM_PATH], 'media')

        if not self[IMAGES_DIR_PATH]:
            self[IMAGES_DIR_PATH] = os.path.join(self[FILESYSTEM_PATH], 'images')

        if not self[DJANGO_TEMPLATES_DIR]:
            self[DJANGO_TEMPLATES_DIR] = os.path.join(self[FILESYSTEM_PATH], 'templates')

        if not self[APACHE_CONFIG_PATH]:
            apacheConfigFilePath = os.path.join('var', 'httpd-autogenerated.conf')
            self[APACHE_CONFIG_PATH] = os.path.join(self[FILESYSTEM_PATH], apacheConfigFilePath)

        if not self[WSGI_SCRIPT_PATH]:
            wsgiScriptPath = os.path.join('wsgi', '%s.wsgi' % self[SYSTEM_NAME])
            self[WSGI_SCRIPT_PATH] = os.path.join(self[FILESYSTEM_PATH], wsgiScriptPath)
        if not self[WSGI_PROCESS_GROUP]:
            self[WSGI_PROCESS_GROUP] = self[SITE_HOST]

        # Media host and post.
        if not self[MEDIA_PORT]:
            self[MEDIA_PORT] = self[HTTP_PORT]
        # Database configuration.
        if not self[DB_NAME]:
            if self[DB_TYPE] == 'sqlite':
                sqlitePath = os.path.join('var', '%s.db' % self[SYSTEM_NAME])
                self[DB_NAME] = os.path.join(self[FILESYSTEM_PATH], sqlitePath)

            else:
                self[DB_NAME] = self[SYSTEM_NAME]
        if not self[DB_USER]:
            self[DB_USER] = self[SYSTEM_NAME]
        if not self[DB_SUPER_USER]:
            self[DB_SUPER_USER] = self[DB_USER]
        if not self[DB_SUPER_PASS]:
            self[DB_SUPER_PASS] = self[DB_PASS]
        # Database create and delete commands.
        dbCmds = {
          'postgres': {
            'create': "createdb -h %(host)s -U %(super_user)s %(name)s",
            'delete': "dropdb -h %(host)s -U %(super_user)s %(name)s",
          },
          'mysql': {
            'create': "mysqladmin -h'%(host)s' -u'%(super_user)s' -p'%(super_pass)s' create %(name)s",
            'delete': "mysqladmin -h'%(host)s' -u'%(super_user)s' -p'%(super_pass)s' --force drop %(name)s",
          },
          'sqlite': {
            'create': "touch %(name)s",
            'delete': "rm %(name)s",
          },
        }
        dbVars = {
          'name': self[DB_NAME],
          'user': self[DB_USER],
          'pass': self[DB_PASS],
          'host': self[DB_HOST],
          'super_user': self[DB_SUPER_USER],
          'super_pass': self[DB_SUPER_PASS],
        }
        if not self[DB_CREATE_COMMAND]:
            if self[DB_TYPE] in dbCmds:
                try:
                    cmd = dbCmds[self[DB_TYPE]]['create'] % dbVars
                except:
                    msg = "Couldn't generate %s database create command. Commands: %s Vars: %s" % (self[DB_TYPE], dbCmds, dbVars)
                self[DB_CREATE_COMMAND] = cmd
            else:
                msg = "Inferring database create command for database type"
                msg += " '%s' not supported." % self[DB_TYPE]
                msg += " Try setting 'create_command = ...' in the [db]"
                msg += " section of the configuration file."
                raise Exception, msg
        if not self[DB_DELETE_COMMAND]:
            if self[DB_TYPE] in dbCmds:
                try:
                    cmd = dbCmds[self[DB_TYPE]]['delete'] % dbVars
                except:
                    msg = "Couldn't generate %s database delete command. Commands: %s Vars: %s" % (self[DB_TYPE], dbCmds, dbVars)
                self[DB_DELETE_COMMAND] = cmd
            else:
                msg = "Inferring database delete command for database type"
                msg += " '%s' not supported." % self[DB_TYPE]
                msg += " Try setting 'delete_command = ...' in the [db]"
                msg += " section of the configuration file."
                raise Exception, msg
        if PYTHONPATH_ALT in self:
            if not self[PYTHONPATH]:
                self[PYTHONPATH] = self.pop(PYTHONPATH_ALT)
        if self[VIRTUALENVBIN_PATH]:
            if self[PYTHONPATH]:
                self[PYTHONPATH] = self[VIRTUALENVBIN_PATH]+":"+self[PYTHONPATH]
            else:
                self[PYTHONPATH] = self[VIRTUALENVBIN_PATH]
        if not self[HTTP_AUTH_REALM]:
            realm = self[SYSTEM_SERVICE_NAME]
            realm = realm.decode('utf-8').replace('#', '\#')
            self[HTTP_AUTH_REALM] = realm
        if not self[SERVICE_EMAIL]:
            self[SERVICE_EMAIL] = "noreply@%s" % self[DNS_DOMAIN_NAME]
        lastModified = self.readApacheConfigLastModified()
        self[APACHE_CONFIG_LAST_MODIFIED] = lastModified
        
    def readApacheConfigLastModified(self):    
        apacheConfigPath = self[APACHE_CONFIG_PATH]
        if apacheConfigPath and os.path.exists(apacheConfigPath):
            timestamp = os.path.getmtime(apacheConfigPath)
            return datetime.datetime.utcfromtimestamp(timestamp)
        return None

    def getUmask(self):
        return UMASK.parse(self[UMASK])

    def setNewWordsFromOld(self):
        # Support usage of old dictionary words in existing config files.
        self.setNewWordFromOld(DB_PASS, OLD_DB_PASS)
        self.setNewWordFromOld(MEDIA_PATH, OLD_MEDIA_PATH)
  
    def setWordsFromEnvironment(self):
        if self.environment.isAvoidingEnablingModelCache():
            self[MODEL_CACHE_IS_ENABLED] = False
   
    def setNewWordFromOld(self, new, old):
        if old in self:
            # Todo: Warn of deprecation.
            if not self[new]:
                self[new] = self.pop(old)
   
    
    def getSystemVersion(self):
        return dm.__version__

    def getSystemUserName(self):
        return self.environment.getSystemUserName()

    def getSystemTitle(self):
        systemName = self[SYSTEM_NAME]
        if systemName == 'domainmodel':
            systemTitle = 'DomainModel'
        else:
            systemTitle = systemName.capitalize()
        return systemTitle

    def getSystemName(self):
        return 'domainmodel'

    def getSystemPackageName(self):
        systemName = self.getSystemName()
        if systemName == 'domainmodel':
            packageName = 'dm'
        else:
            packageName = systemName
        return packageName

    def getSystemServiceName(self):
        return self.getSystemName().capitalize()

    def getDnsDomainName(self):
        import commands
        status, output = commands.getstatusoutput('dnsdomainname')
        if not status:
            return output
        else:
            raise Exception, "Couldn't determine dnsdomainname."

    def initTimezone(self):
        if self[TIMEZONE]:
            self.environment.setTimezone(self[TIMEZONE])
            dm.times.resetTimezone()

    def initUmask(self):
        if self[UMASK]:
            os.umask(self.getUmask())

    def set(self, name, value):
        self[name] = value

    def validateDictionaryWords(self):
        self.validateUriPrefix()
        # Todo: Move the checksettings code in here.
        # Todo: Move the validation methods to the definition classes.
        # Todo: Automate going through and validating all attributes (which have definitions).

    def validateUriPrefix(self):
        uriPrefix = self[URI_PREFIX]
        if uriPrefix == '':
            return
        if uriPrefix[0] != '/':
            msg = "No leading slash on '%s': '%s'." % (
                URI_PREFIX, self[URI_PREFIX]
            )
            raise InvalidSystemDictionary(msg)
        if uriPrefix[-1] == '/':
            msg = "Trainling slash on '%s': '%s'." % (
                URI_PREFIX, self[URI_PREFIX]
            )
            raise InvalidSystemDictionary(msg)
        
