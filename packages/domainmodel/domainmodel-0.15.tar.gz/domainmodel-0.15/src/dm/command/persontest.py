import unittest
from dm.command.testunit import TestCase
from dm.command.person import *
from dm.exceptions import *

def suite():
    suites = [
        unittest.makeSuite(TestPersonCreate),
    #    unittest.makeSuite(TestPersonRead),
    #    unittest.makeSuite(TestPersonDelete),
    #    unittest.makeSuite(TestPersonUndelete),
    #    unittest.makeSuite(TestPersonPurge),
    #    unittest.makeSuite(TestPersonList),
    #    unittest.makeSuite(PersonAuthenticateTest),
    ]
    return unittest.TestSuite(suites)


class TestPersonCreate(TestCase):
    "TestCase for the PersonCreate command."

    fixtureName = 'TestPersonCreate'

    def setUp(self):
        super(TestPersonCreate, self).setUp()
        self.command = PersonCreate(self.fixtureName)

    def tearDown(self):
        try:
            person = self.registry.people.getAll()[self.fixtureName]
            person.delete()
            person.purge()
        except:
            pass

    def testExecute(self):
        self.failIf(self.fixtureName in self.registry.people)
        self.command.execute()
        self.failUnless(self.fixtureName in self.registry.people)

    def testErrorPersonExists(self):
        self.command.execute()
        self.failUnlessRaises(KforgeCommandError, self.command.execute)


class TestPersonDelete(TestCase):
    "TestCase for the PersonDelete command."

    def setUp(self):
        super(TestPersonDelete, self).setUp()
        self.fixtureName = 'TestPersonDelete'
        try:
            self.person = self.registry.people.create(self.fixtureName)
        except:
            person = self.registry.people.getAll()[self.fixtureName]
            person.delete()
            person.purge()
            raise
        self.command = PersonDelete(self.fixtureName)

    def tearDown(self):
        try:
            person = self.registry.people.getAll()[self.fixtureName]
            person.delete()
            person.purge()
        except:
            pass

    def testExecute(self):
        self.failUnless(self.fixtureName in self.registry.people)
        self.command.execute()
        self.failIf(self.fixtureName in self.registry.people)

    def testErrorNoPerson(self):
        self.command.execute()
        self.failUnlessRaises(KforgeCommandError, self.command.execute)


class TestPersonUndelete(TestCase):
    "TestCase for the PersonUndelete command."

    def setUp(self):
        super(TestPersonUndelete, self).setUp()
        self.fixtureName = 'TestPersonUndelete'
        try:
            self.person = self.registry.people.create(self.fixtureName)
            self.person.delete()
        except:
            person = self.registry.people.getAll()[self.fixtureName]
            person.delete()
            person.purge()
            raise
        self.command = PersonUndelete(self.fixtureName)

    def tearDown(self):
        try:
            person = self.registry.people.getAll()[self.fixtureName]
            person.delete()
            person.purge()
        except:
            pass
        self.command = None

    def testExecute(self):
        self.failUnless(self.fixtureName in self.registry.people.getDeleted())
        self.command.execute()
        self.failIf(self.fixtureName in self.registry.people.getDeleted())
        self.failUnless(self.fixtureName in self.registry.people)

    def testErrorNoPerson(self):
        self.command.execute()
        self.failUnlessRaises(KforgeCommandError, self.command.execute)


class TestPersonPurge(TestCase):
    "TestCase for the PersonPurge command."

    def setUp(self):
        super(TestPersonPurge, self).setUp()
        self.fixtureName = 'TestPersonPurge'
        try:
            self.person = self.registry.people.create(self.fixtureName)
            self.person.delete()
        except:
            person = self.registry.people.getAll()[self.fixtureName]
            person.delete()
            person.purge()
            raise
        self.command = PersonPurge(self.fixtureName)

    def tearDown(self):
        try:
            person = self.registry.people.getAll()[self.fixtureName]
            person.delete()
            person.purge()
        except:
            pass
        self.command = None

    def testExecute(self):
        self.failUnless(self.fixtureName in self.registry.people.getDeleted())
        self.command.execute()
        self.failIf(self.fixtureName in self.registry.people.getDeleted())
        self.failIf(self.fixtureName in self.registry.people)
        self.failIf(self.fixtureName in self.registry.people.getAll())

    def testErrorNoPerson(self):
        self.command.execute()
        self.failUnlessRaises(KforgeCommandError, self.command.execute)


class TestPersonRead(TestCase):
    "TestCase for the PersonRead command."

    personName = 'TestPersonRead'

    def setUp(self):
        super(TestPersonRead, self).setUp()
        try:
            self.person = self.registry.people.create(self.personName)
        except:
            person = self.registry.people.getAll()[self.personName]
            person.delete()
            person.purge()
            raise
        self.command = PersonRead(self.personName)

    def tearDown(self):
        try:
            person = self.registry.people.getAll()[self.personName]
            person.delete()
            person.purge()
        except:
            pass

    def testExecute(self):
        self.command.execute()
        self.failUnless(self.command.person)
        self.assertEquals(self.command.person.name, self.personName)


class TestPersonList(TestCase):
    "TestCase for the PersonList command."

    personName = 'TestPersonList'

    def setUp(self):
        super(TestPersonList, self).setUp()
        try:
            self.person = self.registry.people.create(self.personName)
        except:
            person = self.registry.people.getAll()[self.personName]
            person.delete()
            person.purge()
        self.command = dm.command.person.PersonList()

    def tearDown(self):
        try:
            person = self.registry.people.getAll()[self.personName]
            person.delete()
            person.purge()
        except:
            pass

    def testExecute(self):
        self.command.execute()
        self.command.people[self.personName]


class PersonAuthenticateTest(TestCase):
    
    def testAuthenticate(self):
        command = PersonAuthenticate('levin','levin')
        command.execute()
    
    def testPasswordError(self):
        command = PersonAuthenticate('levin','middlename')
        self.failUnlessRaises(KforgeCommandError, command.execute)
    
    def testNameError(self):
        command = PersonAuthenticate('notlevin','levin')
        self.failUnlessRaises(KforgeCommandError, command.execute)

