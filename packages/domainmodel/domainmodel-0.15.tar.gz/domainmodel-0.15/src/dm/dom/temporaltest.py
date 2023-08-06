import unittest
from dm.dom.testunit import TestCase
from dm.exceptions import *
from dm.dom.stateful import NamedObject, NamedStatefulObject, StatefulObject, String, DateTime, HasA, HasMany, AggregatesMany
from dm.dom.base import DomainObjectRegister
from dm.ioc import RequiredFeature
import datetime
import dm.times
from time import sleep
from dm.dom.temporal import TemporalProperty, BitemporalProperty, BitemporalActual
from dm.dom.temporal import TemporalCollection, BitemporalCollection, BitemporalActualCollection

def suite():
    suites = [
#        unittest.makeSuite(TestTemporalProperty),
#        unittest.makeSuite(TestBitemporalActual),
#        unittest.makeSuite(TestBitemporalProperty),
        # Example of DomainObject with temporal properties.
#        unittest.makeSuite(TestTemporal),   # TestTemporalPropertiesExample
        unittest.makeSuite(TestTemporalObjectExample),
    ]
    return unittest.TestSuite(suites)

# Todo: StringTemporal, DateTimeTemporal etc. attribute classes.
# Todo: Separate out the testing of indexes from testing of temporal attribute.


class TemporalObjectExampleGrant(StatefulObject):

    example = HasA('TemporalObjectExample', isRequired=True)
    permission  = HasA('Permission', isRequire=True)


class TemporalObjectExample(NamedStatefulObject):

    isTemporal = True

    title = String(default='Baby Title', isTemporal=True)
    address = String(default='Baby Address', isTemporal=True)
    person = HasA('Person', isRequired=False, isTemporal=True)
    grants = AggregatesMany('TemporalObjectExampleGrant', 'permission', 'example', isTemporal=True)


