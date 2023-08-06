import dm.testunit
from dm.dictionarywords import URI_PREFIX
from dm.on import json
from dm.webkit import HttpRequest
from dm.util.datastructure import MultiValueDict

class TestCase(dm.testunit.TestCase):
    "Base class for View TestCases."
    
    def buildRequest(self):
        return None


class ApiTestCase(TestCase):
    "Abstract test case for CRUD requests to register and entities in API."

    apiKeyHeaderName = None
    viewClass = None
    registerName = None
    updatedEntityKey = None
    #META = MultiValueDict({            
    #    'SERVER_NAME': ['kforge.dev.localhost'],
    #    'SERVER_PORT': ['80'], 
    #})  
    META = {
        'SERVER_NAME': 'kforge.dev.localhost',
        'SERVER_PORT': '80',
    }

    def setUp(self):
        if not hasattr(self, 'apiKey'):
            person = self.registry.people['admin']
            apiKeys = self.registry.apiKeys.findDomainObjects(person=person)
            if apiKeys:
                self.apiKey = apiKeys[0]
            else:
                self.apiKey = self.registry.apiKeys.create(person=person)

    def test_getResponse(self):
        self.failUnlessRegisterGet()
        self.failUnlessRegisterGetNotFound()
        self.failUnlessRegisterPost()
        self.failUnlessRegisterPostBadRequest()
        self.failUnlessRegisterPostNotFound()
        self.failUnlessRegisterPostConflict()
        self.failUnlessEntityGet()
        self.failUnlessEntityGetNotFound()
        self.failUnlessEntityPut()
        self.failUnlessEntityPutBadRequest()
        self.failUnlessEntityPutNotFound()
        self.failUnlessEntityPutConflict()

    def setRequestPath(self, path):
        self.requestPath = self.dictionary[URI_PREFIX] + '/api' + path

    def failUnlessRegisterGet(self):
        self.setRequestPath('/%s' % self.registerName)
        self.getResponse()
        self.failUnlessStatusCode(200)
        self.failUnlessDataIsInstance(list)

    def failUnlessRegisterGetNotFound(self):
        self.setRequestPath('/zzz%s' % self.registerName)
        self.getResponse()
        self.failUnlessStatusCode(404)

    def failUnlessRegisterPost(self):
        self.setRequestPath('/%s' % self.registerName)
        self.getResponse(self.newEntity)
        self.failUnlessStatusCode(201)
        self.failUnlessData(None)
        if 'Location' in self.response:
            self.lastLocationHeader = self.response['Location']
            self.entityKey = self.response['Location'].strip('/').split('/')[-1]
            if not self.updatedEntityKey:
                self.updatedEntityKey = self.entityKey
        # Todo: Return created entity as response, so we can check what it looks like now?

    def failUnlessRegisterPostBadRequest(self):
        self.setRequestPath('/%s' % self.registerName)
        self.getResponse({})
        self.failUnlessStatusCode(400)

    def failUnlessRegisterPostNotFound(self):
        self.setRequestPath('/zzz%s' % self.registerName)
        self.getResponse(self.newEntity)
        self.failUnlessStatusCode(404)

    def failUnlessRegisterPostConflict(self):
        pass

    def failUnlessEntityGet(self):
        self.setRequestPath('/%s/%s' % (self.registerName, self.entityKey))
        self.getResponse()
        self.failUnlessStatusCode(200)
        self.failUnlessDataIsInstance(dict)

    def failUnlessEntityGetNotFound(self):
        self.setRequestPath('/%s/zzz%s' % (self.registerName, self.entityKey))
        self.getResponse()
        self.failUnlessStatusCode(404)

    def failUnlessEntityPut(self):
        self.setRequestPath('/%s/%s' % (self.registerName, self.entityKey))
        self.getResponse(self.changedEntity)
        self.failUnlessStatusCode(200)
        self.failUnlessData(None)
        # Read the entity, check it has been updated.
        self.setRequestPath('/%s/%s' % (self.registerName, self.updatedEntityKey))
        self.getResponse()
        for name in self.changedEntity:
            self.failUnlessEqual(self.data[name], self.changedEntity[name])
        # Check the read entity data can be submitted as an update.
        self.getResponse(self.data)
        self.failUnlessStatusCode(200)
        self.failUnlessData(None)

    def failUnlessEntityPutBadRequest(self):
        pass

    def failUnlessEntityPutNotFound(self):
        pass

    def failUnlessEntityPutConflict(self):
        pass

    def getResponse(self, data=None):
        self.data = None
        view = self.viewClass(request=self.createRequest(data))
        self.response = view.getResponse()
        if self.response.content:
            try:
                self.data = json.loads(self.response.content)
            except Exception, inst:
                raise Exception, "Couldn't get data from content '%s': %s" % (self.response.content, inst)

    def createRequest(self, data=None):
        request = HttpRequest()
        request.path = self.requestPath
        if data != None:
            request.POST[json.dumps(data)] = 1
        assert self.apiKeyHeaderName, "Api key header name not set on %s (needs something like 'HTTP_X_PACKAGENAME_API_KEY')." % self.__class__
        request.META = self.META.copy()
        request.META[self.apiKeyHeaderName] = self.apiKey.key
        return request

    def failUnlessStatusCode(self, expect=200):
        msg = "Status code '%s' not '%s' for path '%s'. %s" % (self.response.status_code, expect, self.requestPath, self.data)
        self.failUnlessEqual(self.response.status_code, expect, msg)

    def failUnlessData(self, expect):
        self.failUnlessEqual(self.data, expect)

    def failUnlessDataIsInstance(self, expect):
        msg = "Data '%s' is not instance of '%s'." % (self.data, expect)
        self.failUnless(isinstance(self.data, expect), msg)


