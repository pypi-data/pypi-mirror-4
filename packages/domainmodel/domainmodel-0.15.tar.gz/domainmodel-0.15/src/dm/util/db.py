import os
import commands

import dm.ioc
from dm.dictionarywords import DB_DELETE_COMMAND, DB_CREATE_COMMAND

class Database(object):
    """Manipulate service database.

    As some of these methods must function when the database does not exist it
    is important that the features used are highly restricted so as to ensure
    that a dependency on the database is not created.
    """

    features = dm.ioc.features

    def create(self):
        """Create a service database."""
        self._runCommandFromDictionary(DB_CREATE_COMMAND)

    def init(self):
        """
        Initialises service database by creating initial domain object records.
        """
        initModelCommandClass = self.getInitModelCommandClass()
        initModelCommand = initModelCommandClass()
        initModelCommand.execute()

    def rebuild(self):
        """Rebuild service database (delete + create + init)
        Allow for possibility that database does not already exist.
        """
        try:
            self.delete()
        except Exception, instd:
            try:
                self.create()
            except:
                raise Exception(instd)
        else:
            self.create()
        self.init()

    def delete(self):
        "Delete a service database."
        self._runCommandFromDictionary(DB_DELETE_COMMAND)

    def getInitModelCommandClass(self):
        commandSet = self.getApplicationCommandSet()
        return commandSet['InitialiseDomainModel']

    def getApplicationCommandSet(self):
        import dm.soleInstance
        commandSet = dm.soleInstance.application.commands
        return commandSet

    def _runCommandFromDictionary(self, commandName):
        self._registerSystemDictionaryFeature()
        self.dictionary = self.features['SystemDictionary']
        cmd = self.dictionary[commandName]
        try:
            self._runCommand(cmd)
        finally:
            self._deregisterSystemDictionaryFeature()

    def _registerSystemDictionaryFeature(self):
        self.didRegistration = False
        if not 'SystemDictionary' in self.features:
            systemDictionary = self._getSystemDictionary()
            self.features.register('SystemDictionary', systemDictionary)
            self.didRegistration = True
    
    def _getSystemDictionary(self):
        # override in derived classes
        import dm.dictionary
        systemDictionary = dm.dictionary.SystemDictionary()
        return systemDictionary

    def _runCommand(self, cmd):
        status, output = commands.getstatusoutput(cmd)
        if status:
            msg = 'Command "%s" failed: %s' % (cmd, output)
            raise(Exception(msg))

    def _deregisterSystemDictionaryFeature(self):
        if self.didRegistration:
            self.features.deregister('SystemDictionary')
   
