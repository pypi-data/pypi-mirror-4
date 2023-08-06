import unittest
from dm.dom.testunit import TestCase
import dm.dom.person
from dm.exceptions import *

def suite():
    suites = [
        unittest.makeSuite(TestPlugin),
    ]
    return unittest.TestSuite(suites)

class TestPlugin(TestCase):
    "TestCase for the Plugin class."

    def setUp(self):
        super(TestPlugin, self).setUp()
        self.fixtureName = 'TestPlugin'
        self.plugin = self.registry.plugins['example']

    def test_getChoices(self):
        pluginClass = self.registry.getDomainClass('Plugin')
        self.failUnless(pluginClass)
        self.failUnless(pluginClass.name)
        self.failUnless(pluginClass.name.getChoices)
        pluginChoices = pluginClass.name.getChoices()
        self.failUnless(pluginChoices)
        self.failUnless(('example', 'example') in pluginChoices)

