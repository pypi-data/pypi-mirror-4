import unittest
from dm.command.testunit import TestCase

from dm.command.emailpassword import EmailNewPassword
from dm.exceptions import *

def suite():
    suites = [
        unittest.makeSuite(TestEmailNewPassword),
    ]
    return unittest.TestSuite(suites)

# todo: Write customer test for integration with SMTP server.

class MockEmailNewPassword(EmailNewPassword):

    def dispatchEmailMessage(self, msgFrom, msgTo, msgSubject, msgBody):
        self.dispatchedMessage = {}
        self.dispatchedMessage['from'] = msgFrom
        self.dispatchedMessage['to'] = msgTo
        self.dispatchedMessage['subject'] = msgSubject
        self.dispatchedMessage['body'] = msgBody
        self.isDispatchedOK = True


class TestEmailNewPassword(TestCase):

    def setUp(self):
        self.person = self.registry.people['levin']
        self.oldPassword = self.person.name
        self.cmd = MockEmailNewPassword(self.person)

    def tearDown(self):
        self.person.setPassword(self.oldPassword)
        self.person.save()

    def testExecute(self):
        self.cmd.execute()
        self.failIf(self.person.isPassword(self.oldPassword))
        data = self.cmd.dispatchedMessage
        self.failUnless(data['from'], data)
        self.failUnless(data['to'], data)
        self.failUnless(data['subject'], data)
        self.failUnless(data['body'], data)

