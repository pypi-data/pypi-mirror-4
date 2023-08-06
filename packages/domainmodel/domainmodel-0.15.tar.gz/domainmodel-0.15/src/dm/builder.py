"""
Application builder. Used by a "director" to inject feature dependencies.
"""

from dm.ioc import *

class ApplicationBuilder(object):

    def construct(self):
        features.register('SystemDictionary', self.findSystemDictionary())
        features.register('SystemMode',       self.findSystemMode())
        features.register('Debug',            self.findDebug())
        features.register('Logger',           self.findLogger())
        features.register('DatabaseFacade',   self.findDatabaseFacade())
        features.register('DomainRegistry',   self.findDomainRegistry())
        features.register('ModelBuilder',     self.findModelBuilder())
        features.register('PluginController', self.findPluginController())
        features.register('PluginFactory',    self.findPluginFactory())
        features.register('CommandSet',       self.findCommandSet())
        features.register('FileSystem',       self.findFileSystem())
        features.register('AccessController', self.findAccessController())
        features.register('Timepoint',        self.findTimepoint())

    def findSystemDictionary(self):
        import dm.dictionary
        return dm.dictionary.SystemDictionary()

    def findSystemMode(self):
        import dm.mode
        return dm.mode.SystemMode()

    def findDebug(self):
        import dm.debug
        return dm.debug.Debug().isDebug()

    def findDomainRegistry(self):
        import dm.dom.registry
        return dm.dom.registry.DomainRegistry()

    def findModelBuilder(self):
        import dm.dom.builder
        return dm.dom.builder.ModelBuilder()

    def findLogger(self):
        import dm.log
        return dm.log.getLogger()

    def findPluginController(self):
        import dm.plugin.controller
        return dm.plugin.controller.PluginController()

    def findPluginFactory(self):
        import dm.plugin.factory
        return dm.plugin.factory.PluginFactory()

    def findDatabaseFacade(self):
        import dm.db
        return dm.db.DatabaseFacade()

    def findCommandSet(self):
        import dm.command
        return dm.command.__dict__

    def findFileSystem(self):
        import dm.filesystem
        return dm.filesystem.FileSystemPathBuilder()

    def findAccessController(self):
        import dm.accesscontrol
        return dm.accesscontrol.SystemAccessController()

    def findTimepoint(self):
        import dm.timepoint
        return dm.timepoint.Timepoint()

