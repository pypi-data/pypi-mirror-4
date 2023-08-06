import os
import sys
import optparse

import dm.environment
from dm.cli.base import CommandLineUtility
from dm.exceptions import KforgeError, MissingConfigurationPath
import traceback
from dm.dictionarydef import *

class MethodError(object): pass

class AdministrationUtility(CommandLineUtility):
    "Supports command-line system adminstration."
    
    def __init__(self):
        CommandLineUtility.__init__(self) # old style class
        self.dictionary = None
        self.appInstance = None
        self.interactive = 0
        self.prompt = '> '

    def getLogger(self):
        import dm.log
        return dm.log.log

    def default(self, line):
        print 'Error: Not a valid command: %s' % line
        errorStatus = int(not self.interactive)
        return errorStatus

    def run_interactive(self):
        "Run an interactive session."
        print 'Welcome to interactive mode.'
        print 'Type "?", "help" or "about" for more information.'
        print ''
        while 1:
            try:
                self.cmdloop()
                #break
            except KeyboardInterrupt:
                print ''
                print 'Use "quit" or Ctrl-D (i.e. EOF) to exit.'
                print ''

    def getApplication(self):
        # Todo: Rename 'appInstance' attribute as 'application'.
        if self.appInstance == None:
            self.buildApplication()
        return self.appInstance
        
    def buildApplication(self):
        import dm.soleInstance
        self.appInstance = dm.soleInstance.application

    def loadAllPlugins(self):
        for plugin in self.getApplication().registry.plugins:
            plugin.getSystem()

    def convertLineToArgs(self, line):
        unstrippedArgs = line.strip().split()
        self.args = [arg.strip() for arg in unstrippedArgs]
        return self.args

    def do_settings(self, line=None):
        settings = self.getSettings()
        for setting in settings:
            print setting[0], "=", setting[1]

    def getSettings(self):
        #settings = self.getSystemDictionary().items()
        self.loadAllPlugins()
        settings = self.getApplication().dictionary.items()
        settings.sort()
        return settings

    def help_settings(self, line=None):
        usage = \
'''settings

List system dictionary settings, which are based on KForge configuration file.
'''
        print usage

    def do_checksettings(self, line=None):
        dictionary = self.getApplication().dictionary
        settings = self.getSettings()
        errors = []
        for s in settings:
            key = s[0]
            value = s[1]
            if isinstance(key, DictionaryDef):
                try:
                    key.check(value, dictionary)
                except DictionaryDefinitionError, inst:
                    print inst
                    errors.append(inst)
                else:
                    print "OK %s: %s" % (key, value)
        if errors:
            print
            print "There were errors."
            print
            for inst in errors:
                print inst
            print
            return 1
        else:
            print
            print "Everything looks OK."
            return 0

    def help_checksettings(self):
        usage = \
'''checksettings

Check the configuration options are okay.
'''
        print usage

    def do_setup(self, line=None):
        self.convertLineToArgs(line)
        # Todo: Setup from dump file (optional argument on the command line?).
        # Todo: Setup with admin password (optional argument on the command line?).
        self.createFilesystem()
        dumpPath = None
        if len(self.args) == 1:
            dumpPath = self.args[0]
        try:
            self.takeDatabaseAction('create')
        except Exception, inst:
            print "Warning: Couldn't create the database: %s" % inst
            print "Trying to init the database anyway..."
        if dumpPath:
            self.migrateLoad(dumpPath)
        else:
            self.takeDatabaseAction('init')
        self.getApplication()
        self.buildApacheConfig()

    def help_setup(self, line=None):
        usage = \
