from dm.dictionarywords import *
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestDictionaryWords),
    ]
    return unittest.TestSuite(suites)


class TestDictionaryWords(unittest.TestCase):

    def test_dictionarywords(self):
        self.failUnlessEqual(SYSTEM_NAME, 'system_name')
        self.failUnlessEqual(IMAGES_DIR_PATH, 'images_dir')

