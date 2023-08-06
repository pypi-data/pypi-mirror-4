"""
Test-by-example plugin module.

"""

import dm.plugin.base

class Plugin(dm.plugin.base.PluginBase):
    "Testing example plugin class."

    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)

    def onRun(self, sender):
        "Trivial run handler."
        self.log("Testing example plugin received onRun event.")
        return 1

    def onProjectCreate(self, project):
        "Trivial run handler."
        self.log("Testing example plugin received onProjectCreate event!")
        return 1

    def onProjectApprove(self, project):
        "Trivial run handler."
        self.log("Testing example plugin received onProjectApprove event!")
        return 1

    def onDeletePlugin(self, project):
        "Trivial run handler."
        self.log("Testing example plugin received onDeletePlugin event!")
        return 1

    def onNewPlugin(self, project):
        "Trivial run handler."
        self.log("Testing example plugin received onNewPlugin event!")
        return 1

    def onProjectDelete(self, project):
        "Trivial run handler."
        self.log("Testing example plugin received onProjectDelete event!")
        return 1

    def onPersonCreate(self, project):
        "Trivial run handler."
        self.log("Testing example plugin received onPersonCreate event!")
        return 1

    def onPersonApprove(self, project):
        "Trivial run handler."
        self.log("Testing example plugin received onPersonApprove event!")
        return 1

    def onPersonDelete(self, project):
        "Trivial run handler."
        self.log("Testing example plugin received onPersonDelete event!")
        return 1

    def onMemberCreate(self, project):
        "Trivial run handler."
        self.log("Testing example plugin received onMemberCreate event!")
        return 1

    def onMemberApprove(self, project):
        "Trivial run handler."
        self.log("Testing example plugin received onMemberApprove event!")
        return 1

    def onMemberDelete(self, project):
        "Trivial run handler."
        self.log("Testing example plugin received onMemberDelete event!")
        return 1

