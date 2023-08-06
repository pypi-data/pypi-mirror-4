import unittest
import dm.apache.configtest

def suite():
    suites = [
        dm.apache.configtest.suite()
    ]
    return unittest.TestSuite(suites)

