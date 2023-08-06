import unittest
import random
from dm.dom.testunit import TestCase


def suite():
    suites = [
        unittest.makeSuite(TestProtectionObject),
        unittest.makeSuite(TestPermission),
        unittest.makeSuite(TestRole),
    ]
    return unittest.TestSuite(suites)


class TestProtectionObject(TestCase):
    
    def setUp(self):
        super(TestProtectionObject, self).setUp()
        self.protectionObjects = self.registry.protectionObjects
    
    def test_create(self):
        protectedName = 'TestProtectionObject'
        try:
            self.protectionObjects.create(protectedName)
        except:
            protectedObject = self.protectionObjects[protectedName]
            protectedObject.delete()
            
        self.failUnless(self.protectionObjects[protectedName])
        self.protectionObjects[protectedName].delete()
        

class TestPermission(TestCase):
    
    def setUp(self):
        super(TestPermission, self).setUp()
        protectionObjects = self.registry.protectionObjects
        self.protectedName = 'TestPermission' + str(random.randint(1, 10000))
        self.protectionObject = protectionObjects.create(self.protectedName)
    
    def tearDown(self):
        self.protectionObject.delete()
    
    def test_composition(self):
        readAction = self.registry.actions['Read']
        self.protectionObject.permissions[readAction]
        

class TestRole(TestCase):
    
    def setUp(self):
        super(TestRole, self).setUp()
        protectionObjects = self.registry.protectionObjects
        self.protectedName = 'TestRole' + str(random.randint(1, 10000))
        self.protectionObject = protectionObjects.create(self.protectedName)
        self.action = self.registry.actions['Read']
        self.permission = self.protectionObject.permissions[self.action]
    
    def tearDown(self):
        self.protectionObject.delete()
        
    def test_create(self):
        testRoleName = 'TestRole'
        self.registry.roles.create(testRoleName)
        self.failUnless(self.registry.roles[testRoleName])
        self.registry.roles[testRoleName].delete()
    
    def test_grant(self):
        role = self.registry.roles['Developer']
        role.grants.create(self.permission)
        self.failUnless(self.permission in role.grants)
        self.failUnless(role.hasPermission(self.permission))
        self.protectionObject.delete()
        self.failIf(role.hasPermission(self.permission))