class TestTemporalObjectExample(TestCase):

    timepoint = RequiredFeature('Timepoint')

    def setUp(self):
        super(TestTemporalObjectExample, self).setUp()
        self.timepoint.reset()
        self.collection = TemporalObjectExample.createRegister(ownerName='parent')
        self.instance = None

    def tearDown(self):
        super(TestTemporalObjectExample, self).tearDown()
        while '' in self.collection:
            del(self.collection[''])
        self.timepoint.reset()

    def test_title(self):
        self.timepoint.reset()
        self.instance = self.collection.create()
        title1 = "Title1"
        title2 = "Title2"
        title3 = "Title3"
        title4 = "Title4"
        self.instance.title = title1
        self.instance.save()
        instance = self.collection['']
        self.failUnlessEqual(instance.title, title1)
        revision1 = self.timepoint.now()
        sleep(1)
        self.instance.title = title2
        self.instance.save()
        self.instance.title = title3
        self.instance.save()
        revision3 = self.timepoint.now()
        sleep(1)
        self.instance.title = title4
        self.instance.save()
        instance = self.collection['']
        self.failUnlessEqual(instance.title, title4)
        self.timepoint.recorded = revision1
        instance = self.collection['']
        self.failUnlessEqual(instance.title, title1)
        self.timepoint.recorded = revision3
        instance = self.collection['']
        self.failUnlessEqual(instance.title, title3)
        self.timepoint.reset()
        instance = self.collection['']
        self.failUnlessEqual(instance.title, title4)

    def test_grants(self):
        permissions = self.registry.permissions.getSortedList()
        permission1 = permissions[0]
        permission2 = permissions[1]
        permission3 = permissions[2]
        permission4 = permissions[3]

        self.timepoint.reset()
        self.instance = self.collection.create()
        grant1 = self.instance.grants.create(permission1)
        self.instance.save()
        revision1 = self.timepoint.now()
        instance = self.collection['']
        self.failUnless(permission1 in instance.grants)
        self.failIf(permission2 in instance.grants)
        self.failIf(permission3 in instance.grants)
        self.failIf(permission4 in instance.grants)
        sleep(1)
        del(self.instance.grants[permission1])
        grant2 = self.instance.grants.create(permission2)
        self.instance.save()
        grant3 = self.instance.grants.create(permission3)
        self.instance.save()
        revision3 = self.timepoint.now()
        sleep(1)
        grant4 = self.instance.grants.create(permission4)
        self.instance.save()
        revision4 = self.timepoint.now()

        #print "Sleeping"
        #sleep(1)

        self.timepoint.reset()
        grants = [i for i in self.collection[''].grants]
        self.failIf(grant1 in grants, grants)
        self.failUnless(grant2 in grants, grants)
        self.failUnless(grant3 in grants, grants)
        self.failUnless(grant4 in grants, grants)
        grants = self.collection[''].grants.keys()
        self.failIf(permission1 in grants, grants)
        self.failUnless(permission2 in grants, grants)
        self.failUnless(permission3 in grants, grants)
        self.failUnless(permission4 in grants, grants)
        grants = self.collection[''].grants
        self.failIf(permission1 in grants, grants)
        self.failUnless(permission2 in grants, grants)
        self.failUnless(permission3 in grants, grants)
        self.failUnless(permission4 in grants, grants)
        self.failUnlessEqual(len(grants), 3)
        self.failUnlessEqual(grants[permission4], grant4)

        self.timepoint.recorded = revision3
        grants = [i for i in self.collection[''].grants]
        self.failIf(grant1 in grants, (grant1, grants))
        self.failUnless(grant2 in grants, grants)
        self.failUnless(grant3 in grants, grants)
        self.failIf(grant4 in grants, (permission4, grants))
        grants = self.collection[''].grants.keys()
        self.failIf(permission1 in grants, grants)
        self.failUnless(permission2 in grants, grants)
        self.failUnless(permission3 in grants, grants)
        self.failIf(permission4 in grants, (permission4, grants))
        grants = self.collection[''].grants
        self.failIf(permission1 in grants, grants)
        self.failUnless(permission2 in grants, grants)
        self.failUnless(permission3 in grants, grants)
        self.failIf(permission4 in grants, grants)
        self.failUnlessEqual(len(grants), 2)
        self.failUnlessEqual(grants[permission3], grant3)

        self.timepoint.recorded = revision1
        grants = [i for i in self.collection[''].grants]
        self.failUnless(grant1 in grants, grants)
        self.failIf(grant2 in grants, grants)
        self.failIf(grant3 in grants, grants)
        self.failIf(grant4 in grants, grants)
        grants = self.collection[''].grants.keys()
        self.failUnless(permission1 in grants, grants)
        self.failIf(permission2 in grants, grants)
        self.failIf(permission3 in grants, grants)
        self.failIf(permission4 in grants, grants)
        grants = self.collection[''].grants
        self.failUnless(permission1 in grants, grants)
        self.failIf(permission2 in grants, grants)
        self.failIf(permission3 in grants, grants)
        self.failIf(permission4 in grants, grants)
        self.failUnlessEqual(len(grants), 1)
        self.failUnlessEqual(grants[permission1], grant1)

        self.timepoint.recorded = revision4
        grants = [i for i in self.collection[''].grants]
        self.failIf(grant1 in grants, grants)
        self.failUnless(grant2 in grants, grants)
        self.failUnless(grant3 in grants, grants)
        self.failUnless(grant4 in grants, grants)
        grants = self.collection[''].grants.keys()
        self.failIf(permission1 in grants, grants)
        self.failUnless(permission2 in grants, grants)
        self.failUnless(permission3 in grants, grants)
        self.failUnless(permission4 in grants, grants)
        grants = self.collection[''].grants
        self.failIf(permission1 in grants, grants)
        self.failUnless(permission2 in grants, grants)
        self.failUnless(permission3 in grants, grants)
        self.failUnless(permission4 in grants, grants)
        self.failUnlessEqual(len(grants), 3)
        self.failUnlessEqual(grants[permission2], grant2)

        self.timepoint.reset()
        grants = [i for i in self.collection[''].grants]
        self.failIf(grant1 in grants, grants)
        self.failUnless(grant2 in grants, grants)
        self.failUnless(grant3 in grants, grants)
        self.failUnless(grant4 in grants, grants)
        grants = self.collection[''].grants.keys()
        self.failIf(permission1 in grants, grants)
        self.failUnless(permission2 in grants, grants)
        self.failUnless(permission3 in grants, grants)
        self.failUnless(permission4 in grants, grants)
        grants = self.collection[''].grants
        self.failIf(permission1 in grants, grants)
        self.failUnless(permission2 in grants, grants)
        self.failUnless(permission3 in grants, grants)
        self.failUnless(permission4 in grants, grants)
        self.failUnlessEqual(len(grants), 3)
        self.failUnlessEqual(grants[permission2], grant2)

        # Wow!

        # Todo: Test (and implement) startsWith, search methods?


