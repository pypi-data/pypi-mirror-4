import unittest
from dm.testunit import TestCase
import dm.plugin.base

def suite():
    suites = [
            unittest.makeSuite(PluginBaseTest),
        ]
    return unittest.TestSuite(suites)

class PluginBaseTest(TestCase):
    "TestCase for the PluginBase class."

    def setUp(self):
        super(PluginBaseTest, self).setUp()
        while 'MyPluginBaseTest' in self.registry.roles:
            role = self.registry.roles['MyPluginBaseTest']
            role.delete()
        self.namedObject = self.registry.roles.create('MyPluginBaseTest')
        self.plugin = dm.plugin.base.PluginBase(self.namedObject)

    def tearDown(self):
        self.namedObject.delete()

    def testExists(self):
        self.failUnless(self.plugin, "No plugin object was created.")

    def testOnRun(self):
        self.plugin.onRun(None)

    def testOnNewProject(self):
        self.plugin.onProjectCreate(None)

    def testOnDeleteProject(self):
        self.plugin.onProjectDelete(None)

    def testOnNewPerson(self):
        self.plugin.onPersonCreate(None)
    
    def testOnDeletePerson(self):
        self.plugin.onPersonDelete(None)

    def testOnNewMember(self):
        self.plugin.onMemberCreate(None)

    def testOnDeleteMember(self):
        self.plugin.onMemberDelete(None)
    
    def getApacheConfig(self):
        self.plugin.getApacheConfig()

