"""
Module of extensions to the unittest suite.

(This module wanted to be called dm.unittest but that breaks "import unittest".)

"""

import unittest
from dm.ioc import *
from dm.dom.builder import ModelBuilder
from dm.builder import ApplicationBuilder
from dm.application import Application
from dm.dictionary import SystemDictionary
from dm.dictionarywords import WEBKIT_NAME


class SystemModeError(Exception):
    pass


class DevModelBuilder(ModelBuilder):

    def construct(self):
        super(DevModelBuilder, self).construct()
        self.loadTemporal()

    def loadTemporal(self):
        from dm.dom.temporaltest import Temporal
        from dm.dom.temporaltest import TemporalObjectExampleGrant
        from dm.dom.temporaltest import TemporalObjectExample
        from dm.dom.temporal import TemporalProperty, BitemporalProperty, BitemporalActual
        self.registry.registerDomainClass(Temporal)
        self.registry.registerDomainClass(TemporalObjectExampleGrant)
        self.registry.registerDomainClass(TemporalObjectExample)
        self.registry.temporals = Temporal.createRegister()
        self.registry.registerDomainClass(TemporalProperty)
        self.registry.registerDomainClass(BitemporalProperty)
        self.registry.registerDomainClass(BitemporalActual)


class DevSystemDictionary(SystemDictionary):

    def setDefaultWords(self):
        super(DevSystemDictionary, self).setDefaultWords()
        #self[WEBKIT_NAME] = 'pylons'


class DevApplicationBuilder(ApplicationBuilder):

    def findModelBuilder(self):
        return DevModelBuilder()

    def findSystemDictionary(self):
        return DevSystemDictionary()


class DevApplication(Application):

    builderClass = DevApplicationBuilder


class ApplicationTestSuite(unittest.TestSuite):

    #appBuilderClass = DevApplicationBuilder

    def assertDevMode(self):
        dictionary = RequiredFeature('SystemDictionary')
        if dictionary != None:
            currentSystem = registry.systems.getSortedList()[-1]
            requiredSystemModeName = 'development'
            if currentSystem.mode != requiredSystemModeName:
                configFilePath = dictionary.environment.getConfigFilePath()
                raise SystemModeError("The system was built in '%s' mode. The system must be built in '%s' mode for the test suite to be run. Please check the 'system_mode' setting in your configuration file '%s' and rebuild the database." % (currentSystem.mode, requiredSystemModeName, configFilePath))

    assertDevMode = classmethod(assertDevMode)
 

class TestCase(unittest.TestCase):

    dictionary = RequiredFeature('SystemDictionary')
    registry = RequiredFeature('DomainRegistry')
    accessController = RequiredFeature('AccessController')

    def __init__(self, *args, **kwds):
        super(TestCase, self).__init__(*args, **kwds)

