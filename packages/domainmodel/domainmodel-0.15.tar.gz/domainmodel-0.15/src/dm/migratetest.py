import unittest
from dm.view.basetest import TestCase
from dm.migrate import DomainModelDumper
from dm.migrate import DomainModelLoader
from dm.migrate import DomainModelMigrator

# Todo: Fixup synching record indexes better than create/delete cycles, which probably causes undesirable consequences for aggregated objects that have already been imported.

def suite():
    suites = [
        unittest.makeSuite(TestDomainModelDumper),
        unittest.makeSuite(TestDomainModelLoader),
        unittest.makeSuite(TestDomainModelMigrator),
    ]
    return unittest.TestSuite(suites)


class TestDomainModelDumper(TestCase):

    def setUp(self):
        self.dumper = DomainModelDumper()

    def tearDown(self):
        del(self.dumper)

    def testDumpData(self):
        dump = self.dumper.dumpData()
        self.failUnless(dump['Action'])
        self.failUnless(dump['Action']['metaData'])
        self.failUnlessEqual(dump['Action']['metaData']['name'], 'String')
        self.failUnless(dump['Action'][1])
        self.failUnlessEqual(dump['Action'][1]['name'], 'Create')
        self.failUnlessEqual(dump['Person'][3]['fullname'], u'Levin \xf3'.encode('utf8'))

    def testDumpDataAsJson(self):
        self.failUnless(self.dumper.dumpDataAsJson())

    def testDumpDataToFile(self):
        # get a file somewhere
        # call the dumpDataToFile() method with path to file
        # check the written file
        pass


class TestDomainModelLoader(TestCase):

    def clearFixtures(self):
        for name in ['IdSacrifice', 'migrated', 'migrated23', 'migrated77']:
            if name in self.registry.sessions:
                del(self.registry.sessions[name])
        for name in ['IdSacrifice', 'migrated', 'migrated2']:
            if name in self.registry.people:
                del(self.registry.people[name])

    def setUp(self):
        self.failUnlessRaises(Exception, DomainModelLoader)
        self.loader = DomainModelLoader(isMerge=True)
        self.clearFixtures()
        self.lastPersonId = self.registry.people.create("IdSacrifice").id
        self.lastSessionId = self.registry.sessions.create("IdSacrifice").id

    def tearDown(self):
        self.clearFixtures()
        del(self.loader)

    def testLoadDataAsJson(self):
        # Persons
        lastId = self.lastPersonId
        self.failIf('migrated' in self.registry.people)
        self.failIf('migrated2' in self.registry.people)
        self.loader.loadDataAsJson("""{
            "Person": {
                "metaData": {"name": "String"},
                "%s": {"name": "migrated", "fullname": "Unicode \xc3\xb3 Jeff"},
                "%s": {"name": "migrated2", "dateCreated": "2005-12-31 18:30:00"}
            }
        }""" % (lastId+1, lastId+2))
        self.failUnless('migrated' in self.registry.people)
        self.failUnlessEqual(self.registry.people['migrated'].fullname, "Unicode \xc3\xb3 Jeff".decode('utf8'))
        self.failUnless('migrated2' in self.registry.people)
        import datetime
        self.failUnlessEqual(self.registry.people['migrated2'].dateCreated, datetime.datetime(2005,12,31,18,30,0))
        del(self.registry.people['migrated'])
        del(self.registry.people['migrated2'])
        self.failIf('migrated' in self.registry.people)
        self.failIf('migrated2' in self.registry.people)

        # Sessions
        lastId = self.lastSessionId
        self.failIf('migrated' in self.registry.sessions)
        self.failIf('migrated23' in self.registry.sessions)
        self.loader.loadDataAsJson("""{
            "Session": {
                "metaData": {"key": "String"},
                "%s": {"key": "migrated"},
                "%s": {"key": "migrated23"}
            }
        }""" % (lastId+1, lastId+7))
        self.failUnless('migrated' in self.registry.sessions)
        del(self.registry.sessions['migrated'])
        self.failIf('migrated' in self.registry.sessions)
        self.failUnless('migrated23' in self.registry.sessions)
        lastId = self.registry.sessions['migrated23'].id 
        del(self.registry.sessions['migrated23'])
        self.failIf('migrated23' in self.registry.sessions)

        forwardId = lastId + 5
        sessionName = "migrated77"
        self.failIf(sessionName in self.registry.sessions)
        self.loader.loadDataAsJson(
            """{
                "Session": {
                    "metaData": {"key": "String"},
                    "%s": {"key": "%s"}
                }
            }""" % (forwardId, sessionName)
        )
        self.failUnless(sessionName in self.registry.sessions)
        resultingId = self.registry.sessions[sessionName].id
        self.failUnlessEqual(resultingId, forwardId)
        del(self.registry.sessions[sessionName])
        self.failIf(sessionName in self.registry.sessions)


class DomainModelMigratorTestCase(TestCase):

    dumpedData = None
    planSteps = []

    def setUp(self):
        super(DomainModelMigratorTestCase, self).setUp()
        self.strategy = DomainModelMigrator(self.dumpedData, self.planSteps)

    def tearDown(self):
        super(DomainModelMigratorTestCase, self).tearDown()
        self.strategy = None

    def test_migrate(self):
        self.failUnlessDataOkBefore()
        self.strategy.migrate()
        self.failUnlessDataOkAfter()

    def failUnlessDataOkBefore(self):
        pass

    def failUnlessDataOkAfter(self):
        pass


class TestDomainModelMigrator(DomainModelMigratorTestCase):

    # Todo: Adjust meta data too, and check data with meta data?
    # Todo: Or perhaps just code changes against the system version number?

    dumpedData = {
        'Person': {
            'fred': {
                'id': 1,
                'name': 'fred',
                'email': 'fred@domain.com',
            },
            'jill': {
                'id': 2,
                'name': 'jill',
                'email': 'jill@domain.com',
            },
            'joe': {
                'id': 3,
                'name': 'joe',
                'email': 'joe@domain.com',
            },
        },
        'Project': {
            'yellow': {
                'id': 1,
                'name': 'yellow',
                'description': 'yellow yellow yellow',
            },
            'red': {
                'id': 2,
                'name': 'red',
                'description': 'red red red',
            },
        },
        'Place': {
            2: {
                'id': 2,
                'title': 'Hill Top \xc3\xb3',
                'location': 'GR465798',
                'image': '',
                'dateDiscovered': '2007-03-04 00:00:00',
            },
        },
    }
    planSteps = [
        'drop class Project',
        'move class Person User',
        'add class TrainingSession',
        'drop attribute Place image',
        'move attribute Place title officialname',
        'add attribute Place latitude',
        'move class Place GeographicalPlace',
        'move attribute GeographicalPlace location gridref',
        'convert attribute GeographicalPlace dateDiscovered datetime_to_date',
    ]

    def failUnlessDataOkAfter(self):
        self.failUnlessEqual(len(self.dumpedData.keys()), 2)
        dumpedDataKeys = self.dumpedData.keys()
        self.failUnless('User' in dumpedDataKeys, dumpedDataKeys)
        self.failUnless('GeographicalPlace' in dumpedDataKeys, dumpedDataKeys)
        placeData = self.dumpedData['GeographicalPlace']
        place = placeData[2]
        self.failUnless('officialname' in place, place)
        self.failUnless('gridref' in place, place)
        self.failUnless('dateDiscovered' in place, place)
        self.failUnlessEqual(place['officialname'], 'Hill Top \xc3\xb3')
        self.failUnlessEqual(place['gridref'], 'GR465798')
        self.failUnlessEqual(place['dateDiscovered'], '2007-03-04')

