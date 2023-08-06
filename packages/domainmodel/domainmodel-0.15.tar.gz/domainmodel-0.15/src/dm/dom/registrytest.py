import unittest
from dm.dom.basetest import TestCase
from dm.dom.registry import RegistryPathGetter
from dm.dom.registry import ModelPath 
from dm.dom.base import DomainObject

def suite():
    suites = [
        unittest.makeSuite(TestSessionsPath),
        unittest.makeSuite(TestRolesPath),
        unittest.makeSuite(TestRolePath),
        unittest.makeSuite(TestProtectionObjectsPath),
        unittest.makeSuite(TestGrantsPath),
        unittest.makeSuite(TestRoleGrantsPath),
        unittest.makeSuite(TestRoleGrantPath1),
        unittest.makeSuite(TestRoleGrantPath2),
        unittest.makeSuite(TestRoleGrantPermissionPath1),
        unittest.makeSuite(TestRoleGrantPermissionActionPath1),
        unittest.makeSuite(TestRegistryPathGetter1),
        unittest.makeSuite(TestRegistryPathGetter2),
    ]
    return unittest.TestSuite(suites)


class ModelPathTestCase(TestCase):

    openIsDomainObject = False

    def setUp(self):
        try:
            del(self.registry.sessions['TestPath1'])
        except:
            pass
        try:
            del(self.registry.protectionObjects['TestPath1'])
        except:
            pass
        try:
            del(self.registry.sessions['TestPath1'])
        except:
            pass
        self.session1 = self.registry.sessions.create('TestPath1')
        self.protectionObject1 = self.registry.protectionObjects.create('TestPath1')
        self.role1 = self.registry.roles.create('TestPath1')
        self.path = ModelPath(self.registry)

    def tearDown(self):
        self.path = None
        self.role1.delete()
        self.protectionObject1.delete()
        self.session1.delete()

    def test_open(self):
        o = self.path.open(self.openPath)
        if self.openIsDomainObject:
            self.failUnless(isinstance(o, DomainObject))
            self.failUnlessEqual(o.meta.name, self.openTypeName)
        else:
            self.failUnlessEqual(o.typeName, self.openTypeName)


class TestSessionsPath(ModelPathTestCase):

    openPath = 'sessions'
    openTypeName = 'Session'


class TestRolesPath(ModelPathTestCase):

    openPath = 'roles'
    openTypeName = 'Role'


class TestProtectionObjectsPath(ModelPathTestCase):

    openPath = 'protectionObjects'
    openTypeName = 'ProtectionObject'


class TestGrantsPath(ModelPathTestCase):

    openPath = 'grants'
    openTypeName = 'Grant'


class TestRolePath(ModelPathTestCase):

    openIsDomainObject = True
    openPath = 'roles/Administrator'
    openTypeName = 'Role'


class TestRoleGrantsPath(ModelPathTestCase):

    openPath = 'roles/Administrator/grants'
    openTypeName = 'Grant'


class TestRoleGrantPath1(ModelPathTestCase):

    openIsDomainObject = True
    openPath = 'roles/Administrator/grants/1'
    openTypeName = 'Grant'


class TestRoleGrantPath2(ModelPathTestCase):

    openIsDomainObject = True
    openPath = 'roles/Administrator/grants/9'
    openTypeName = 'Grant'


class TestRoleGrantPermissionPath1(ModelPathTestCase):

    openIsDomainObject = True
    openPath = 'roles/Administrator/grants/9/permission'
    openTypeName = 'Permission'


class TestRoleGrantPermissionActionPath1(ModelPathTestCase):

    openIsDomainObject = True
    openPath = 'roles/Administrator/grants/24/permission/action/permissions/Person'
    openTypeName = 'Permission'




### Older way.

class TestRegistryPathGetter1(TestCase):

    def test_sessions(self):
        getter = RegistryPathGetter('sessions')
        register = getter.getRegister()
        self.failUnlessEqual(register.getDomainClass().meta.name, 'Session')


class TestRegistryPathGetter2(TestCase):

    def setUp(self):
        super(TestRegistryPathGetter2, self).setUp()
        people = self.registry.people
        self.person = people.create('TestRegistryAutocomplete')

    def tearDown(self):
        self.person.delete()
    
    def test_person_sessions(self):
        getter = RegistryPathGetter('people/%s/sessions'% (
            self.person.getRegisterKeyValue()
        ))
        register = getter.getRegister()
        self.failUnlessEqual(register.getDomainClass().meta.name, 'Session')


