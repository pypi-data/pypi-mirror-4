import unittest
from dm.view.testunit import TestCase
from dm.view.manipulator import DomainObjectManipulator
from dm.view.manipulator import HasManyManipulator
from dm.ioc import *
from dm.util.datastructure import MultiValueDict
from dm.dom.pickers import *
from dm.exceptions import FormError

def suite():
    suites = [
        unittest.makeSuite(TestDomainObjectManipulatorCreate),
        unittest.makeSuite(TestDomainObjectManipulatorUpdate),
        unittest.makeSuite(TestHasManyManipulator),
    ]
    return unittest.TestSuite(suites)

# Todo: Test for manipulator building fields for attr types: Text (ie Textarea), Integer, Date, Markdown, Url, Boolean, Image, default, and HasA when choices > 50. 

class ManipulatorTestCase(TestCase):

    def setUp(self):
        super(ManipulatorTestCase, self).setUp()
        self.setUpData()
        self.buildManipulator()

    def tearDown(self):
        self.manipulator = None
        super(ManipulatorTestCase, self).tearDown()
    
    def buildManipulator(self):
        self.manipulator = self.createManipulator()
    
    def createManipulator(self):
        raise "Abstract method not implemented."

    def testValidate(self):
        # Valid data.
        try:
            self.manipulator.validate(self.validData)
        except FormError, inst:
            self.failFormError(inst)
        self.failIf(self.manipulator.getErrors())
        # Invalid data.
        self.failUnlessRaises(FormError, self.manipulator.validate, self.invalidData)
        self.failUnless(self.manipulator.getErrors())

    def failFormError(self, exc):
        self.fail("There were errors: %s" % exc.errors)


class DomainObjectManipulatorTestCase(ManipulatorTestCase):

    fixtureName = 'ManipulatorTestCase'
    sessionKey = 'sessiontestkey34234234234535634561345'

    def setUp(self):
        super(DomainObjectManipulatorTestCase, self).setUp()
        self.sessionFixture = self.registry.sessions.create(self.sessionKey)

    def setUpData(self):
        self.validData = MultiValueDict()
        self.validData['name'] = self.fixtureName
        self.validData['fullname'] = 'DomainObject Manipulator TestCase'
        self.validData['password'] = 'password'
        #self.validData['email'] = 'noreply@appropriatesoftware.net'
        self.validData['role'] = '/roles/Visitor'
        self.validData['state'] = 'active'
        self.validData.setlist('memberships', ['administration', 'example'])
        self.invalidData = MultiValueDict()
        self.invalidData['wrong'] = 'wrong'

    def tearDown(self):
        super(DomainObjectManipulatorTestCase, self).tearDown()
        if self.sessionKey in self.registry.sessions:
            del(self.registry.sessions[self.sessionKey])
        if self.fixtureName in self.registry.people.getAll():
            person = self.registry.people.getAll()[self.fixtureName]
            person.delete()
            person.purge()

    def createManipulator(self):
        return DomainObjectManipulator(objectRegister=self.registry.people, pickerClass=GetAdminInitableAttributes)

    #def testGetValidationErrors(self):
    #    errors = self.manipulator.getValidationErrors(self.validData)
    #    self.failIf(errors, str(errors))
    #    errors = self.manipulator.getValidationErrors(self.invalidData)
    #    self.failUnless(errors, str(errors))


class TestDomainObjectManipulatorCreate(DomainObjectManipulatorTestCase):

    def testCreate(self):
        # Check fields.
        self.failUnless('name' in self.manipulator.fields, self.manipulator.fields.keys())
        self.failUnless(self.manipulator.fields['name'].regex)
        # Check object doesn't exist.
        self.failIf(self.fixtureName in self.registry.people)
        # Create object.
        try:
            self.manipulator.create(self.validData)
        except FormError, inst:
            self.failFormError(inst)
        self.failIf(self.manipulator.getErrors())
        # Check object does now exist.
        self.failUnless(self.fixtureName in self.registry.people)
        person = self.registry.people[self.fixtureName]
        # Check attributes.
        self.failUnlessEqual(person.name, self.validData['name'])
        self.failUnlessEqual(person.fullname, self.validData['fullname'])
        #self.failUnlessEqual(person.email, self.validData['email'])
        self.failUnlessEqual(person.role.getUri(), self.validData['role'])