class TestTemporalProperty(TestCase):

    timepoint = RequiredFeature('Timepoint')

    def setUp(self):
        super(TestTemporalProperty, self).setUp()
        self.collection = TemporalProperty.createRegister(ownerName='parent')
        self.property = None

    def tearDown(self):
        super(TestTemporalProperty, self).tearDown()
        self.timepoint.reset()
        self.collection = None
        if self.property:
            self.property.delete()

    def test_collection(self):
        self.failUnlessEqual(type(self.collection), TemporalCollection)
        self.failUnlessEqual(self.collection.ownerName, 'parent')
        self.failUnlessEqual(self.collection.isCached, True)
        self.failUnlessEqual(self.collection.getDomainClass(), TemporalProperty)
        self.failUnlessEqual(TemporalProperty.isUnique, False)
        self.failUnlessEqual(TemporalProperty.isConstant, True)
        self.failUnlessEqual(TemporalProperty.registerKeyName, 'id')
        self.failUnlessEqual(TemporalProperty.sortOnName, 'dateCreated')
        self.failUnlessEqual(TemporalProperty.sortAscending, False)

    def test_instance(self):
        self.property = self.collection.create(recordedValue='')
        self.failUnless(self.property.dateCreated)
        #self.failUnlessEqual(self.property.getSortOnValue(), self.property.id)
        self.failUnlessEqual(self.property.getSortOnValue(), (self.property.dateCreated, self.property.id))

    def test_getFindTime(self):
        time1 = datetime.datetime(2003, 6, 1)
        self.timepoint.recorded = time1
        self.failUnlessEqual(self.collection.getFindTime(), time1)
        sleep(0.1)
        self.failUnlessEqual(self.collection.getFindTime(), time1)

    def test_getCreateTime(self):
        time1 = datetime.datetime(2003, 6, 1)
        self.timepoint.recorded = time1
        sleep(0.1)
        self.failUnlessEqual(self.collection.getCreateTime(), time1)
        self.timepoint.reset()
        self.failUnless(self.collection.getCreateTime() > time1)


class TestBitemporalActual(TestCase):

    timepoint = RequiredFeature('Timepoint')

    def setUp(self):
        super(TestBitemporalActual, self).setUp()
        self.collection = BitemporalActual.createRegister(ownerName='parent')
        self.property = None
        self.timepoint.reset()

    def tearDown(self):
        self.timepoint.reset()
        self.collection = None
        if self.property:
            self.property.delete()

    def test_collection(self):
        self.failUnlessEqual(type(self.collection), BitemporalActualCollection)
        self.failUnlessEqual(self.collection.ownerName, 'parent')
        self.failUnlessEqual(self.collection.isCached, True)
        self.failUnlessEqual(self.collection.getDomainClass(), BitemporalActual)
        self.failUnlessEqual(BitemporalActual.isUnique, False)
        self.failUnlessEqual(BitemporalActual.isConstant, True)
        self.failUnlessEqual(BitemporalActual.registerKeyName, 'id')
        self.failUnlessEqual(BitemporalActual.sortOnName, 'dateCreated')
        self.failUnlessEqual(BitemporalActual.sortAscending, False)

    def test_instance(self):
        time1 = datetime.datetime(2003, 6, 1)
        time2 = datetime.datetime(2003, 7, 1)
        time3 = datetime.datetime(2003, 8, 1)
        time4 = datetime.datetime(2003, 8, 1)
        property1 = self.collection.create(dateCreated=time1, recordedValue="1")
        property2 = self.collection.create(dateCreated=time3, recordedValue="2")
        property3 = self.collection.create(dateCreated=time2, recordedValue="3")
        property4 = None
        try:
            self.failUnless(property1.dateCreated)
            self.failUnlessEqual(property1.getSortOnValue(), (property1.dateCreated, property1.id))
            sortedList = self.collection.findDomainObjects()
            self.failUnlessEqual(sortedList, [property2, property3, property1])
            self.failUnlessEqual(sortedList[0].dateCreated, time3)
            self.failUnlessEqual(sortedList[1].dateCreated, time2)
            self.failUnlessEqual(sortedList[2].dateCreated, time1)
            self.failUnlessEqual(sortedList[0].recordedValue, "2")
            property4 = self.collection.create(dateCreated=time3, recordedValue="4")
            sortedList = self.collection.findDomainObjects()
            self.failUnlessEqual(sortedList[0].dateCreated, time3)
            self.failUnlessEqual(sortedList[0].recordedValue, "4", sortedList)
        finally:
            if property4:
                property4.delete()
            property3.delete()
            property2.delete()
            property1.delete()

    def test_getFindTime(self):
        time1 = datetime.datetime(2003, 6, 1)
        self.timepoint.actual = time1
        self.failUnlessEqual(self.collection.getFindTime(), time1)
        self.timepoint.reset()
        self.failUnless(self.collection.getFindTime() > time1)
        self.timepoint.recorded = time1
        self.failIfEqual(self.collection.getFindTime(), time1)

    def test_getCreateTime(self):
        time1 = datetime.datetime(2003, 6, 1)
        self.timepoint.actual = time1
        self.failUnlessEqual(self.collection.getCreateTime(), time1)
        self.timepoint.reset()
        self.failUnless(self.collection.getCreateTime() > time1)
        self.timepoint.recorded = time1
        self.failIfEqual(self.collection.getCreateTime(), time1)


