import unittest
from dm.view.basetest import ViewTestCase
from dm.view.basetest import MultiValueDict
from dm.view.api import ApiView
from dm.dictionarywords import SYSTEM_VERSION
from dm.on import json

def suite():
    suites = [
        unittest.makeSuite(TestApiGetOk),
        unittest.makeSuite(TestApiGetDictionaryNotFound),
        unittest.makeSuite(TestApiPostDenied),
        unittest.makeSuite(TestApiGetPersonsOk),
        unittest.makeSuite(TestApiPostPersonsOk),
        unittest.makeSuite(TestApiPostPersonsBadRequest1),
        unittest.makeSuite(TestApiPostPersonsBadRequest2),
        unittest.makeSuite(TestApiGetPersonOk),
        unittest.makeSuite(TestApiPostPersonOk),
        #unittest.makeSuite(TestApiPostPersonBadRequest),
    ]
    return unittest.TestSuite(suites)


class ApiViewTestCase(ViewTestCase):
    "Abstract test case single requests to API view."

    viewClass = ApiView
    requestData = None
    requiredResponseData = None
    requiredResponseFields = None
    requiredResponseValues = None
    requiredResponseItems = None

    maxDiff = None # So unittest shows errors with full diff.

    def initPost(self):
        if self.requestData != None:
            jsonRequestData = json.dumps(self.requestData)
            self.POST = MultiValueDict({jsonRequestData: 1})

    def checkResponseContent(self):
        if self.requiredResponseData != None:
            # Check exact match with response data.
            responseData = json.loads(self.response.content)
            self.failUnlessEqual(responseData, self.requiredResponseData)
        if self.requiredResponseFields != None:
            # Check for exact match with names in dict.
            responseData = json.loads(self.response.content)
            self.failUnlessEqual(responseData.keys(), self.requiredResponseFields)
        if self.requiredResponseValues != None:
            # Check for specific named values in dict.
            responseData = json.loads(self.response.content)
            for (name, requiredValue) in self.requiredResponseValues.items():
                actualValue = responseData[name]
                msg = "'%s' is '%s' (expected '%s')" % (name, actualValue, requiredValue)
                self.failUnlessEqual(actualValue, requiredValue, msg)
        if self.requiredResponseItems != None:
            # Check for specific items in list.
            responseData = json.loads(self.response.content)
            for requiredItem in self.requiredResponseItems:
                msg = "'%s' not in '%s'" % (requiredItem, responseData)
                self.failUnless(requiredItem in responseData, msg)
        


class TestApiGetOk(ApiViewTestCase):
    requestPath = '/api'
    requiredResponseClassName = 'HttpResponse'
    requiredResponseStatus = 200
    requiredResponseData = ["http://kforge.dev.localhost/api/people", "http://kforge.dev.localhost/api/systems"]

class TestApiGetDictionaryNotFound(ApiViewTestCase):
    requestPath = '/api/dictionary'
    requiredResponseClassName = 'HttpResponse'
    requiredResponseStatus = 404

class TestApiPostDenied(ApiViewTestCase):
    requestPath = '/api'
    requiredResponseClassName = 'HttpResponse'
    requestData = {"resources": []}
    requiredResponseStatus = 403

class TestApiGetPersonsOk(ApiViewTestCase):
    requestPath = '/api/people'
    requiredResponseClassName = 'HttpResponse'
    requiredResponseStatus = 200
    requiredResponseData = [
        "http://kforge.dev.localhost/api/people/admin",
        "http://kforge.dev.localhost/api/people/levin",
        "http://kforge.dev.localhost/api/people/natasha",
        "http://kforge.dev.localhost/api/people/visitor",
    ]

class TestApiPostPersonsOk(ApiViewTestCase):
    requestPath = '/api/people'
    requiredResponseClassName = 'HttpResponse'
    requiredResponseStatus = 201
    requestData = {"name": "testapi", "password": "pass"}
    requiredResponseHeaders = [('Location', 'http://kforge.dev.localhost/api/people/testapi')]

    def tearDown(self):
        super(TestApiPostPersonsOk, self).tearDown()
        if 'testapi' in self.registry.people:
            del(self.registry.people['testapi'])

class TestApiPostPersonsBadRequest1(ApiViewTestCase):
    requestPath = '/api/people'
    requiredResponseClassName = 'HttpResponse'
    requiredResponseStatus = 400
    requestData = {"resources": []}
    requiredResponseData = {"password": "This field is required.", "name": "This field is required."}

class TestApiPostPersonsBadRequest2(ApiViewTestCase):
    requestPath = '/api/people'
    requestData = {"name": "admin", "fullname": "Administrator", "password": "pass"}
    requiredResponseClassName = 'HttpResponse'
    requiredResponseStatus = 400
    requiredResponseData = {"name": "The name \'admin\' is already being used."}

class TestApiGetPersonOk(ApiViewTestCase):
    requestPath = '/api/people/admin'
    requiredResponseClassName = 'HttpResponse'
    requiredResponseStatus = 200
    requiredResponseFields = [u'name', u'lastModified', u'dateCreated', u'role', u'emailAddresses', u'password', u'fullname']
    requiredResponseValues = {'name': 'admin', 'role': 'http://kforge.dev.localhost/api/roles/Administrator', 'fullname': 'Administrator'}

class TestApiPostPersonOk(ApiViewTestCase):
    viewerName = 'admin'
    requestPath = '/api/people/admin'
    requestData = {"fullname": "Administrator"}
    requiredResponseClassName = 'HttpResponse'
    requiredResponseStatus = 200

# Having made fullname optional, this test is effectively redundant.
class TestApiPostPersonBadRequest(ApiViewTestCase):
    viewerName = 'admin'
    requestPath = '/api/people/admin'
    requestData = {}
    requiredResponseClassName = 'HttpResponse'
    requiredResponseStatus = 400

