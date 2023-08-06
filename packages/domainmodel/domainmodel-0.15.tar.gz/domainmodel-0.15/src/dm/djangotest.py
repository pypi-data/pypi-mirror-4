import unittest
import dm.testunit
import dm.django.settingstest

def suite():
    suites = [
        dm.django.settingstest.suite(),
    ]
    return unittest.TestSuite(suites)

