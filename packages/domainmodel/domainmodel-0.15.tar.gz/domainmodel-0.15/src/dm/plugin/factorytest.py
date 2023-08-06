import unittest
from dm.testunit import TestCase
import dm.plugin.factory
from dm.exceptions import *

def suite():
    suites = [
            unittest.makeSuite(TestPluginFactory),
        ]
    return unittest.TestSuite(suites)


class TestPluginFactory(TestCase):
    "TestCase for the PluginFactory class."

    def setUp(self):
        super(TestPluginFactory, self).setUp()
        self.setUpFactory()

    def setUpFactory(self):
        self.factory = dm.plugin.factory.PluginFactory()

    def pluginName(self):
        return "example"

    def pluginDomainObject(self):
        name = self.pluginName()
        return self.registry.plugins[name]

    def testExists(self):
        self.failUnless(self.factory, "No factory was created.")

    def test_getAvailableNames(self):
        self.failUnless(self.pluginName() in self.factory.getAvailableNames())

    def test_getPlugin(self):
        plugin = self.factory.getPlugin(self.pluginDomainObject())
        self.failUnless(plugin, "No plugin produced by factory.")
        self.failUnlessEqual(plugin.domainObject, self.pluginDomainObject())

    def test_getPluginClass(self):
        self.failUnless(self.factory.getPluginClass(self.pluginName()))

    def testOnRun(self):
        plugin = self.factory.getPlugin(self.pluginDomainObject())
        countBefore = plugin.counts['onRun']
        val = plugin.onRun(None)
        countAfter = plugin.counts['onRun']
        self.failUnless(countBefore + 1 == countAfter)

