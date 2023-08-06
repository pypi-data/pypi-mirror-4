import unittest
from dm.view.basetest import AdminSessionViewTestCase
from dm.view.rpc import RpcView
from dm.view.rpc import JsonView
from dm.view.rpc import AutocompleterView, RegistryAutocompleterView
from dm.view.rpc import Autocompleter, RegistryAutocompleter
from dm.view.rpc import RegistryAutoappenderView
from dm.view.rpc import RegistryAutodeleteView
from dm.on import json

def suite():
    suites = [
        unittest.makeSuite(TestRpcView),
        unittest.makeSuite(TestJsonView1),
        unittest.makeSuite(TestJsonView2),
        unittest.makeSuite(TestAutocompleterView1),
        unittest.makeSuite(TestAutocompleterView2),
        unittest.makeSuite(TestAutocompleterView3),
        unittest.makeSuite(TestRegistryAutocompleterView),
        unittest.makeSuite(TestRegistryAutoappenderView),
        unittest.makeSuite(TestRegistryAutodeleteView),
    ]
    return unittest.TestSuite(suites)


class RpcViewTestCase(AdminSessionViewTestCase):
    
    viewClass = RpcView


class TestRpcView(RpcViewTestCase):

    requiredResponseContent = ''


class JsonViewTestCase(RpcViewTestCase):
    
    viewClass = JsonView
    postMethodName = 'default'
    postMethodParams = []
    requiredResponseContent = '"default message"'

    def initPost(self):
        jsonString = json.dumps({
            'method': self.postMethodName,
            'params': self.postMethodParams,
        })
        self.POST[jsonString] = 1



class TestJsonView1(JsonViewTestCase):

    pass


class TestJsonView2(JsonViewTestCase):

    postMethodName = ''


class AutocompleterViewTestCase(JsonViewTestCase):

    viewClass = AutocompleterView
    postQueryName = 'value'
    postQueryString = ''
    requiredResponseContent = '["", "errors", "errors1", "errors2", "errors3", "errors4"]'

    def initPost(self):
        self.POST[self.postQueryName] = self.postQueryString

    def createViewKwds(self):
        kwds = super(AutocompleterViewTestCase, self).createViewKwds()
        kwds['completer'] = self.createAutocompleter()
        kwds['queryName'] = self.postQueryName
        return kwds

    def createAutocompleter(self):
        return Autocompleter()


class TestAutocompleterView1(AutocompleterViewTestCase):

    pass


class TestAutocompleterView2(AutocompleterViewTestCase):

    postQueryString = 'a'
    requiredResponseContent = '["a", "errors", "errors1", "errors2", "errors3", "errors4"]'


class TestAutocompleterView3(AutocompleterViewTestCase):

    postQueryName = 'queryString'
    postQueryString = 'b'
    requiredResponseContent = '["b", "errors", "errors1", "errors2", "errors3", "errors4"]'


class TestRegistryAutocompleterView(AutocompleterViewTestCase):

    postQueryName = 'queryString'
    viewClass = RegistryAutocompleterView
    postQueryString = 'RegistryAutocomplete2'
    requiredResponseContent = '["RegistryAutocomplete2"]'
    registryPath = None

    def initPost(self):
        super(TestRegistryAutocompleterView, self).initPost()
        self.POST['registryPath'] = self.registryPath

    def createAutocompleter(self):
        return RegistryAutocompleter()

    def setUp(self):
        sessions = self.registry.sessions
        people = self.registry.people
        self.person = people.create('TestRegistryAutocomplete')
        self.session1 = sessions.create('RegistryAutocomplete1')
        self.session2 = sessions.create('RegistryAutocomplete2')
        self.requiredResponseContent = '["RegistryAutocomplete2 (#%s)"]' % (
            self.session2.id
        )
        self.registryPath = 'people/%s/sessions' % self.person.getRegisterKeyValue()
        super(TestRegistryAutocompleterView, self).setUp()

    def tearDown(self):
        super(TestRegistryAutocompleterView, self).tearDown()
        self.session2.delete()
        self.session1.delete()
        self.person.delete()


