import unittest
from dm.dom.testunit import TestCase
import dm.dom.meta
from dm.util.datastructure import MultiValueDict
import datetime
from dm.dictionarywords import PASSWORD_DIGEST_SECRET

# todo: HasA
# todo: HasMany

def suite():
    suites = [
        unittest.makeSuite(TestString),
        unittest.makeSuite(TestText),
        unittest.makeSuite(TestMarkdownText),
        unittest.makeSuite(TestUrl),
        unittest.makeSuite(TestPassword),
        unittest.makeSuite(TestDateTime),
        unittest.makeSuite(TestDate),
        unittest.makeSuite(TestRDate),
        unittest.makeSuite(TestBoolean_True),
        unittest.makeSuite(TestBoolean_False),
        unittest.makeSuite(TestInteger_Zero),
        unittest.makeSuite(TestInteger_NonZero),
        unittest.makeSuite(TestInteger_Negative),
        unittest.makeSuite(TestFloat_Zero),
        unittest.makeSuite(TestFloat_NonZero),
        unittest.makeSuite(TestFloat_Negative),
        unittest.makeSuite(TestImageFile),
        unittest.makeSuite(TestHasA_Null),
        unittest.makeSuite(TestHasMany_Null),
    ]
    return unittest.TestSuite(suites)


class FakeDomainObject(object):
    pass


class MetaAttrTestCase(TestCase):

    fieldName = 'myTestField'

    def setUp(self):
        super(MetaAttrTestCase, self).setUp()
        self.field = self.createField()

    def createField(self):
        field = self.fieldClass() 
        field.name = self.fieldName
        return field

    def prepareMultiValueDict(self):
        multiValueDict = MultiValueDict()
        multiValueDict[self.fieldName] = self.htmlValue
        return multiValueDict

    def prepareFakeDomainObject(self):
        fakeDomainObject = FakeDomainObject()
        setattr(fakeDomainObject, self.fieldName, self.domValue)
        return fakeDomainObject
        
    def test_create(self):
        self.failUnless(self.field)
        self.failUnlessEqual(self.field.typeName, self.typeName)

    def test_isValueObject(self):
        self.failUnlessEqual(self.field.isValueObject(), self.isValueObject)
    
    def test_makeValueFromMultiValueDict(self):
        multiValueDict = self.prepareMultiValueDict()
        domValue = self.field.makeValueFromMultiValueDict(multiValueDict)
        self.failUnlessEqual(domValue, self.domValue)

    def test_createValueRepr(self):
        domainObject = self.prepareFakeDomainObject()
        htmlValue = self.field.createValueRepr(domainObject)
        self.failUnlessEqual(htmlValue, self.htmlRepr)

    def test_convertToDbValue(self):
        dbValue = self.field.convertToDbValue(self.domValue)
        self.failUnlessEqual(dbValue, self.dbValue)

    def test_convertFromDbValue(self):
        domValue = self.field.convertFromDbValue(self.dbValue)
        self.failUnlessEqual(domValue, self.domValue)


class TestString(MetaAttrTestCase):

    fieldClass = dm.dom.meta.String
    typeName = 'String'
    isValueObject = True
    htmlValue = 'My String'
    htmlRepr = 'My String'
    domValue = 'My String'
    dbValue = 'My String'
    

class TestText(MetaAttrTestCase):

    fieldClass = dm.dom.meta.Text
    typeName = 'Text'
    isValueObject = True
    htmlValue = 'My Text'
    htmlRepr = 'My Text'
    domValue = 'My Text'
    dbValue = 'My Text'
    

class TestMarkdownText(MetaAttrTestCase):

    fieldClass = dm.dom.meta.MarkdownText
    typeName = 'MarkdownText'
    isValueObject = True
    htmlValue = 'My Text'
    htmlRepr = 'My Text'
    domValue = 'My Text'
    dbValue = 'My Text'
    

class TestUrl(MetaAttrTestCase):

    fieldClass = dm.dom.meta.Url
    typeName = 'Url'
    isValueObject = True
    htmlValue = 'MyUrl'
    htmlRepr = 'MyUrl'
    domValue = 'MyUrl'
    dbValue = 'MyUrl'
    

from dm.messagedigest import *
from dm.dictionarywords import PASSWORD_DIGEST_SECRET
import random

class TestPassword(MetaAttrTestCase):

    fieldClass = dm.dom.meta.Password
    typeName = 'Password'
    isValueObject = True
    htmlValue = 'MyPassword'
    htmlRepr = ''
    domValue = hmac(key='abcdefgh', msg=md5(htmlValue).hexdigest(), digestmod=sha256).hexdigest()
    dbValue = domValue

    def setUp(self):
        super(TestPassword, self).setUp()
        self.origPasswordDigestSecret = TestCase.dictionary[PASSWORD_DIGEST_SECRET]
        TestCase.dictionary[PASSWORD_DIGEST_SECRET] = 'abcdefgh'

    def tearDown(self):
        TestCase.dictionary[PASSWORD_DIGEST_SECRET] = self.origPasswordDigestSecret 
        super(TestPassword, self).tearDown()

