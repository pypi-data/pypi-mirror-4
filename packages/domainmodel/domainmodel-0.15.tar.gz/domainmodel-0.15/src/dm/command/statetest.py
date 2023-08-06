import unittest
from dm.command.testunit import TestCase
from dm.command.state import *
from dm.exceptions import *

def suite():
    suites = [
        unittest.makeSuite(TestStateCreate),
    ]
    return unittest.TestSuite(suites)

class TestStateCreate(TestCase):
    "TestCase for the StateCreate command."

    stateName = 'TestStateCreate'

    def findPluginController(self):
        return None

    def setUp(self):
        super(TestStateCreate, self).setUp()
        self.command = StateCreate(self.stateName)

    def tearDown(self):
        if self.stateName in self.registry.states:
            state = self.registry.states[self.stateName]
            state.delete()

    def testExecute(self):
        self.failIf(self.stateName in self.registry.states)
        self.command.execute()
        self.failUnless(self.stateName in self.registry.states)

    def testErrorProjectExists(self):
        self.command.execute()
        self.failUnlessRaises(KforgeCommandError, self.command.execute)