class TestBitemporalProperty(TestCase):

    timepoint = RequiredFeature('Timepoint')

    def setUp(self):
        super(TestBitemporalProperty, self).setUp()
        self.collection = BitemporalProperty.createRegister(ownerName='parent')

    def tearDown(self):
        self.timepoint.reset()
        self.collection = None

    def test_collection(self):
        self.failUnlessEqual(type(self.collection), BitemporalCollection)
        self.failUnlessEqual(self.collection.ownerName, 'parent')
        self.failUnlessEqual(self.collection.isCached, True)
        self.failUnlessEqual(self.collection.getDomainClass(), BitemporalProperty)
        self.failUnlessEqual(TemporalProperty.isUnique, False)
        self.failUnlessEqual(TemporalProperty.isConstant, True)
        self.failUnlessEqual(TemporalProperty.registerKeyName, 'id')
        self.failUnlessEqual(TemporalProperty.sortOnName, 'dateCreated')
        self.failUnlessEqual(TemporalProperty.sortAscending, False)

    def test_instance(self):
        time1 = datetime.datetime(2003, 6, 1)
        time2 = datetime.datetime(2003, 7, 1)
        time3 = datetime.datetime(2003, 8, 1)
        time4 = datetime.datetime(2003, 8, 1)
#        property1 = self.collection.create(recordedValue="1")
#        property2 = self.collection.create(recordedValue="2")
#        property3 = self.collection.create(recordedValue="3")
#        property4 = None
#        try:
#            self.failUnless(property1.dateCreated)
#            self.failUnlessEqual(property1.getSortOnValue(), (property1.id))
#            sortedList = self.collection.findDomainObjects()
#            self.failUnlessEqual(sortedList, [property3, property2, property1])
#            self.failUnlessEqual(sortedList[0].recordedValue, "3")
#            property4 = self.collection.create(recordedValue="4")
#            sortedList = self.collection.findDomainObjects()
#            self.failUnlessEqual(sortedList[0].recordedValue, "4", sortedList)
#        finally:
#            if property4:
#                property4.delete()
#            property3.delete()
#            property2.delete()
#            property1.delete()

    def test_instance_actualtime_changes(self):
        time1 = datetime.datetime(2003, 6, 1)
        time2 = datetime.datetime(2003, 7, 1)
        time3 = datetime.datetime(2003, 8, 1)
        time4 = datetime.datetime(2003, 8, 1)
