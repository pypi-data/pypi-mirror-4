from dm.testunit import *
import dm.plugin.basetest
import dm.plugin.controllertest
import dm.plugin.factorytest
import unittest
import os


def suite():
    suites = [
        dm.plugin.basetest.suite(),
        dm.plugin.controllertest.suite(),
        dm.plugin.factorytest.suite(),
    ]
    return unittest.TestSuite(suites)

