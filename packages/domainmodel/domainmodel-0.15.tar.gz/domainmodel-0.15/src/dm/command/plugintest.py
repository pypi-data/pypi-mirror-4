import unittest
from dm.testunit import TestCase
import dm.command
from dm.command.plugin import *
from dm.exceptions import *

def suite():
    suites = [
        unittest.makeSuite(TestPluginCreate),
        unittest.makeSuite(TestPluginDelete),
    ]
    return unittest.TestSuite(suites)

class TestPluginCreate(TestCase):
    "TestCase for the PluginCreate command."

    pluginName = 'testingexample'

    def setUp(self):
        super(TestPluginCreate, self).setUp()
        self.command = PluginCreate(self.pluginName)

    def tearDown(self):
        if self.pluginName in self.registry.plugins.getAll():
            plugin = self.registry.plugins[self.pluginName]
            plugin.delete()
            plugin.purge()

    def testExecute(self):
        self.failIf(self.pluginName in self.registry.plugins)
        self.command.execute()
        self.failUnless(self.pluginName in self.registry.plugins)

    def testErrorPluginExists(self):
        self.command.execute()
        self.failUnlessRaises(KforgeCommandError, self.command.execute)

class TestPluginDelete(TestCase):
    "TestCase for the PluginDelete command."

    pluginName = 'testingexample'

    def setUp(self):
        super(TestPluginDelete, self).setUp()
        self.fixtureName = 'TestPluginDelete'
        while self.pluginName in self.registry.plugins.getAll():
            plugin = self.registry.plugins.getAll()[self.pluginName]
            plugin.delete()
            plugin.purge()
            
        self.plugin = self.registry.plugins.create(self.pluginName)
        self.command = PluginDelete(self.pluginName)

    def tearDown(self):
        if self.pluginName in self.registry.plugins.getAll():
            plugin = self.registry.plugins.getAll()[self.pluginName]
            plugin.delete()
            plugin.purge()
        self.command = None

    def testExecute(self):
        self.failUnless(self.pluginName in self.registry.plugins)
        self.command.execute()
        self.failIf(self.pluginName in self.registry.plugins)

    def testErrorNoPlugin(self):
        self.command.execute()
        self.failUnlessRaises(KforgeCommandError, self.command.execute)

