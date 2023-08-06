import unittest
import dm.accesscontrol
from dm.testunit import TestCase
from dm.exceptions import *

# Todo: Test for permissions set on a person's grants and bars.

def suite():
    suites = [
        unittest.makeSuite(TestSystemAccessController),
    ]
    return unittest.TestSuite(suites)

class TestSystemAccessController(TestCase):
    
    def setUp(self):
        super(TestSystemAccessController, self).setUp()
        self.ac = dm.accesscontrol.SystemAccessController()
        self.person = None
        self.actionName = ''
        self.protectedObject = None
    
    def tearDown(self):
        self.ac = None

    def failIfAccessAuthorised(self):
        self.failIf(self.isAccessAuthorised())

    def failUnlessAccessAuthorised(self):
        self.failUnless(self.isAccessAuthorised())

    def isAccessAuthorised(self):
        return self.ac.isAccessAuthorised(
            person=self.person, 
            actionName=self.actionName, 
            protectedObject=self.protectedObject, 
        )
        
    def test_setUp(self):
        self.failUnless(self.ac)

    def test_isAccessAuthorised_nothing(self):
        self.failIfAccessAuthorised()

    def test_isAccessAuthorised_without_actionName_or_object(self):
        self.person = self.registry.people['levin']
        self.failIfAccessAuthorised()

    def test_isAccessAuthorised_without_object(self):
        self.person = self.registry.people['levin']
        self.actionName = 'Create'
        self.failIfAccessAuthorised()

    def test_no_isAccessAuthorised_delete_person(self):
        self.person = self.registry.people['levin']
        self.actionName = 'Delete'
        self.protectedObject = self.registry.getDomainClass('Person')
        self.failIfAccessAuthorised()

    def test_isAccessAuthorised_read_person(self):
        self.person = self.registry.people['levin']
        self.actionName = 'Read'
        self.protectedObject = self.registry.getDomainClass('Person')
        oldRole = self.person.role
        self.person.role = self.registry.roles['Administrator']
        self.failUnlessAccessAuthorised()
        self.person.role = oldRole

    def test_isAccessAuthorised_visitor_create_person(self):
        self.person = self.registry.people['visitor']
        self.actionName = 'Create'
        self.protectedObject = self.registry.getDomainClass('Person')
        self.failUnlessAccessAuthorised()

