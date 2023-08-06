# -*- coding=utf-8 -*-
from dm.testunit import TestCase
from dm.db import ConnectionFacade, DatabaseFacade
from dm.exceptions import *
import unittest

def suite():
    "Return a TestSuite of dm.db TestCases."
    suites = [
        unittest.makeSuite(TestConnectionFacade),
        unittest.makeSuite(TestDatabaseFacade),
        unittest.makeSuite(TestConnection),
        # todo: replace these tests with tests for the abstracted
        unittest.makeSuite(TestImage),
        unittest.makeSuite(TestPerson),
        unittest.makeSuite(TestTransaction),
        #unittest.makeSuite(TestProject),
        #unittest.makeSuite(TestService),
        #unittest.makeSuite(TestMember),
    ]
    return unittest.TestSuite(suites)

class TestConnectionFacade(TestCase):
    "TestCase for the ConnectionFacade class."
    
    def setUp(self):
        super(TestConnectionFacade, self).setUp()
        self.Connection = ConnectionFacade()

    def testConnection(self):
        self.failUnless(self.Connection, "No ConnectionFacade object.")
    
    def testGetConnection(self):
        self.failUnless(self.Connection.getConnection(), "No (db) connection")
    
class TestDatabaseFacade(TestCase):
    "TestCase for the ConnectionFacade class."
    
    def setUp(self):
        super(TestDatabaseFacade, self).setUp()
        self.database = DatabaseFacade()

    def testDatabase(self):
        self.failUnless(self.database, "No database interface.")

    def testConnection(self):
        self.failUnless(self.database.connection, "No connection interface.")

    def testPerson(self):
        person = self.database.createRecord('Person', name='TestDatabaseFacade', stateID=1, roleID=1)
        try:
            self.failUnless(person, "No person created.")
            self.failUnless(self.database.findRecord('Person', name='TestDatabaseFacade'), "No person found.")
        finally:
            person.destroySelf()

class TestConnection(TestCase):
    "TestCase for the Connection class."
    
    def setUp(self):
        super(TestConnection, self).setUp()
        self.Connection = ConnectionFacade()

    def testConnection(self):
        if not self.Connection:
            raise "No connection interface."
    
class TestImage(TestCase):
    "TestCase for the Image record."
    
    def setUp(self):
        super(TestImage, self).setUp()
        self.database = DatabaseFacade()
        self.image = self.database.createRecord('Image', stateID=2)
        self.imageId = self.image.id

    def tearDown(self):
        if self.image:
            self.image.destroySelf()

    def test_create(self):
        self.failUnless(self.image, "New record could not be created.")
        self.database.createRecord('Image', stateID=2)
        self.database.createRecord('Image', stateID=2)
        self.database.createRecord('Image', stateID=2)

    def test_find(self):
        self.failUnless(self.database.findRecord('Image', id=self.imageId), "Image could not be selected.")
        self.failUnlessRaises(DbObjectNotFound, self.database.findRecord, 'Image', id=666666666666)
        self.failUnlessRaises(DbObjectNotFound, self.database.findRecord, 'Image', id=666666666666)

    def test_destroySelf(self):
        imageId = self.image.id
        self.database.findRecord('Image', id=imageId)
        self.image.destroySelf()
        self.image = None
        self.failUnlessRaises(DbObjectNotFound, self.database.findRecord, 'Image', id=imageId)
        self.image = self.database.createRecord('Image', stateID=2)
        self.failUnless(self.image, "Old record could not be re-created.")


