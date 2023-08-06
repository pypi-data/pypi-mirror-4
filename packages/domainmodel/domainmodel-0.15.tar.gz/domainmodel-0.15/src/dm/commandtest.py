import unittest
from dm.testunit import TestCase
import dm.command
import dm.command.statetest
#import dm.command.permissiontest
import dm.command.persontest
import dm.command.plugintest
import dm.command.accesscontroltest
import dm.command.emailpasswordtest
from dm.exceptions import *

def suite():
    suites = [
        unittest.makeSuite(TestCommand),
        unittest.makeSuite(TestMacroCommand),
        dm.command.statetest.suite(),
        #dm.command.permissiontest.suite(),
        dm.command.persontest.suite(),
        dm.command.plugintest.suite(),
        dm.command.accesscontroltest.suite(),
        dm.command.emailpasswordtest.suite(),
    ]
    return unittest.TestSuite(suites)

class TestCommand(TestCase):
    "TestCase for the Command class."

    def setUp(self):
        super(TestCommand, self).setUp()
        self.command = dm.command.Command()

    def tearDown(self):
        self.command = None

    def testExecute(self):
        self.command.execute()

    def testError(self):
        msg = "Error!"
        self.failUnlessRaises(KforgeCommandError, self.command.raiseError, msg)
        try:
            self.command.raiseError(msg)
        except Exception, inst:
            errorMsg = str(inst)
            self.assertEquals(msg, errorMsg, "Wrong message: %s" % errorMsg)

class TestMacroCommand(TestCase):
    "TestCase for the command class."

    def setUp(self):
        super(TestMacroCommand, self).setUp()
        self.command = dm.command.MacroCommand()

    def tearDown(self):
        self.command = None

    def testExecute(self):
        self.command.execute()

# todo: Add tests for DomainObjectCommands.