class TestDateTime(MetaAttrTestCase):
    
    fieldClass = dm.dom.meta.DateTime
    typeName = 'DateTime'
    isValueObject = True
    htmlValue = '2007-06-03 12:30:06'
    htmlRepr = '2007-06-03 12:30:06'
    domValue = datetime.datetime(2007, 6, 3, 12, 30, 6)
    dbValue = datetime.datetime(2007, 6, 3, 12, 30, 6)
    
    def test_convertor(self):
        self.failUnless(self.field.convertor)


class TestDate(MetaAttrTestCase):
    
    fieldClass = dm.dom.meta.Date
    typeName = 'Date'
    isValueObject = True
    htmlValue = '2007-06-03'
    htmlRepr = '2007-06-03'
    domValue = datetime.datetime(2007, 6, 3)
    dbValue = datetime.datetime(2007, 6, 3)
    
    def test_convertor(self):
        self.failUnless(self.field.convertor)


class TestRDate(MetaAttrTestCase):
    
    fieldClass = dm.dom.meta.RDate
    typeName = 'RDate'
    isValueObject = True
    htmlValue = '03-06-2007'
    htmlRepr = '03-06-2007'
    domValue = datetime.datetime(2007, 6, 3)
    dbValue = datetime.datetime(2007, 6, 3)
    
    def test_convertor(self):
        self.failUnless(self.field.convertor)


class TestBoolean_True(MetaAttrTestCase):
    
    fieldClass = dm.dom.meta.Boolean
    typeName = 'Boolean'
    isValueObject = True
    htmlValue = 'True'
    htmlRepr = 'on'
    domValue = True
    dbValue = True
    

class TestBoolean_False(MetaAttrTestCase):
    
    fieldClass = dm.dom.meta.Boolean
    typeName = 'Boolean'
    isValueObject = True
    htmlValue = 'False'
    htmlRepr = ''
    domValue = False
    dbValue = False


class TestInteger_Zero(MetaAttrTestCase):
    
    fieldClass = dm.dom.meta.Integer
    typeName = 'Integer'
    isValueObject = True
    htmlValue = '0'
    htmlRepr = 0
    domValue = 0
    dbValue = 0


class TestInteger_NonZero(MetaAttrTestCase):
    
    fieldClass = dm.dom.meta.Integer
    typeName = 'Integer'
    isValueObject = True
    htmlValue = '12'
    htmlRepr = 12
    domValue = 12
    dbValue = 12


class TestInteger_Negative(MetaAttrTestCase):
    
    fieldClass = dm.dom.meta.Integer
    typeName = 'Integer'
    isValueObject = True
    htmlValue = '-12'
    htmlRepr = -12
    domValue = -12
    dbValue = -12


class TestFloat_Zero(MetaAttrTestCase):
    
    fieldClass = dm.dom.meta.Float
    typeName = 'Float'
    isValueObject = True
    htmlValue = '0'
    htmlRepr = 0
    domValue = 0
    dbValue = 0


class TestFloat_NonZero(MetaAttrTestCase):
    
    fieldClass = dm.dom.meta.Float
    typeName = 'Float'
    isValueObject = True
    htmlValue = '12.1'
    htmlRepr = 12.1
    domValue = 12.1
    dbValue = 12.1


class TestFloat_Negative(MetaAttrTestCase):
    
    fieldClass = dm.dom.meta.Float
    typeName = 'Float'
    isValueObject = True
    htmlValue = '-12.1'
    htmlRepr = -12.1
    domValue = -12.1
    dbValue = -12.1


class TestImageFile(MetaAttrTestCase):

    fieldClass = dm.dom.meta.ImageFile
    typeName = 'ImageFile'
    isValueObject = False
    htmlValue = '++++++++++++++++++++++++++++'
    htmlRepr = '++++++++++++++++++++++++++++'
    domValue = '++++++++++++++++++++++++++++'

    def test_makeValueFromMultiValueDict(self):
        pass
    
    def test_convertToDbValue(self):
        pass

    def test_convertFromDbValue(self):
        pass

    # todo: test file system manipulations


class TestHasA_Null(MetaAttrTestCase):

    fieldClass = dm.dom.meta.HasA
    typeName = 'Person'
    isValueObject = False
    htmlValue = ''
    htmlRepr = None
    domValue = None
    dbValue = None

    def createField(self):
        field = self.fieldClass('Person') 
        field.name = self.fieldName
        return field


class TestHasMany_Null(MetaAttrTestCase):
    
    fieldClass = dm.dom.meta.HasMany
    typeName = 'Person'
    isValueObject = False
    htmlValue = ''
    htmlRepr = []
    domValue = None
    dbValue = None

    def createField(self):
        field = self.fieldClass('Person', 'id') 
        field.name = self.fieldName
        return field

    def test_makeValueFromMultiValueDict(self):
        # HasMany is valueless.
        pass

    def test_createValueRepr(self):
        # Fake object has no association register (so there's an exception).
        pass

