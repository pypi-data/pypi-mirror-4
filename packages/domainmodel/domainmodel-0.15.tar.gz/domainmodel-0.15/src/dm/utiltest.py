import unittest
import dm.util.passwordtest
import dm.util.mailertest

def suite():
    suites = [
        dm.util.passwordtest.suite(),
        dm.util.mailertest.suite(),
    ]
    return unittest.TestSuite(suites)

