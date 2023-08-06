import unittest
from dm.configwriter import ConfigWriter

def suite():
    suites = [
        unittest.makeSuite(TestConfigWriterNull),
        unittest.makeSuite(TestConfigWriterValueSubst),
        unittest.makeSuite(TestConfigWriterValueSubstUncomment),
        unittest.makeSuite(TestConfigWriterNoChange),
        unittest.makeSuite(TestConfigWriterAppendValue),
        unittest.makeSuite(TestConfigWriterAppendSection),
    ]
    return unittest.TestSuite(suites)


class ConfigWriterTestCase(unittest.TestCase):

    def setUp(self):
        self.configWriter = ConfigWriter()

    def test(self):
        self.configWriter.updateLines(self.configLines, self.updateLines)
        self.failUnlessEqual(
            self.configWriter.newLines,
            self.expectedLines,
            "\n%s\nNot equal to:\n%s\n%s\n%s" % (
                "".join(self.configWriter.newLines), 
                "".join(self.expectedLines), 
                self.configWriter.newLines,
                self.expectedLines
            )
        )


class TestConfigWriterNull(ConfigWriterTestCase):
    configLines = []
    updateLines = []
    expectedLines = []

class TestConfigWriterNoChange(ConfigWriterTestCase):
    configLines = ["#Some comment","[DEFAULT]","name1 = value1","","[section1]","name1 = value2"]
    updateLines = []
    expectedLines = ["#Some comment\n","[DEFAULT]\n","name1 = value1\n","\n","[section1]\n","name1 = value2\n"]

class TestConfigWriterValueSubst(ConfigWriterTestCase):
    configLines = ["[DEFAULT]","name1=value1","","[section1]","name1= value2"]
    updateLines = ["[DEFAULT]","name1=value3","[section1]","name1=value4"]
    expectedLines = ["[DEFAULT]\n","name1 = value3\n","\n","[section1]\n","name1 = value4\n"]

class TestConfigWriterValueSubstUncomment(ConfigWriterTestCase):
    configLines = ["[DEFAULT]","#Some general comment.","#name1=value1","","[section1]","#name1= value2"]
    updateLines = ["[DEFAULT]","name1=value3","[section1]","name1=value4"]
    expectedLines = ["[DEFAULT]\n","#Some general comment.\n","name1 = value3\n","\n","[section1]\n","name1 = value4\n"]

class TestConfigWriterAppendValue(ConfigWriterTestCase):
    configLines = ["[DEFAULT]","name1 =value1","","[section1]","name1= value2"]
    updateLines = ["[DEFAULT]","name2=value3","[section1]","name2=value4"]
    expectedLines = ["[DEFAULT]\n","name1 = value1\n","name2 = value3\n","\n","[section1]\n","name1 = value2\n","name2 = value4\n"]

class TestConfigWriterAppendSection(ConfigWriterTestCase):
    configLines = ["[DEFAULT]","name1 =value1","","[section1]","name1= value2"]
    updateLines = ["[DEFAULT]","[section2]","name1=value3","name2=value4"]
    expectedLines = ["[DEFAULT]\n","name1 = value1\n","\n","[section1]\n","name1 = value2\n","\n","[section2]\n","name1 = value3\n","name2 = value4\n"]
