import unittest
from dm.testunit import TestCase
from dm.ioc import *

def suite():
    "Return a TestSuite of dm.log TestCases."
    suites = [
        unittest.makeSuite(TestLogger),
    ]
    return unittest.TestSuite(suites)

class TestLogger(TestCase):
    "TestCase for the Logger class."

    log = RequiredFeature('Logger')

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testExists(self):
        self.failUnless(self.log, "Logger isn't there!")
    
    def testLogDebug(self):
        self.log.debug('Debug logging test. Please ignore this message.')
    
    def testLogInfo(self):
        self.log.info('Info logging test. Please ignore this message.')
    
    def testLogWarning(self):
        self.log.warning('Warning logging test. Please ignore this message.')

# Todo: Fixup not printing log to STDOUT during the tests.
#    def testLogError(self):
#        self.log.error('Error logging test. Please ignore this message.')
#    
#    def testLogCritical(self):
#        self.log.critical('Critical logging test. Please ignore this message.')

