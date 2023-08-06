from dm.application import Application
from dm.ioc import *
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestApplication),
    ]
    return unittest.TestSuite(suites)

class TestApplication(unittest.TestCase):

    def setUp(self):
        self.application = Application()

    def tearDown(self):
        self.application = None

    def test_exists(self):
        self.failUnless(self.application)

    def test_features(self):
        self.failUnless(self.application.commands)
        self.failUnless(self.application.dictionary)
        self.failUnless(self.application.registry)