class AutoappenderViewTestCase(JsonViewTestCase):

    viewClass = RegistryAutoappenderView
    completedString = 'RegistryAutoappend3'
    targetAttribute = 'key'
    registryPath = None
    requiredResponseContent = None

    def initPost(self):
        self.POST['completedString'] = self.completedString
        self.POST['registryPath'] = self.registryPath
        self.POST['targetAttribute'] = self.targetAttribute

    def setUp(self):
        while 'TestRegistryAutoappend' in self.registry.people:
            del(self.registry.people['TestRegistryAutoappend'])
        while 'RegistryAutoappend1' in self.registry.sessions:
            del(self.registry.sessions['RegistryAutoappend1'])
        while 'RegistryAutoappend2' in self.registry.sessions:
            del(self.registry.sessions['RegistryAutoappend2'])
        while 'RegistryAutoappend3' in self.registry.sessions:
            del(self.registry.sessions['RegistryAutoappend3'])
        sessions = self.registry.sessions
        people = self.registry.people
        self.person = people.create('TestRegistryAutoappend')
        self.session1 = sessions.create('RegistryAutoappend1')
        self.session2 = sessions.create('RegistryAutoappend2')
        registerKey = self.person.getRegisterKeyValue()
        self.registryPath = 'people/%s/sessions' % registerKey 
        super(AutoappenderViewTestCase, self).setUp()

    def tearDown(self):
        super(AutoappenderViewTestCase, self).tearDown()
        while 'RegistryAutoappend3' in self.registry.sessions:
            del(self.registry.sessions['RegistryAutoappend3'])
        while 'RegistryAutoappend2' in self.registry.sessions:
            del(self.registry.sessions['RegistryAutoappend2'])
        while 'RegistryAutoappend1' in self.registry.sessions:
            del(self.registry.sessions['RegistryAutoappend1'])
        while 'TestRegistryAutoappend' in self.registry.people:
            del(self.registry.people['TestRegistryAutoappend'])

    def checkResponseContent(self):
        session = self.registry.sessions[self.completedString]
        self.requiredResponseContent = '"OK"'
        self.failUnlessResponseContent()
        


class TestRegistryAutoappenderView(AutoappenderViewTestCase):

    pass


class AutodeleteViewTestCase(JsonViewTestCase):

    viewClass = RegistryAutodeleteView
    registryPath = None
    requiredResponseContent = None

    def initPost(self):
        self.POST['registryPath'] = self.registryPath

    def setUp(self):
        while 'TestRegistryAutoappend' in self.registry.people:
            del(self.registry.people['TestRegistryAutoappend'])
        while 'RegistryAutoappend1' in self.registry.sessions:
            del(self.registry.sessions['RegistryAutoappend1'])
        while 'RegistryAutoappend2' in self.registry.sessions:
            del(self.registry.sessions['RegistryAutoappend2'])
        while 'RegistryAutoappend3' in self.registry.sessions:
            del(self.registry.sessions['RegistryAutoappend3'])
        people = self.registry.people
        self.person = people.create('TestRegistryAutoappend')
        sessions = self.person.sessions
        self.session1 = sessions.create('RegistryAutoappend1')
        self.session2 = sessions.create('RegistryAutoappend2')
        registerKey = self.person.getRegisterKeyValue()
        self.registryPath = 'people/%s/sessions/%s' % (
            registerKey, 'RegistryAutoappend1')
        super(AutodeleteViewTestCase, self).setUp()

    def tearDown(self):
        super(AutodeleteViewTestCase, self).tearDown()
        while 'RegistryAutoappend3' in self.registry.sessions:
            del(self.registry.sessions['RegistryAutoappend3'])
        while 'RegistryAutoappend2' in self.registry.sessions:
            del(self.registry.sessions['RegistryAutoappend2'])
        while 'RegistryAutoappend1' in self.registry.sessions:
            del(self.registry.sessions['RegistryAutoappend1'])
        while 'TestRegistryAutoappend' in self.registry.people:
            del(self.registry.people['TestRegistryAutoappend'])

    def checkResponseContent(self):
        self.failIf('RegistryAutoappend1' in self.person.sessions, self.person.sessions.keys()) 
        self.failUnless('RegistryAutoappend2' in self.person.sessions) 
        self.requiredResponseContent = '"OK"'
        self.failUnlessResponseContent()
        


class TestRegistryAutodeleteView(AutodeleteViewTestCase):

    pass