class TestPerson(TestCase):
    "TestCase for the Person record."
    
    def setUp(self):
        super(TestPerson, self).setUp()
        self.database = DatabaseFacade()
        self.person = self.database.createRecord('Person', name='TestPerson', stateID=1, roleID=1)

    def tearDown(self):
        self.person.destroySelf()

    def test_create(self):
        self.failUnless(self.person, "New record could not be created.")
        self.failUnlessRaises(KforgeDbError, self.database.createRecord, 'Person', name='TestPerson', stateID=1)

    def test_find(self):
        self.failUnless(self.database.findRecord('Person', name='TestPerson'), "New record could not be selected.")
        self.failUnlessRaises(KforgeDbError, self.database.findRecord, 'Person', name='TestAlien')

    def test_destroySelf(self):
        self.person.destroySelf()
        self.failUnlessRaises(KforgeDbError, self.database.findRecord, 'Person', name='TestPerson')
        self.person = self.database.createRecord('Person', name='TestPerson', stateID=1, roleID=1)
        self.failUnless(self.person, "Old record could not be re-created.")

    def test_update(self):
        # Trouble with sqlite and Python 2.7: writing strings of '' causes record to return with value of None rather than ''.
        #self.assertEquals(self.person.fullname, "", "Record already has a 'fullname': %s" % repr(self.person.fullname))
        self.assertFalse(self.person.fullname, "Record already has a 'fullname': %s" % repr(self.person.fullname))
        self.person.fullname = "Test Person"
        self.assertFalse(self.person.fullname, "Record already has a 'fullname': %s" % repr(self.person.fullname))
        self.person.fullname = "Test Person"
        self.person.syncUpdate()
        self.assertEquals(self.person.fullname, "Test Person")
        person = self.database.findRecord('Person', name='TestPerson')
        self.assertEquals(person.fullname, "Test Person")

    def test_search(self):
        self.failUnlessSearchPerson('levin', 1)
        self.failUnlessSearchPerson('name:admin', 1)
        self.failUnlessSearchPerson('name:istrator', 0)
        self.failUnlessSearchPerson('fullname:admin', 1)
        self.failUnlessSearchPerson('fullname:istrator', 1)
        self.failUnlessSearchPerson('fullname:istrator', 1)
        self.failUnlessSearchPerson('', 0)
        self.failUnlessSearchPerson('notacol:admin', 0)
        self.failUnlessSearchPerson('name:', 0)
        self.failUnlessSearchPerson(':admin', 0)
        
    def failUnlessSearchPerson(self, userQuery, expectedCount):
        results = self.database.search('Person', userQuery, ['name', 'fullname'])
        count = results.count()
        msg = "%s != %s  user query=%s" % (count, expectedCount, userQuery)
        msg += "".join(["\n%s" % i for i in list(self.registry.people)])
        self.failUnlessEqual(count, expectedCount, msg)

class TestTransaction(TestCase):
    "TestCase for the database transactions."

    def setUp(self):
        super(TestTransaction, self).setUp()
        self.database = DatabaseFacade()
        self.fixtureName = 'TestTransaction'
        
        self.trans = self.database.beginTransaction()
        self.person = self.database.createRecord('Person', name=self.fixtureName, stateID=1, roleID=1)
   
    def tearDown(self):
        try:
            person = self.database.findRecord('Person', name=self.fixtureName)
            person.destroySelf()
        except:
            pass
        
    def _test_rollback(self):
        self.person.fullname = self.fixtureName
        self.transaction.rollback()
        self.failIf(self.person.fullname)

    def test_commit(self):  # todo: implement this test
        pass


