import unittest
from dm.apache.config import ApacheConfigBuilder
from dm.testunit import TestCase

def suite():
    suites = [
        unittest.makeSuite(TestApacheConfigBuilder),
    ]
    return unittest.TestSuite(suites)


class TestApacheConfigBuilder(TestCase):

    def setUp(self):
        super(TestApacheConfigBuilder, self).setUp()
        self.builder = ApacheConfigBuilder()

    def tearDown(self):
        super(TestApacheConfigBuilder, self).tearDown()
        self.builder = None

    def testCreateConfigContent(self):
        self.assertTrue(self.builder.createConfigContent())

    def testCreateWsgiContent(self):
        self.assertTrue(self.builder.createWsgiScriptContent())

