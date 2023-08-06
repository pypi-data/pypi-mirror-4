import unittest
from dm.testunit import ApplicationTestSuite

ApplicationTestSuite.buildApplication()

def run(suiteName=""):
    if not suiteName:
        import dm.test
        suite = dm.test.suite()
    else:
        suite = __import__(suiteName,'','','*').suite()
    unittest.TextTestRunner().run(suite)

