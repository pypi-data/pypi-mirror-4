import unittest
import dm.times
import dm.dictionary
from dm.dictionarywords import *
import os
from dm.exceptions import FilePermissionError
import tempfile

def suite():
    suites = [
        unittest.makeSuite(TestSystemDictionary),
    ]
    return unittest.TestSuite(suites)


class TestSystemDictionary(unittest.TestCase):

    def setUp(self):
        self.dictionary = dm.dictionary.SystemDictionary()

    def test_systemName(self):
        self.failUnlessEqual(self.dictionary[SYSTEM_NAME], 'domainmodel')
        if self.dictionary[IMAGES_DIR_PATH]:
            imagesPath = self.dictionary[IMAGES_DIR_PATH]
            self.failUnless(os.path.exists(imagesPath), imagesPath)

    def test_systemUserName(self):
        self.failUnlessEqual(self.dictionary[SYSTEM_USER_NAME], os.environ['USER'])

    def test_systemUpSince(self):
        upSince = self.dictionary[SYSTEM_STARTED]
        self.failUnless(upSince)
        self.failUnless(upSince < dm.times.getUniversalNow())

    def test_assertConfigFilePermissions(self):
        try:
            self.dictionary.assertConfigFilePermissions()
            notokay = [
                0641, 0642, 0643, 0644, 0645, 0646, 0647, 
                0600, 0610, 0620, 0630, 0650, 0660, 0670,
                0140, 0240, 0340, 0540, 0740,
            ]
            for code in notokay:
                os.chmod(self.dictionary.configFilePath, code)
                try:
                    self.dictionary.assertConfigFilePermissions()
                except FilePermissionError:
                    pass
                else:
                    self.fail("Permissions 0o%o didn't raise exception." % code)
            os.chmod(self.dictionary.configFilePath, 0440)
            os.chmod(self.dictionary.configFilePath, 0640)
            self.dictionary.assertConfigFilePermissions()
        finally:
            os.chmod(self.dictionary.configFilePath, 0640)

