import unittest
from dm.view.basetest import TestCase, ViewTestCase
from dm.view.registry import RegistryView
from dm.view.registry import RegistryListView
from dm.view.registry import RegistrySearchView
from dm.view.registry import RegistryCreateView
from dm.view.registry import RegistryReadView
from dm.view.registry import RegistryUpdateView
from dm.view.registry import RegistryDeleteView

def suite():
    suites = [
        unittest.makeSuite(TestRegistryView),
        unittest.makeSuite(TestRegistryListView),
        unittest.makeSuite(TestRegistrySearchView),
        unittest.makeSuite(TestRegistrySearchView2),
        unittest.makeSuite(TestRegistryCreateView),
        unittest.makeSuite(TestRegistryReadView),
        unittest.makeSuite(TestRegistryUpdateView),
        unittest.makeSuite(TestRegistryDeleteView),
    ]
    return unittest.TestSuite(suites)


class MockRegistryView(RegistryView):
    templatePath = 'index'

class MockRegistryListView(MockRegistryView, RegistryListView):
    pass

class MockRegistrySearchView(MockRegistryView, RegistrySearchView):
    pass

class MockRegistryCreateView(MockRegistryView, RegistryCreateView):
    pass

class MockRegistryReadView(MockRegistryView, RegistryReadView):
    pass

class MockRegistryUpdateView(MockRegistryView, RegistryUpdateView):
    pass

class MockRegistryDeleteView(MockRegistryView, RegistryDeleteView):
    pass


class RegistryViewTestCase(ViewTestCase):
    
    registryPath = 'people'
    viewerName = 'admin'

    def createViewKwds(self):
        viewKwds = super(RegistryViewTestCase, self).createViewKwds()
        viewKwds['registryPath'] = self.registryPath
        return viewKwds

    def test_actionName(self):
        self.failUnlessEqual(self.view.actionName, self.actionName)

    def test_getViewPosition(self):
        self.failUnlessEqual(self.view.getViewPosition(), self.viewPosition)


class TestRegistryView(RegistryViewTestCase):

    viewClass = MockRegistryView
    actionName = ''
    viewPosition = 'people/list'


class TestRegistryListView(RegistryViewTestCase):

    viewClass = MockRegistryListView
    actionName = 'list'
    viewPosition = 'people/list'


class TestRegistrySearchView(RegistryViewTestCase):

    viewClass = MockRegistrySearchView
    actionName = 'search'
    viewPosition = 'people/search'
    userQuery = 'admin'

    def initPost(self):
        self.POST = {
            'userQuery': self.userQuery
        }

    def test_getResponse(self):
        super(TestRegistrySearchView, self).test_getResponse()
        self.failUnless(self.view.context['domainObjectList'])
        self.failUnlessEqual(self.view.userQuery, self.userQuery)
        self.failUnlessEqual(self.view.context['userQuery'], self.userQuery)
        self.failUnlessEqual(self.view.context['objectCount'], 1)
        self.failUnlessEqual(self.view.context['isCountSingle'], True)
    
    def test_searchManipulatedRegister(self):
        self.view.userQuery = 'adm'
        results = self.view.searchManipulatedRegister()
        self.failUnlessEqual(len(results), 1)
        self.failUnless(
            hasattr(results[0], 'name'),
            "No name attribute on object '%s' in results '%s'" % (
                str(results[0]),
                str(results),
            )
        )
        self.failUnlessEqual(results[0].name, 'admin')
        self.view.userQuery = 'vis'
        results = self.view.searchManipulatedRegister()
        self.failUnlessEqual(len(results), 1)
        self.failUnlessEqual(results[0].name, 'visitor')
        self.view.userQuery = 'i'
        results = self.view.searchManipulatedRegister()
        self.failUnlessEqual(len(results), 3, [i.name for i in results])


class TestRegistrySearchView2(RegistryViewTestCase):

    viewClass = MockRegistrySearchView
    actionName = 'search'
    viewPosition = 'people/search'
    startsWith = 'ad'

    def initPost(self):
        self.POST = {
            'startsWith': self.startsWith
        }
        
    def test_getResponse(self):
        super(TestRegistrySearchView2, self).test_getResponse()
        self.failUnless(self.view.context['domainObjectList'])
        self.failUnlessEqual(self.view.startsWith, self.startsWith)
        self.failUnlessEqual(self.view.context['startsWith'], self.startsWith)
        self.failUnlessEqual(self.view.context['objectCount'], 1)
        self.failUnlessEqual(self.view.context['isCountSingle'], True)


class TestRegistryCreateView(RegistryViewTestCase):
    viewClass = MockRegistryCreateView
    actionName = 'create'
    viewPosition = 'people/create'

class TestRegistryReadView(RegistryViewTestCase):
    viewClass = MockRegistryReadView
    actionName = 'read'
    registryPath = 'people/admin'
    viewPosition = 'people/read'

class TestRegistryUpdateView(RegistryViewTestCase):
    viewClass = MockRegistryUpdateView
    actionName = 'update'
    registryPath = 'people/admin'
    viewPosition = 'people/update'

class TestRegistryDeleteView(RegistryViewTestCase):
    viewClass = MockRegistryDeleteView
    actionName = 'delete'
    registryPath = 'people/admin'
    viewPosition = 'people/delete'

