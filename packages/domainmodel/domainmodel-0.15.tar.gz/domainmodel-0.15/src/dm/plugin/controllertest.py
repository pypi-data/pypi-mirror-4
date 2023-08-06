import unittest
from dm.testunit import TestCase
import dm.plugin.controller
from dm.exceptions import *

def suite():
    suites = [
            unittest.makeSuite(TestPluginController),
        ]
    return unittest.TestSuite(suites)

class TestPluginController(TestCase):
    "TestCase for the PluginController class."

    def setUp(self):
        super(TestPluginController, self).setUp()
        self.controller = dm.plugin.controller.PluginController()

    def testExists(self):
        self.failUnless(self.controller, "No controller was created.")
    
    def testGetPlugins(self):
        plugins = self.controller.getPlugins()
        self.failUnless(plugins.count, "No plugins available.")
        
    def testNotifyRun(self):
        self.controller.notify(eventName='Run', eventSender=None)
    
    def testNotifyNewProject(self):
        self.controller.notify(eventName='NewProject', eventSender=None)
    
    def testNotifyApproveProject(self):
        self.controller.notify(eventName='ApproveProject', eventSender=None)

    def testNotifyDeleteProject(self):
        self.controller.notify(eventName='DeleteProject', eventSender=None)

    def testNotifyNewPerson(self):
        self.controller.notify(eventName='NewPerson', eventSender=None)
    
    def testNotifyApprovePerson(self):
        self.controller.notify(eventName='ApprovePerson', eventSender=None)

    def testNotifyDeletePerson(self):
        self.controller.notify(eventName='DeletePerson', eventSender=None)

    def testNotifyNewMember(self):
        self.controller.notify(eventName='NewMember', eventSender=None)
    
    def testNotifyApproveMember(self):
        self.controller.notify(eventName='ApproveMember', eventSender=None)

    def testNotifyDeleteMember(self):
        self.controller.notify(eventName='DeleteMember', eventSender=None)

    def testNotifyPlugin(self):
        if 'testingexample' in self.registry.plugins:
            plugin = self.registry.plugins['testingexample']
            plugin.delete()
            plugin.purge()
        countBefore = len(self.controller.getPlugins())
        pluginDomainObject = self.registry.plugins.create('testingexample')
        self.failUnless(pluginDomainObject, "No plugin domain object.")
        pluginSystem = pluginDomainObject.getSystem()
        self.failUnless(pluginSystem, "No plugin system.")
        countAfterCreate = len(self.controller.getPlugins())
        pluginDomainObject.delete()
        countAfterDelete = len(self.controller.getPlugins())
        self.failUnlessEqual(countBefore+1, countAfterCreate)
        self.failUnlessEqual(countBefore, countAfterDelete)

