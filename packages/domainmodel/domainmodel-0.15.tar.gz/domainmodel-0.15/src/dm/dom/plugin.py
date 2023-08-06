from dm.dom.stateful import *
from dm.ioc import *
from dm.dictionarywords import PLUGINS_AVAILABLE
from dm.exceptions import ValidationError

def getProjects():
    domainRegistry = RequiredFeature('DomainRegistry')
    return domainRegistry.projects

def getPluginChoices():
    dictionary = RequiredFeature('SystemDictionary')
    availablePlugins = PLUGINS_AVAILABLE.parse(dictionary[PLUGINS_AVAILABLE])
    return [(i, i) for i in availablePlugins]


class PluginNameValidator(AttributeValidator):

    pluginFactory = RequiredFeature('PluginFactory')

    def validate(self):
        attrName = self.metaAttr.name
        if attrName in self.objectData:
            attrValue = self.objectData[attrName]
            if not self.pluginFactory.getPluginClass(attrValue):
                msg = "Cannot load '%s' plugin." % attrValue
                raise ValidationError(msg)


class Plugin(StandardObject):
    "Registered plugin."

    name = String(isIndexed=True, isRequired=True, isImmutable=True,
        isUnique=True, validators=[PluginNameValidator], getChoices=getPluginChoices)

    pluginFactory = RequiredFeature('PluginFactory')
   
    def __init__(self, **kwds):
        super(Plugin, self).__init__(**kwds)
        self.__system = None
    
    def initialise(self, register):
        "Initialises the plugin system."
        # Todo: Document what 'register' is.
        pluginSystem = self.getSystem()
        if pluginSystem:
            pluginSystem.initialise(register)

    def getSystem(self):
        "Returns plugin system modelled by domain object."
        if not self.__system:
            self.__system = self.pluginFactory.getPlugin(self)
        return self.__system

    def getModelExtnClass(self):
        "Returns the model extention domain class for this plugin."
        return self.getSystem().getModelExtnClass()

    def getExtnRegister(self):
        "Returns the plugin system's domain object register."
        return self.getSystem().getRegister()

    def getExtnObject(self, service):
        "Returns one of the plugin system's domain objects."
        extnRegister = self.getSystem().getRegister()
        if service in extnRegister:
            return extnRegister[service]
        else:
            return None

