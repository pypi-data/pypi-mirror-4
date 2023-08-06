import dm.filesystem
import unittest
from dm.testunit import TestCase

def suite():
    suites = [
        unittest.makeSuite(FileSystemPathBuilderTest),
    ]
    return unittest.TestSuite(suites)

class FileSystemPathBuilderTest(TestCase):
    
    def setUp(self):
        super(FileSystemPathBuilderTest, self).setUp()
        self.builder = dm.filesystem.FileSystemPathBuilder()
    
    def testGetPluginPath(self):
        plugin = self.registry.plugins['example']
        result = self.builder.getPluginPath(plugin)
        self.failUnless(plugin.name in result)
