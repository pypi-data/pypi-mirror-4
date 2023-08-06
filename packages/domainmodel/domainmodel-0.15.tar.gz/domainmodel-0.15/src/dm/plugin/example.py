from dm.plugin.base import PluginBase

class Plugin(PluginBase):

    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        self.counts = {}
        self.counts['onRun'] = 0

    def onRun(self, sender):
        self.counts['onRun'] += 1