'''setup [DUMPFILE]

Set up a new KForge service from given KForge configuration file, optionally
using a DUMPFILE containing domain model data dumped from an existing service.
'''
        print usage

    def do_migratedump(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 1:
            print 'Error: Inappropriate arguments\n'
            self.help_migratedump(line)
            return 1
        dumpPath = self.args[0]
        self.migrateDump(dumpPath)

    def migrateDump(self, dumpPath):
        self.getApplication()
        from dm.migrate import DomainModelDumper
        dataDumper = DomainModelDumper()
        dataDumper.dumpDataToFile(dumpPath)

    def help_migratedump(self, line=None):
        usage = \
'''migratedump filepath

Dump service object model (equals 'db dump')
'''
        print usage

    def do_migratedumpfiles(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 1:
            print 'Error: Inappropriate arguments\n'
            self.help_migratedumpfiles(line)
            return 1
        self.getApplication()
        self.migrateDumpFiles()

    def migrateDumpFiles(self):
        filesDumpDirPath = self.args[0]
        dumper = self.createFilesDumper()
        dumper.dumpInDir(filesDumpDirPath)

    def createFilesDumper(self):
        from dm.migrate import FilesDumper
        return FilesDumper()

    def help_migratedumpfiles(self, line=None):
        usage = \
'''migratedumpfiles dirpath

Dump service filesystem files
'''
        print usage

    def do_migrateload(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 1:
            print 'Error: Inappropriate arguments\n'
            self.help_migrateload(line)
            return 1
        dumpPath = self.args[0]
        self.migrateLoad(dumpPath)

    def migrateLoad(self, dumpPath):
        self.getApplication()
        dataLoader = self.getDomainModelLoaderClass()()
        dataLoader.loadDataFromFile(dumpPath)
        self.touchMigratedDomainModel()

    def getDomainModelLoaderClass(self):
        from dm.migrate import DomainModelLoader
        return DomainModelLoader

    def touchMigratedDomainModel(self):
        pass

    def help_migrateload(self, line=None):
        usage = \
'''migrateload filepath

Load migrated service data (equals 'db init')
'''
        print usage

    def do_backup(self, line):
        self.convertLineToArgs(line)
        if len(self.args) != 1:
            print 'Error: Insufficient arguments\n'
            self.help_backup(line)
            return 1
        else:
            self.backupSystemService()
            return 0

    def backupSystemService(self):
        raise Exception, "Method not implemented."

    def help_backup(self, line=None):
        usage  = 'backup dest\n'
        usage += '\tdest is the path to which you wish to backup'
        print usage
     
    def do_db(self, line=None):
        """Run db commands
        """
        args = self.convertLineToArgs(line)
        actionName = args[0]
        if actionName in ['rebuild', 'delete', 'create', 'init', 'dump']:
            if actionName in ['init'] and len(args) == 2:
                dumpPath = args[1]
                self.migrateLoad(dumpPath) 
            elif actionName in ['dump'] and len(args) == 2:
                dumpPath = args[1]
                self.migrateDump(dumpPath) 
            elif actionName in ['rebuild', 'delete', 'create', 'init'] and len(args) == 1:
                try:
                    self.takeDatabaseAction(actionName)
                except Exception, inst:
                    trace = traceback.format_exc()
                    print trace
                    # Fix up the logging, and write the traceback to the log.
                    print "Error: Couldn't %s the domain data: %s" % (actionName, str(inst))
                    return 1
            else:
                print 'Error: Insufficient arguments\n'
                self.help_db(line)
                return 1
        else:
            print "Error: action '%s' is not supported\n" % actionName
            self.help_db(line)
            return 1
       
    def takeDatabaseAction(self, actionName):
        dictionary = self.getSystemDictionary() # Need to have DJANGO_SETTING_MODULE set.
        dbUtilClass = self.getDatabaseUtilityClass()
        dbUtil = dbUtilClass() # Todo: Pass in the dictionary.
        actionMethod = getattr(dbUtil, actionName)
        actionMethod()

    def getDatabaseUtilityClass(self):
        from dm.util.db import Database
        return Database
       
    def help_db(self, line=None):
        usage  = \
'''db <action>
  action = create | delete | init [DUMPFILE] | rebuild | dump DUMPFILE

db create  - Creates new database instance using configuration file values.
db init    - Writes initial system domain data into virgin database instance.
db delete  - Deletes existing database instance using configuration file values.
db rebuild - Deletes, creates, and then writes the database.
db dump    - Exports domain data to a (dump) file.

NB: If running in interactive mode, a known issue is that due to 
persisted db connections, once you have run db init or db rebuild
you cannot run any other db commands again in the same session.'''
        # [[TODO: display docstrings for each function from db class here
        # Database.__dict__[cmd].__doc__
        print usage

    def do_upgrade(self, line=None):
        # TODO use system version to specify upgrade script used
        # todo: Remove fs/db choice (who does one and not the other).
        args = self.convertLineToArgs(line)
        if len(args) != 1:
            self.help_upgrade(line)
            return 1
        elif args[0] == 'fs':
            self.upgradeSystemServiceFilesystem()
            return 0
        elif args[0] == 'db':
            self.upgradeSystemServiceDatabase()
            return 0
        else:
            print 'Unknown arguments: %s' % args
            self.help_upgrade()

    def upgradeSystemServiceFilesystem(self):
        raise Exception, "Method not implemented."
        
    def upgradeSystemServiceDatabase(self):
        raise Exception, "Method not implemented."
        
    def help_upgrade(self, line=None):
        usage = \
'''upgrade <object>
  object = fs | db

Upgrade a deployment (files and database)'''
        print usage
    
    def do_fs(self, line=None):
        args = self.convertLineToArgs(line)
        if len(args) == 0:
            print 'Error: Insufficient arguments\n'
            self.help_fs(line)
            return 1
        elif args[0] == 'create':
            try:
                self.createFilesystem()
                return 0
            except Exception, inst:
                print "Error: Couldn't create filesystem: %s" % str(inst)
        else:
            self.help_fs()
            return 1

    def help_fs(self, line=None):
        usage = \
'''fs create 

Install template and media files to filesystem paths set in your
service configuration file (see 'templates_dir' and 'media_dir').
'''
        print usage

    def createFilesystem(self):
        from dm.command.initialise import InitialiseFilesystem
        dictionary = self.getSystemDictionary()
        command = InitialiseFilesystem(dictionary)
        command.execute()

    def getSystemDictionary(self):
        if self.dictionary == None:
            if self.appInstance:
                self.dictionary = self.appInstance.dictionary
            else:
                self.dictionary = self.constructSystemDictionary()
        return self.dictionary

    def constructSystemDictionary(self):
        from dm.dictionary import SystemDictionary
        return SystemDictionary()

    def do_apacheconfig(self, line=None):
        args = self.convertLineToArgs(line)
        if len(args) == 0:
            self.help_apacheconfig(line)
            return 1
        try:
            self.getApplication()
        except Exception, inst:
            msg = "Error: %s" % str(inst)
            print msg
            return 1
        if args[0] in ['build', 'create', 'rebuild']:
            try:
                self.buildApacheConfig()
            except Exception, inst:
                print traceback.format_exc()
                msg = "Error: Couldn't generate Apache configuration: %s" % str(inst)
                print msg
                return 1
        elif args[0] == 'reload':
            try:
                self.reloadApacheConfig()
            except Exception, inst:
                msg = "Error: Couldn't reload Apache configuration: %s" % str(inst)
                print msg
                return 1
        elif args[0] == 'path':
            try:
                self.printApacheConfigPath()
            except Exception, inst:
                msg = "Error: Couldn't print Apache configuration path: %s" % str(inst)
                print msg
                return 1
        else:
            self.help_apacheconfig(line)
            return 1

    def help_apacheconfig(self, line=None):
        help = 'apacheconfig [ create | reload | path]\n'
        help += '\tcreate: create web server configuration\n'
        help += '\treload: reload web server configuration\n'
        help += '\tpath: prints path to web server configuration\n'
        print help

    def buildApacheConfig(self):
        configBuilder = self.createApacheConfigBuilder()
        configBuilder.buildAll()

    def reloadApacheConfig(self):
        configBuilder = self.createApacheConfigBuilder()
        configBuilder.reloadConfig()

    def printApacheConfigPath(self):
        configBuilder = self.createApacheConfigBuilder()
        print configBuilder.getConfigPath()

    def createApacheConfigBuilder(self):
        configBuilderClass = self.getApacheConfigBuilderClass()
        configBuilder = configBuilderClass()
        return configBuilder

    def getApacheConfigBuilderClass(self):
        from dm.apache.config import ApacheConfigBuilder
        return ApacheConfigBuilder

    def do_www(self, line=None):
        return self.do_apacheconfig(line)

    def help_www(self, line=None):
        return self.help_apacheconfig(line)

    def do_shell(self, line=None):
        import code
        code.interact()

    def help_shell(self, line=None):
        help = \
'''shell: run a Python interactive shell

Used to administer domain objects. For a full guide to usage of
the interactive shell for administration of a domain model see:
http://knowledgeforge.net/kforge/svn/trunk/docs/cli_shell.txt 
'''
        print help

    def do_about(self, args=None):
        print self.createAboutMessage()

    def help_about(self, line=None):
        help = \
'''about: print basic information about this application

'''
        print help

    def createAboutMessage(self):
        raise Exception, "Method not implemented."

    def do_help(self, line=None):
        CommandLineUtility.do_help(self, line)
        
    def help_help(self, line=None):
        help = \
'''help: print information about commands

'''
        print help

    def do_quit(self, line=None):
        sys.exit()
    
    def help_quit(self, line=None):
        help = \
'''quit: terminate interactive session

'''
        print help

    def do_EOF(self, *args):
        print ''
        sys.exit()

    def help_EOF(self, line=None):
        help = \
'''EOF: terminate interactive session

'''
        print help

    def do_exit(self, *args):
        print 'Use "quit" or Ctrl-D (i.e. EOF) to exit.'
        print ''

    def help_exit(self, line=None):
        print 'Use "quit" or Ctrl-D (i.e. EOF) to exit.'
        print 

class UtilityRunner(object):

    usage  = """Usage: %prog [options] [command]"""

    # Todo: Resolve having multiple definitions of this variable.
    systemName = 'domainmodel'
    utilityClass = AdministrationUtility

    def __init__(self, *args, **kwds):
        packageName = self.systemName == 'domainmodel' and 'dm' or self.systemName
        djangoSettingsModule = '%s.django.settings.main' % packageName
        os.environ['DJANGO_SETTINGS_MODULE'] = djangoSettingsModule
        self.environment = dm.environment.SystemEnvironment(self.systemName)
        self.configFilePathEnvironVariableName = self.environment.getConfigFilePathEnvironmentVariableName()
        self.createOptionParser()
        self.createOptionParserOptions()
        self.parseArgs()
        self.concatenateArgs()
        if self.isHelpRequest():
            self.runUtilityOnce()
            return
        elif self.isVersionRequest():
            self.runUtilityOnce('about')
            return
        else:
            if self.options.configPath:
                # Set the environment from the option.
                configFilePath = os.path.abspath(self.options.configPath)
                os.environ[self.configFilePathEnvironVariableName] = configFilePath
            if self.isScriptRequest():
                self.runScript()
                return
            try:
                if self.isInteractiveRequest():
                    errorStatus = self.runUtilityInteractive()
                    sys.exit(errorStatus)
                elif len(self.args) > 0:

                    if not os.environ.get(self.configFilePathEnvironVariableName, ''):
                        raise MissingConfigurationPath
                    #self.handleNullArgs()
                    errorStatus = self.runUtilityOnce(self.line)
                    sys.exit(errorStatus)
                else:
                    self.handleNullArgs()
            except MissingConfigurationPath, inst:
                print 'Path to configuration file has not been set.'
                print 'Please set %s in environment,' % self.configFilePathEnvironVariableName
                print 'or alternatively use the --config option.'
                sys.exit(1)
                

    def handleNullArgs(self):
        self.optionParser.print_help()
        utility = self.createUtility()
        utility.do_help()
        sys.exit(1)
 
    def createOptionParser(self):
        optionParserClass = optparse.OptionParser
        self.optionParser = optionParserClass(self.usage)
        
    def createOptionParserOptions(self):
        self.optionParser.add_option(
            '--version',
            action='store_true',
            dest='version',
            default=False,
            help='Display version information'
        )
        self.optionParser.add_option(
            '-i', '--interactive',
            action='store_true',
            dest='interactive',
            default=False,
            help='Start interactive mode'
        )
        self.optionParser.add_option(
            '-v', '--verbose',
            action='store_true',
            dest='isVerbose',
            default=False,
            help='Increase verbosity'
        )
        self.optionParser.add_option(
            '--config',
            action='store',
            dest='configPath',
            default='',
            help='Path to service configuration file. Sets ' + \
                 '%s in execution environment' % self.configFilePathEnvironVariableName
        )
        self.optionParser.add_option(
            '-c', '--script',
            action='store_true',
            dest='script',
            default=False,
            help='Executes the admin script. Pass path as first argument.'
        )

    def parseArgs(self):
        (options, args) = self.optionParser.parse_args()
        self.options = options
        self.args = args

    def concatenateArgs(self):
        "Concatenates input arguments as one single-line string."
        argStrings = [str(arg) for arg in self.args]
        self.line = ' '.join(argStrings)

    def isHelpRequest(self):
        return len(self.args) > 0 and self.args[0] == 'help'
   
    def isVersionRequest(self):
        return self.options.version

    def isInteractiveRequest(self):
        return self.options.interactive

    def isScriptRequest(self):
        return self.options.script

    def runUtilityOnce(self, line=None):
        if line == None:
            line = self.line
        utility = self.createUtility()
        errorStatus = utility.onecmd(line)
        return errorStatus
        
    def runUtilityInteractive(self, line=None):
        if line == None:
            line = self.line
        utility = self.createUtility()
        errorStatus = utility.run_interactive()
        return errorStatus

    def createUtility(self):
        return self.utilityClass()

    def runScript(self):
        # Todo: Generalise implementation in provide.cli.admin.
        pass

