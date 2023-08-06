import unittest
from dm.testunit import *
import dm.debug

def suite():
    suites = [
        unittest.makeSuite(TestDebug),
    ]
    return unittest.TestSuite(suites)

class TestDebug(TestCase):
    "TestCase for the Debug class."

    debug = dm.debug.Debug().isDebug()

    def setUp(self):
        super(TestDebug, self).setUp()

    def test_debug(self):
        self.debug