#        property1 = self.collection.create()
#        property1.recordedValue = "1"
#        property1.save()
#        self.timepoint.actual = time1
#        property2 = self.collection.create(recordedValue="2")
#        property3 = self.collection.create(recordedValue="3")
#        property4 = None
#        try:
#            self.failUnless(property1.dateCreated)
#            self.failUnlessEqual(property1.getSortOnValue(), (property1.dateCreated, property1.id))
#            sortedList = self.collection.findDomainObjects()
#            self.failUnlessEqual(sortedList, [property2, property3, property1])
#            self.failUnlessEqual(sortedList[0].dateCreated, time3)
#            self.failUnlessEqual(sortedList[1].dateCreated, time2)
#            self.failUnlessEqual(sortedList[2].dateCreated, time1)
#            self.failUnlessEqual(sortedList[0].recordedValue, "2")
#            property4 = self.collection.create(dateCreated=time3, recordedValue="4")
#            sortedList = self.collection.findDomainObjects()
#            self.failUnlessEqual(sortedList[0].dateCreated, time3)
#            self.failUnlessEqual(sortedList[0].recordedValue, "4", sortedList)
#        finally:
#            if property4:
#                property4.delete()
#            property3.delete()
#            property2.delete()
#            property1.delete()

    def test_getFindTime(self):
        time1 = datetime.datetime(2003, 6, 1)
        self.timepoint.recorded = time1
        self.failUnlessEqual(self.collection.getFindTime(), time1)
        sleep(0.1)
        self.failUnlessEqual(self.collection.getFindTime(), time1)
        self.timepoint.reset()
        self.failUnless(self.collection.getFindTime() > time1)

    def test_getCreateTime(self):
        time1 = datetime.datetime(2003, 6, 1)
        self.timepoint.recorded = time1
        sleep(0.1)
        self.failUnlessEqual(self.collection.getCreateTime(), time1)
        self.timepoint.reset()
        self.failUnless(self.collection.getCreateTime() > time1)


class Temporal(NamedObject):  # Example
    "Temporally attributed domain object."

    timepoint = RequiredFeature('Timepoint')

    # Todo: Exception when register key attribute is temporal.
    name = String(default='', isIndexed=True)
    description = String(default='', isTemporal=True)
    firstkiss = DateTime(isTemporal=True, default=timepoint.now())
    state = HasA('State', isTemporal=True, isRequired=False)
    haircolor = String(default='My Natural Color', isBitemporal=True)


# Todo: Support for passing temporal attribute value as create kwds.