#class TestProject(TestCase):
#    "TestCase for the Project class."
#    
#    def setUp(self):
#        super(TestProject, self).setUp()
#        self.database = DatabaseFacade()
#        self.db = self.database.createRecord('Project', name='TestProject', stateID=1)
#
#    def tearDown(self):
#        self.db.destroySelf()
#    
#    def test_create(self):
#        self.failUnless(self.db, "New record could not be created.")
#        self.failUnlessRaises(KforgeDbError, self.database.createRecord, 'Project', name='TestProject', stateID=1)
#
#    def test_select(self):
#        self.failUnless(self.database.findRecord('Project', name='TestProject'), "New record could not be selected.")
#        self.failUnlessRaises(KforgeDbError, self.database.findRecord, 'Project', name='TestAlien')
#
#    def test_destroySelf(self):
#        self.db.destroySelf()
#        self.failUnlessRaises(KforgeDbError, self.database.findRecord, 'Project', name='TestProject')
#        self.db = self.database.createRecord('Person', name='TestProject', stateID=1)
#        self.failUnless(self.db, "Old record could not be re-created.")
#
#    def test_update(self):
#        self.assertEquals(self.db.title, "", "Record already has a 'title'.")
#        self.db.title = "Test Project"
#        self.assertEquals(self.db.title, "Test Project", "Record 'title' attribute incorrect.")
#        db = self.database.findRecord('Project', name='TestProject')
#        self.assertEquals(db.title, "Test Project", " Record 'title' attribute incorrect.")
#
#class TestService(TestCase):
#    "TestCase for the Service class."
#    
#    def setUp(self):
#        super(TestService, self).setUp()
#        self.database = DatabaseFacade()
#        self.project = self.database.createRecord('Project', name='TestService', stateID=1)
#        self.plugin = self.database.findRecord('Plugin', name='example')
#        try:
#            self.db = self.database.createRecord('Service', project=self.project, plugin=self.plugin, stateID=1)
#        except:
#            self.project.destroySelf()
#            raise
#
#    def tearDown(self):
#        try:
#            self.db.destroySelf()
#        finally:
#            self.project.destroySelf()
#    
#    def test_create(self):
#        self.failUnless(self.db, "New record could not be created.")
#
#    def test_select(self):
#        self.failUnless(self.database.findRecord('Service', project=self.project, plugin=self.plugin), "New service could not be selected.")
#        self.failUnlessRaises(KforgeDbError, self.database.findRecord, 'Service', project=self.project, plugin=self.plugin, name='notExistingService')
#
#    def test_destroySelf(self):
#        self.db.destroySelf()
#        self.failUnlessRaises(KforgeDbError, self.database.findRecord, 'Service', project=self.project, plugin=self.plugin)
#        self.db = self.database.createRecord('Service', project=self.project, plugin=self.plugin, stateID=1)
#        self.failUnless(self.db, "Old record could not be re-created.")
#
#    def test_update(self):
#        self.assertEquals(self.db.name, "", "Record already has wrong name.")
#        self.db.name = "myexample"
#        self.db.sync()
#        self.assertEquals(self.db.name, "myexample", "Record 'name' attribute incorrect.")
#        db = self.database.findRecord('Service', project=self.project, name="myexample")
#        self.assertEquals(db.name, "myexample", " Record 'name' attribute incorrect.")
#
#class TestMember(TestCase):
#    "TestCase for the Member class."
#    
#    def setUp(self):
#        super(TestMember, self).setUp()
#        self.database = DatabaseFacade()
#        self.person = self.database.createRecord('Person', name='TestMember', stateID=1)
#        self.person2 = self.database.createRecord('Person', name='TestMember2', stateID=1)
#        try:
#            self.project = self.database.createRecord('Project', name='TestMember', stateID=1)
#        except:
#            self.person.destroySelf()
#            self.person2.destroySelf()
#            raise
#        else:
#            try:
#                member = self.database.createRecord('Member', project=self.project, person=self.person, stateID=1)
#                self.db = member
#            except:
#                try:
#                    self.project.destroySelf()
#                finally:
#                    self.person.destroySelf()
#                    self.person2.destroySelf()
#
#                raise
#
#    def tearDown(self):
#
#        try:
#            self.db.destroySelf()
#        finally:
#            try:
#                self.project.destroySelf()
#            finally:
#                self.person.destroySelf()
#                self.person2.destroySelf()
#    
#    def test_create(self):
#        self.failUnless(self.db, "New record could not be created.")
#        self.failUnlessRaises(KforgeDbError, self.database.createRecord, 'Member', project=self.project, person=self.person, stateID=1)
#
#    def test_select(self):
#        self.failUnless(self.database.findRecord('Member', project=self.project, person=self.person), "New record could not be selected.")
#        self.failUnlessRaises(KforgeDbError, self.database.findRecord, 'Member', project=self.project, person=self.person2)
#
#    def test_destroySelf(self):
#        self.db.destroySelf()
#        self.failUnlessRaises(KforgeDbError, self.database.findRecord, 'Member', project=self.project, person=self.person)
#        self.db = self.database.createRecord('Member', project=self.project, person=self.person, stateID=1)
#        self.failUnless(self.db, "Old record could not be re-created.")
#
#    def test_update(self):
#        self.failUnless(self.db.personID, "Record attribute has no user.")
#        self.assertEquals(self.db.personID, self.person.id, "Record attribute has incorrect value: %s, %s." % (self.db.personID, self.person.id))
#        self.db.person = self.person2
#        self.db.sync()
#        self.failUnlessRaises(KforgeDbError, self.database.findRecord, 'Member', project=self.project, person=self.person)
#        db = self.database.findRecord('Member', project=self.project, person=self.person2)
#        self.assertEquals(db.personID, self.person2.id, "Changed record attribute incorrect.")
#        self.db.person = self.person
#        self.db.sync()
#        self.failUnlessRaises(KforgeDbError, self.database.findRecord, 'Member', project=self.project, person=self.person2)
#        db = self.database.findRecord('Member', project=self.project, person=self.person)
#        self.assertEquals(db.personID, self.person.id, "Reset record attribute incorrect.")
#
