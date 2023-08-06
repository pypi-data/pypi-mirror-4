import unittest
import dm.testunit
#import dm.webkit.settingstest

def suite():
    suites = [
        #dm.webkit.settingstest.suite(),
    ]
    return unittest.TestSuite(suites)

