import unittest
import StringIO
from dm.config import ConfigFileReader

def suite():
    suites = [
        unittest.makeSuite(TestConfigFileReader),
    ]
    return unittest.TestSuite(suites)


class TestConfigFileReader(unittest.TestCase):
    
    configText = """[DEFAULT]
var_1: var1
var_2: var2/var1
# core stuff
[core]
var_2 = var2
var_3: /var3/%(var_1)s
"""

    def setUp(self):
        configFile1 = StringIO.StringIO(self.configText)
        self.reader = ConfigFileReader()
        self.reader.readfp(configFile1)
        self.expectedDictionary = {
            'var_1'     : 'var1',
            'var_2'     : 'var2/var1',
            'core.var_1': 'var1',
            'core.var_2': 'var2',
            'core.var_3': '/var3/var1',
        }
    
    def test_convertKey(self):
        keyname = 'sect1.optionA'
        exp = ('sect1', 'optionA')
        out = self.reader.convertKey(keyname)
        self.assertEqual(exp, out)

    def test___set_item__(self):
        keyname = 'newsection.abc'
        value = 'xyz'
        self.reader[keyname] = value
        self.assertEqual(value, self.reader[keyname])

    def test_as_dictionary(self):
        config = self.reader
        for word in self.expectedDictionary.keys():
            configWord = config[word]
            expectedWord = self.expectedDictionary[word]
            self.assertEquals(configWord, expectedWord)

    def test_has_key(self):
        key1 = 'var_1'
        key2 = 'core.var_2'
        key3 = 'core.xyz'
        key4 = 'nonexistent.blah'
        self.failUnless(self.reader.has_key(key1))
        self.failUnless(self.reader.has_key(key2))
        self.failIf(self.reader.has_key(key3))
        self.failIf(self.reader.has_key(key4))

    def test_keys(self):
        out = self.reader.keys()
        exp = ['var_2', 'var_1', 'core.var_3', 'core.var_2', 'core.var_1' ]
        out.sort()
        exp.sort()
        self.assertEqual(exp, out)

