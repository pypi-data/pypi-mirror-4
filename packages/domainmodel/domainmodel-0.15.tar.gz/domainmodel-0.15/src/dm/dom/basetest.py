import unittest
from dm.dom.testunit import TestCase
import dm.dom.base

def suite():
    suites = [
        unittest.makeSuite(TestDomainObject),
        unittest.makeSuite(TestDomainObjectRegister),
    ]
    return unittest.TestSuite(suites)


class TestDomainObject(TestCase):
    
    def setUp(self):
        super(TestDomainObject, self).setUp()
        self.object = dm.dom.base.DomainObject() 
    
    def test_create(self):
        self.failUnless(self.object)
        self.failUnless(self.object.meta)


class TestDomainObjectRegister(TestCase):
    
    def setUp(self):
        super(TestDomainObjectRegister, self).setUp()
        self.register = dm.dom.base.DomainObjectRegister() 
    
    def test_create(self):
        self.failUnless(self.register)
        self.failUnless(self.register.typeName)


