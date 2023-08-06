import unittest
from dm.dom.testunit import TestCase
from dm.dom.pickers import GetReadableAttributes
from dm.dom.pickers import GetEditableAttributes
from dm.exceptions import *

def suite():
    suites = [
        unittest.makeSuite(TestGetReadableAttributes),
        unittest.makeSuite(TestGetEditableAttributes),
    ]
    return unittest.TestSuite(suites)

class ModelPickerTestCase(TestCase):

    domainClassName = None
    pickerClassName = None
    expectedAttributeNames = []

    def test_picker(self):
        domainClass = self.registry.getDomainClass(self.domainClassName)
        picker = self.pickerClassName(domainClass.meta)
        attributeNames = [a.name for a in picker.pick()]
        self.failUnlessEqual(attributeNames, self.expectedAttributeNames)


class TestGetReadableAttributes(ModelPickerTestCase):
    
    domainClassName = 'Person'
    pickerClassName = GetReadableAttributes
    expectedAttributeNames = [
        'dateCreated',
        'emailAddresses',
        'fullname',
        'lastModified',
        'name',
        'password',
        'role',
    ]

class TestGetEditableAttributes(ModelPickerTestCase):
    
    domainClassName = 'Person'
    pickerClassName = GetEditableAttributes
    expectedAttributeNames = ['fullname', 'password']

        
