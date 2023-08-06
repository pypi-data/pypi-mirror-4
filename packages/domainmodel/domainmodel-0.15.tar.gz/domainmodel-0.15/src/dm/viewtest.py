import unittest
import dm.view.manipulatortest
import dm.view.basetest
import dm.view.admintest
import dm.view.registrytest
import dm.view.rpctest
import dm.view.apitest

def suite():
    suites = [
        dm.view.manipulatortest.suite(),
        dm.view.basetest.suite(),
        dm.view.admintest.suite(),
        dm.view.registrytest.suite(),
        dm.view.rpctest.suite(),
        dm.view.apitest.suite(),
    ]
    return unittest.TestSuite(suites)