class TestDomainObjectManipulatorUpdate(DomainObjectManipulatorTestCase):

    def setUp(self):
        super(TestDomainObjectManipulatorUpdate, self).setUp()
        self.manipulator.create(self.validData)
        # Replace manipulator.
        self.manipulator = DomainObjectManipulator(
            objectRegister=self.registry.people,
            domainObject=self.manipulator.domainObject,
            pickerClass=GetAdminEditableAttributes
        )

    def testUpdateString(self):
        self.validData['fullname'] = 'Update ' + self.validData['fullname']
        try:
            self.manipulator.update(self.validData)
        except FormError, inst:
            self.failFormError(inst)
        person = self.registry.people[self.fixtureName]
        self.failUnlessEqual(person.fullname, self.validData['fullname'])

    def testUpdateHasA(self):
        self.validData['role'] = '/roles/Developer'
        try:
            self.manipulator.update(self.validData)
        except FormError, inst:
            self.failFormError(inst)
        person = self.registry.people[self.fixtureName]
        self.failUnlessEqual(person.role.getUri(), self.validData['role'])

    # Todo: Review behaviour of updating HasMany attribute (there are a few different
    # cases. The question is whether the associated object is deleted. That's good if
    # it models an association (is part of of a HasMany-HasA-HasA-HasMany pair) but
    # not if models a collection when a multi-select box doesn't allow for objects to be
    # created. So perhaps it would be good to code for when HasMany has association objects.
    # Todo: Code association object as an association object.
    # Note, this has now been done with the isImplicitAssociation. Only many-many associations
    # are created and deleted by adding and items to the HasMany attribute. Other HasMany
    # attributes are updated independently on the attribute's register.
    # Todo: Change this test to work with HasMany('MyImplicitAssociation') and then reinstate.
    #def testUpdateHasMany(self):
    #    person = self.registry.people[self.fixtureName]
    #    self.failIf(self.sessionKey in person.sessions)
    #    self.sessionFixture.person = person
    #    self.sessionFixture.save()
    #    self.failUnless(self.sessionKey in person.sessions)
    #    self.validData.setlist('sessions', [''])
    #    self.manipulator.update(self.validData)
    #    self.failIf(self.sessionKey in person.sessions, (self.sessionKey, person.sessions.keys()))


class HasManyManipulatorTestCase(ManipulatorTestCase):

    sessionKey = 'sessiontestkey34234234234535634561345'
    personName = 'levin'
    roleName = 'Developer'

    def setUp(self):
        self.person = self.registry.people[self.personName]
        super(HasManyManipulatorTestCase, self).setUp()
        self.sessionFixture = self.registry.sessions.create(self.sessionKey)

    def setUpData(self):
        self.validData = MultiValueDict()
        self.validData['person'] = self.personName
        self.validData['key'] = self.sessionKey
        self.validData['lastVisited'] = '2010-01-01'
        self.invalidData = MultiValueDict()
        self.invalidData['person'] = self.personName
        self.invalidData['key'] = self.sessionKey
        self.invalidData['lastVisited'] = 'letters'

    def tearDown(self):
        super(HasManyManipulatorTestCase, self).tearDown()
        if self.sessionKey in self.registry.sessions:
            del(self.registry.sessions[self.sessionKey])

    def createManipulator(self):
        return HasManyManipulator(objectRegister=self.person.sessions, pickerClass=GetEditableAttributes)


class TestHasManyManipulator(HasManyManipulatorTestCase):

    def testCreate(self):
        try:
            self.manipulator.create(self.validData)
        except FormError, inst:
            self.failFormError(inst)

