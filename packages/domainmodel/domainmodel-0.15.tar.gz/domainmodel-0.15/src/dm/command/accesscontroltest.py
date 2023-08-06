import unittest
from dm.command.testunit import TestCase
from dm.command.accesscontrol import *
from dm.exceptions import *
from dm.strategy import FindProtectionObject

def suite():
    suites = [
        unittest.makeSuite(TestGrantAccess),
        unittest.makeSuite(TestRevokeAccess),
        unittest.makeSuite(TestGrantStandardSystemAccess),
    ]
    return unittest.TestSuite(suites)

class TestAccessControlCommand(TestCase):

    def setUp(self):
        super(TestAccessControlCommand, self).setUp()
        self.roleName = ''
        self.role = None
        self.actionName = ''
        self.action = None
        self.protectedObject = None

    def setRole(self, name):
        self.roleName = name
        self.role = self.registry.roles[name]

    def setAction(self, name):
        self.actionName = name
        self.action = self.registry.actions[name]

    def setProtectedObject(self, className, instanceName=''):
        domainClass = self.registry.getDomainClass(className)
        if instanceName:
            raise "Test method not implemented for instanceName argument."
        else:
            self.protectedObject = domainClass

    def findGrant(self):
        findObject = FindProtectionObject(self.protectedObject)
        protectionObject = findObject.find()
        permission = protectionObject.permissions[self.action]
        if permission in self.role.grants:
            self.grant = self.role.grants[permission]
        else:
            self.grant = None
        return self.grant

    def findBar(self):
        findObject = FindProtectionObject(self.protectedObject)
        protectionObject = findObject.find()
        permission = protectionObject.permissions[self.action]
        if permission in self.role.bars:
            self.bar = self.role.bars[permission]
        else:
            self.bar = None
        return self.bar

    def createGrant(self):
        findObject = FindProtectionObject(self.protectedObject)
        protectionObject = findObject.find()
        permission = protectionObject.permissions[self.action]
        self.role.grants.create(permission)

    def deleteGrant(self):
        grant = self.findGrant()
        if grant:
            grant.delete()
    

class TestGrantAccess(TestAccessControlCommand):

    def setUp(self):
        super(TestGrantAccess, self).setUp()
        self.setRole('Visitor')
        self.setAction('Purge')
        self.setProtectedObject('Person')

    def tearDown(self):
        self.deleteGrant()

    def test_execute(self):
        self.failIf(self.findGrant())
        cmd = GrantAccess(
            self.role, self.actionName, self.protectedObject
        )
        cmd.execute()
        self.failUnless(self.findGrant())


class TestRevokeAccess(TestAccessControlCommand):

    def setUp(self):
        super(TestRevokeAccess, self).setUp()
        self.setRole('Visitor')
        self.setAction('Purge')
        self.setProtectedObject('Person')
        self.createGrant()

    def tearDown(self):
        self.deleteGrant()
    
    def test_execute(self):
        self.failUnless(self.findGrant())
        cmd = RevokeAccess(
            self.role, self.actionName, self.protectedObject
        )
        cmd.execute()
        self.failIf(self.findGrant())


class TestGrantStandardSystemAccess(TestCase):

    def setUp(self):
        super(TestGrantStandardSystemAccess, self).setUp()
        protectedName = 'ARandomProtectionObject'
        try:
            self.pobj = self.registry.protectionObjects.create(protectedName)
        except:
            pobj = self.registry.protectionObjects[protectedName]
            pobj.delete()
            raise
        cmd = GrantStandardSystemAccess(self.pobj)
        cmd.execute()

    def tearDown(self):
        self.pobj.delete()

    def testPermissionsExist(self):
        for action in self.registry.actions:
            self.failUnless(action in self.pobj.permissions)

    def testGrantExist(self):
        action = self.registry.actions['Read']
        permission = self.pobj.permissions[action]
        role = self.registry.roles['Friend']
        self.failUnless(permission in role.grants)

