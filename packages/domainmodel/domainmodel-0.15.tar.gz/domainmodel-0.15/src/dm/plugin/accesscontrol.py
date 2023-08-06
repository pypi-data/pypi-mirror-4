from dm.plugin.base import PluginBase

class Plugin(PluginBase):

    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        name = 'accesscontrol'