class TestTemporal(TestCase):  # Example
    "TestCase for the Temporal class."

    timepoint = RequiredFeature('Timepoint')
    
    def setUp(self):
        super(TestTemporal, self).setUp()
        self.fixtureName = 'TestTemporal'
        self.temporals = self.registry.temporals
        if self.fixtureName in self.temporals:
            del(self.temporals[self.fixtureName])
        self.fixture = self.temporals.create(self.fixtureName)
        self.temporal = self.fixture 
        for i in range(1,5):
            newName = "%s%s" % (self.fixtureName, i)
            self.temporals.create(newName)

    def tearDown(self):
        for i in range(1,5):
            newName = "%s%s" % (self.fixtureName, i)
            del(self.temporals[newName])
        if self.fixture:
            fixture = self.fixture
        if self.fixtureName in self.temporals:
            del(self.temporals[self.fixtureName])
        self.temporal = None

    def test_meta(self):
        metaAttr = self.fixture.meta.attributeNames['description']
        self.failUnlessEqual(metaAttr.isIndexed, False)
        self.failUnlessEqual(metaAttr.isTemporal, True)
        metaAttr = self.fixture.meta.attributeNames['firstkiss']
        self.failUnlessEqual(metaAttr.isIndexed, False)
        self.failUnlessEqual(metaAttr.isTemporal, True)
        metaAttr = self.fixture.meta.attributeNames['name']
        self.failUnlessEqual(metaAttr.isIndexed, True)
        self.failUnlessEqual(metaAttr.isTemporal, False)

    def test_new(self):
        self.failUnless(self.fixture)
        self.failUnlessRaises(KforgeDomError,
            self.registry.temporals.create, self.fixtureName
        )
        self.failUnlessEqual(type(self.fixture.description), type(""))
        self.failUnlessEqual(self.fixture.description, "")


    def test_find(self):
        self.failUnless(self.registry.temporals['TestTemporal'],
            "New temporal could not be found."
        )
        self.failUnlessRaises(KforgeRegistryKeyError,
            self.registry.temporals.__getitem__, 'TestAlien'
        )

    def test_recorded_history_of_actual_history(self):
        # This test follows the example half-way down this page:
        # http://martinfowler.com/ap2/temporalProperty.html

        self.timepoint.reset()
        
        color1 = "First Color"
        color2 = "Second Color"
        changeTime1 = datetime.datetime(2000, 1, 1, 0, 0 ,0)
        updateTime1 = datetime.datetime(2003, 6, 1, 0, 0 ,0)
        beforeChange2 = datetime.datetime(2003, 12, 1, 0, 0, 0)
        changeTime2 = datetime.datetime(2004, 1, 1, 0, 0 ,0)
        afterChange2 = datetime.datetime(2004, 1, 2, 0, 0, 0)
        beforeUpdate2 = datetime.datetime(2004, 1, 9, 0, 0, 0)
        updateTime2 = datetime.datetime(2004, 1, 10, 0, 0 ,0)
        afterUpdate2 = datetime.datetime(2004, 1, 10, 0, 0, 0)

        temporal = self.temporals[self.fixtureName]
        #  Check that we currently have first value before time of 2nd change.
        
        # Record something happening at an earlier actual time.
        self.timepoint.reset()
        self.timepoint.recorded = updateTime1
        self.timepoint.actual = changeTime1
        temporal.haircolor = color1
        temporal.save()

        # Later, record that something else has happened.
        self.timepoint.reset()
        self.timepoint.recorded = updateTime2
        self.timepoint.actual = changeTime2
        temporal.haircolor = color2
        temporal.save()
       
        #  Check before 2nd update that we have first value before time of 2nd change.
        self.timepoint.reset()
        self.timepoint.recorded = beforeUpdate2
        self.timepoint.actual = beforeChange2
        temporal = self.temporals[self.fixtureName]
        self.failUnlessEqual(self.temporal.haircolor, color1)

        #  Check after 2nd update that we have first value before time of 2nd change.
        self.timepoint.reset()
        self.timepoint.recorded = afterUpdate2
        self.timepoint.actual = beforeChange2
        temporal = self.temporals[self.fixtureName]
        self.failUnlessEqual(self.temporal.haircolor, color1)

        #  Check that we currently have first value before time of 2nd change.
        self.timepoint.reset()
        self.timepoint.actual = beforeChange2
        temporal = self.temporals[self.fixtureName]
        self.failUnlessEqual(self.temporal.haircolor, color1)


        #  Check before 2nd update that we have first value after time of 2nd change.
        self.timepoint.reset()
        self.timepoint.recorded = beforeUpdate2
        self.timepoint.actual = afterChange2
        temporal = self.temporals[self.fixtureName]
        self.failUnlessEqual(self.temporal.haircolor, color1)

        #  Check after 2nd update that we have second value after time of 2nd change.
        self.timepoint.reset()
        self.timepoint.recorded = afterUpdate2
        self.timepoint.actual = afterChange2
        temporal = self.temporals[self.fixtureName]
        self.failUnlessEqual(self.temporal.haircolor, color2)

        #  Check that we currently have second value after time of 2nd change.
        self.timepoint.reset()
        self.timepoint.actual = afterChange2
        temporal = self.temporals[self.fixtureName]
        self.failUnlessEqual(self.temporal.haircolor, color2)



    def test_recorded_value_history(self):
        self.failUnlessEqual(self.temporal.description, "", "Already has a description.")
        self.temporal.description = "Test Temporal"
        self.failUnlessEqual(self.temporal.description, "Test Temporal", "Temporal doesn't have attribute.")
        self.temporal.save()
        temporal = self.temporals[self.fixtureName]
        self.failUnlessEqual(temporal.description, "Test Temporal")
        temporal.description = "Other Temporal"
        self.failUnlessEqual(self.temporal.description, "Other Temporal", "Suspect duplicate domain objects!!")
        temporal.save()
        self.failUnlessEqual(temporal.description, "Other Temporal", "Suspect broken temporal attribute: %s" % temporal.description)
        temporal.save()
        self.failUnlessEqual(temporal.description, "Other Temporal", "Suspect broken temporal attribute: %s" % temporal.description)
        temporal.save()
        temporal = self.temporals[self.fixtureName]
        self.failUnlessEqual(temporal.description, "Other Temporal", "Suspect broken temporal attribute: %s" % temporal.description)

        # Make changes to the recorded time.
        state1 = self.registry.states['active']
        state2 = self.registry.states['pending']
        state3 = self.registry.states['deleted']
        time1 = datetime.datetime(2007, 6, 1, 0, 0 ,0)
        time2 = datetime.datetime(2007, 7, 1, 0, 0 ,0)
        time3 = datetime.datetime(2007, 8, 1, 0, 0 ,0)
        description1 = "Description One"
        description2 = "Description Two"
        description3 = "Description Three"
        haircolor0 = "Haircolor Zero"
        haircolor1 = "Haircolor One"
        haircolor2 = "Haircolor Two"
        haircolor3 = "Haircolor Three"
        haircolor4 = "Haircolor Four"
        temporal.description = description1
        temporal.firstkiss = time1
        temporal.state = state1
        temporal.haircolor = haircolor1
        temporal.save()
        revisionTime = self.timepoint.now()
        sleep(3)
        temporal.description = description2
        temporal.firstkiss = time2
        temporal.state = state2
        temporal.haircolor = haircolor2
        temporal.save()
        #  - check present is most recent
        self.timepoint.reset()
        temporal = self.temporals[self.fixtureName]
        self.failUnlessEqual(temporal.description, description2)
        self.failUnlessEqual(temporal.firstkiss, time2)
        self.failUnlessEqual(temporal.state, state2)
        self.failUnlessEqual(temporal.haircolor, haircolor2)
        #  - check revisionTime is 'recent'
        self.timepoint.recorded = revisionTime
        temporal = self.temporals[self.fixtureName]
        self.failUnlessEqual(temporal.description, description1)
        self.failUnlessEqual(temporal.firstkiss, time1)
        self.failUnlessEqual(temporal.state, state1)
        self.failUnlessEqual(temporal.haircolor, haircolor1)
        #  - check we can return to the present
        self.timepoint.reset()
        temporal = self.temporals[self.fixtureName]
        self.failUnlessEqual(temporal.description, description2)
        self.failUnlessEqual(temporal.firstkiss, time2)
        self.failUnlessEqual(temporal.state, state2)
        self.failUnlessEqual(temporal.haircolor, haircolor2)
        #  - check a new value comes through ok
        temporal.description = description3
        temporal.firstkiss = time3
        temporal.state = state3
        temporal.haircolor = haircolor3
        temporal.save()
        temporal = self.temporals[self.fixtureName]
       
        self.failUnlessEqual(temporal.description, description3)
        self.failUnlessEqual(temporal.firstkiss, time3)
        self.failUnlessEqual(temporal.state, state3)
        self.failUnlessEqual(temporal.haircolor, haircolor3)

    def test_count(self):
        self.failUnless(self.temporals.count(), "Problem with temporal count.")

    def test_keys(self):
        self.failUnless(self.temporals.keys(), "Problem with temporal list.")

    def test_iter(self):
        self.failUnless(self.temporals.__iter__(), "Problem with temporal iter.")
        for p in self.temporals:
            self.failUnless(p.name, "Problem with iteration temporal: %s" % p)

    def test_getNextObject(self):
        temporalList = self.temporals.getSortedList()
        lenList = len(temporalList)
        self.failUnless(lenList >= 4, lenList)
        temporal = temporalList[-3]
        nextTemporal = self.temporals.getNextObject(temporalList, temporal)
        self.failUnlessEqual(nextTemporal, temporalList[-2])
        nextTemporal = self.temporals.getNextObject(temporalList, nextTemporal)
        self.failUnlessEqual(nextTemporal, temporalList[-1])
        nextTemporal = self.temporals.getNextObject(temporalList, nextTemporal)
        self.failIf(nextTemporal)
        
    def test_getPreviousObject(self):
        temporalList = self.temporals.getSortedList()
        lenList = len(temporalList)
        self.failUnless(lenList >= 4, lenList)
        temporal = temporalList[2]
        previousTemporal = self.temporals.getPreviousObject(temporalList, temporal)
        self.failUnlessEqual(previousTemporal, temporalList[1])
        previousTemporal = self.temporals.getPreviousObject(temporalList, previousTemporal)
        self.failUnlessEqual(previousTemporal, temporalList[0])
        previousTemporal = self.temporals.getPreviousObject(temporalList, previousTemporal)
        self.failIf(previousTemporal)


