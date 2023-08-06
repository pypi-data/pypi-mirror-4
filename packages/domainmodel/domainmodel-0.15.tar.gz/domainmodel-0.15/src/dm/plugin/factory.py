from dm.ioc import *
import dm.exceptions
from dm.plugin.base import PluginBase
from dm.dictionarywords import PLUGIN_PACKAGE_NAME
from dm.dictionarywords import PLUGINS_AVAILABLE

# Todo: Change the get methods to raise exceptions rather than returning None.

class PluginFactory(object):

    dictionary = RequiredFeature('SystemDictionary')
    logger     = RequiredFeature('Logger')

    def getAvailableNames(self):
        return PLUGINS_AVAILABLE.parse(self.dictionary[PLUGINS_AVAILABLE])

    def getPlugin(self, domainObject):
        "Returns plugin system object for given plugin domain object."
        pluginName = domainObject.name
        pluginClass = self.getPluginClass(pluginName)
        if pluginClass:
            return pluginClass(domainObject)
        else:
            return None

    def getPluginClass(self, pluginName):
        "Returns plugin system class for given plugin name."
        pluginPackage = self.getPluginPackage(pluginName)
        pluginClass = None
        if pluginPackage:
            pluginPackageDict = pluginPackage.__dict__
            for value in pluginPackageDict.values():
                if type(value) == type and issubclass(value, PluginBase) \
                    and value.__module__.split('.')[-1] == pluginName:
                        if pluginClass:
                            msg = "Two plugin classes found in "
                            msg += "'%s' plugin module: " % pluginName
                            msg += "%s" % repr(pluginPackage)
                            raise dm.exceptions.MultiplePluginSystems(msg)
                        pluginClass = value
            if not pluginClass:
                msg = "Couldn't find a subclass of PluginBase in "
                msg += "'%s' plugin module: " % pluginName
                msg += "%s" % repr(pluginPackage)
                raise dm.exceptions.MissingPluginSystem(msg) 
        return pluginClass

    def getPluginPackage(self, pluginName):
        "Imports named plugin package."
        pluginPackageName = self.dictionary[PLUGIN_PACKAGE_NAME]
        pluginPackageName += '.' + pluginName
        try:
            pluginPackage = __import__(pluginPackageName, '', '', '*')
            if not pluginPackage:
                raise Exception("No plugin package was imported.")
        except Exception, inst:
            msg = "Could not import '%s' plugin package: %s." % (
                pluginPackageName, inst
            )
            self.logger.warn(msg)
            pluginPackage = None
        return pluginPackage

