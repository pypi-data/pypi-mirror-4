import unittest
import dm.testunit
#import dm.pylons.settingstest

def suite():
    suites = [
        #dm.pylons.settingstest.suite(),
    ]
    return unittest.TestSuite(suites)

