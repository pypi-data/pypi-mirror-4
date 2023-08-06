import re
import dm.regexps
from dm.command.base import * 

class PluginCommand(Command):
    "Abstract Plugin command."

    pluginFactory = None
        
    def __init__(self, name):
        super(PluginCommand, self).__init__(pluginName=name)
        self.name = name
        self.plugin = None
        self.plugins = self.registry.plugins

    def isPluginNameImportable(self):
        try:
            self.getPluginPackage(self.name)
        except:
            return False
        else:
            return True

    def assertDependencies(self):
        package = self.getPluginPackage(self.name)
        # todo: look for subclass in __dict__, instead of:
        if hasattr(package, 'Plugin'):
            systemClass = package.Plugin
            systemClass.assertDependencies()

    def getPluginPackage(self, name):
        factory = self.getPluginFactory()
        return factory.getPluginPackage(name)

    def getPluginFactory(self):
        if not PluginCommand.pluginFactory:
            pluginPackageName = self.dictionary['plugin_package']
            package = __import__(pluginPackageName, '', '', '*')
            factory = package.PluginFactory()
            PluginCommand.pluginFactory = factory
        return PluginCommand.pluginFactory


class PluginCreate(DomainObjectCreate):
    "Command to create a new plugin."

    reservedNames = re.compile('^%s$' % dm.regexps.reservedPluginName)

    def __init__(self, name='', **kwds):
        super(PluginCreate, self).__init__(
            typeName='Plugin', objectId=name, objectKwds=kwds
        )
        self.plugin = None

    def execute(self):
        super(PluginCreate, self).execute()
        self.plugin = self.object


class PluginDelete(PluginCommand):
    "Deletes plugin."

    def __init__(self, name):
        super(PluginDelete, self).__init__(name)

    def execute(self):
        "Make it so."
        super(PluginDelete, self).execute()
        if not self.name in self.plugins:
            message = "No plugin found with name '%s'." % self.name
            self.raiseError(message)
        plugin = self.plugins[self.name]
        try:
            system = plugin.getSystem()
            system.assertNoDependents()
        except Exception, inst:
            self.raiseError(str(inst))
        try:
            plugin.delete()
        except Exception, inst:
            message = "Couldn't delete that plugin: %s" % str(inst)
            self.raiseError(message)
        else:
            self.commitSuccess()


class PluginRead(PluginCommand):
    "Reads registered plugin."

    def __init__(self, name):
        super(PluginRead, self).__init__(name)

    def execute(self):
        "Make it so."
        super(PluginRead, self).execute()
        if not self.name in self.plugins:
            message = "No plugin found with name '%s'." % self.name
            self.raiseError(message)
        self.plugin = self.plugins[self.name]

class PluginList(PluginCommand):
    "Lists registered plugins."

    def __init__(self):
        super(PluginList, self).__init__('')

    def execute(self):
        "Make it so."
        super(PluginList, self).execute()
        self.results = self.getPlugins()

    def getPlugins(self):
        return [p for p in self.plugins]
       
class ProjectPluginList(PluginList):
    "Lists available service plugins for a given project."

    def __init__(self, project):
        self.project = project
        super(ProjectPluginList, self).__init__()

    def getPlugins(self):
        plugins = []
        for plugin in self.plugins:
            numServices = len(plugin.services.findDomainObjects(project=self.project))
            maxServices = plugin.getMaxServicesPerProject()
            if maxServices == None or numServices < maxServices:
                plugins.append(plugin)
        return plugins

