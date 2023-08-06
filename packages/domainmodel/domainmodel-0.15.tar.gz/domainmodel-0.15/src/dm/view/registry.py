from dm.view.base import AbstractInstanceView
from dm.view.base import AbstractListView
from dm.view.base import AbstractSearchView
from dm.view.base import AbstractFindView
from dm.view.base import AbstractCreateView
from dm.view.base import AbstractReadView
from dm.view.base import AbstractUpdateView
from dm.view.base import AbstractDeleteView
from dm.view.manipulator import HasManyManipulator

class RegistryNavigation(object):

    def __init__(self, view):
        self.view = view

    def createMajorItem(self):
        return self.createMinorItem()

    def createMinorItem(self):
        return ''

    def createMinorItems(self):
        items = []
        return items


class RegistryFieldNames(list):

    def __init__(self, *args, **kwds):
        super(RegistryFieldNames, self).__init__(*args, **kwds)


class RegistryContextSetter(object):

    def __init__(self, *args, **kwds):
        super(RegistryContextSetter, self).__init__(*args, **kwds)

    def setContext(self, view):
        pass


class RegistryView(AbstractInstanceView):

    domainClassName = ''
    manipulatedFieldNames = {}
    manipulators = {}
    contextSetters = {}
    redirectors = {}
    navigation = {}
    registryPathNames = None
    viewPosition = None

    def __init__(self, registryPath=None, actionName='', actionValue='', **kwds):
        super(RegistryView, self).__init__(**kwds)
        self.setRegistryPath(registryPath)
        self.actionName = actionName
        self.actionValue = actionValue
        self._canCreateDomainObject = None
        self._canReadDomainObject = None
        self._canUpdateDomainObject = None
        self._canDeleteDomainObject = None

    def getRegistryPathNames(self):
        if self.registryPathNames == None:
            if self.registryPath:
                self.registryPathNames = self.registryPath.split('/')
            else:
                self.registryPathNames = []
        return self.registryPathNames

    def countRegistryPathNames(self):
        return len(self.getRegistryPathNames())

    def setRegistryPath(self, registryPath):
        if registryPath != None:
            if registryPath[0] == '/':
                registryPath = registryPath[1:]
            if registryPath[-1] == '/':
                registryPath = registryPath[:-1]
        self.registryPath = registryPath

    def __repr__(self):
        return "<%s redirect='%s' redirectPath='%s' registryPath='%s' actionName='%s'>" % (
            self.__class__.__name__,
            self.redirect,
            self.redirectPath,
            self.registryPath,
            self.actionName,
        )

    def canCreateDomainObject(self):
        if self._canCreateDomainObject == None:
            self._canCreateDomainObject = self.canAccess('Create')
        return self._canCreateDomainObject

    def canReadDomainObject(self):
        if self._canReadDomainObject == None:
            self._canReadDomainObject = self.canAccess('Read')
        return self._canReadDomainObject

    def canUpdateDomainObject(self):
        if self._canUpdateDomainObject == None:
            self._canUpdateDomainObject = self.canAccess('Update')
        return self._canUpdateDomainObject

    def canDeleteDomainObject(self):
        if self._canDeleteDomainObject == None:
            self._canDeleteDomainObject = self.canAccess('Delete')
        return self._canDeleteDomainObject

    def canAccess(self, actionName=None):
        actionName = actionName or self.getAccessControlActionName()
        protectedObject = self.getManipulatedDomainObject()
        if protectedObject:
            if not protectedObject.isActionActionable(actionName):
                return False
        else:
            protectedRegister = self.getManipulatedObjectRegister()
            protectedClassName = protectedRegister.typeName
            protectedClass = self.getDomainClass(protectedClassName)
            protectedObject = protectedClass
        return self.authoriseActionObject(actionName, protectedObject)

    def getAccessControlActionName(self):
        actionName = self.actionName.capitalize()
        if actionName in ['', 'List', 'Search', 'Find']:
            return 'Read'
        else:
            return actionName

    def makeTemplatePath(self):
        return self.getViewPosition()
        
    def getViewPosition(self):
        if self.viewPosition == None:
            self.viewPosition = ''
            for i in range(0, self.countRegistryPathNames(), 2):
                self.viewPosition += self.getRegistryPathNames()[i] + '/'
            self.viewPosition += self.getTemplatePathActionName()
        return self.viewPosition

    def getTemplatePathActionName(self):
        actionName = self.actionName or "List"
        return actionName[0].lower() + actionName[1:]
        
    def isRegistryPathToRegister(self):
        return self.countRegistryPathNames() % 2
    
    def getManipulatedObjectRegister(self):
        if self.isRegistryPathToRegister():
            registerPathNames = self.getRegistryPathNames()[:]
        else:
            registerPathNames = self.getRegistryPathNames()[:-1]
        owner = self.registry
        register = self.registry
        for name in registerPathNames:
            if owner:
                if not name:
                    msg = "Path names error: %s" % str(registerPathNames)
                    raise Exception, msg
                register = getattr(owner, name)
                owner = None
            else:
                owner = register[name]
        return register

    def getDomainObject(self):
        return self.getRegistryDomainObject()
    
    def getManipulatedDomainObject(self):
        return self.getRegistryDomainObject()
    
    def getRegistryDomainObject(self):
        if self.domainObject == None:
            if not self.isRegistryPathToRegister():
                objectRegister = self.getManipulatedObjectRegister()
                if self.getRegistryPathNames() and objectRegister:
                    registerKey = self.getRegistryPathNames()[-1]
                    self.domainObject = objectRegister[registerKey]
        return self.domainObject

    def setContext(self):
        super(RegistryView, self).setContext()
        if self.isRegistryPathToRegister():
            registerName = self.getRegistryPathNames()[-1]
        else:
            registerName = self.getRegistryPathNames()[-2]
        
        self.context.update({
            'registryPath'  : self.registryPath,
            'registryAttribute'  : self.getRegistryPathNames()[0],
            'registerName' : registerName,
            'registerNameTitle' : registerName[0].capitalize()+registerName[1:],
            'domainClassName' : self.getManipulatedObjectRegister().typeName,
            'actionName'    : self.actionName,
        })
        # todo: Write tests for this.
        contextSetter = self.getContextSetter()
        if contextSetter != None:
            contextSetter.setContext(self)

    def getContextSetter(self):
        viewPosition = self.getViewPosition()
        if viewPosition in self.contextSetters:
            return self.contextSetters[viewPosition]
        return None

    def getManipulatorClass(self):
        viewPosition = self.getViewPosition()
        if viewPosition in self.manipulators:
            manipulatorClass = self.manipulators[viewPosition]
        else:
            manipulatorClass = HasManyManipulator
        return manipulatorClass

    def getManipulatedFieldNames(self):
        viewPosition = self.getViewPosition()
        if viewPosition in self.manipulatedFieldNames:
            fieldNames = self.manipulatedFieldNames[viewPosition]
        else:
            fieldNames = []
        return fieldNames

    def getAssociationObject(self): # smell: refused bequest
        return None

    def makePostManipulateLocation(self):
        viewPosition = self.getViewPosition()
        if viewPosition in self.redirectors:
            redirectorClass = self.redirectors[viewPosition]
            redirector = redirectorClass(view=self)
            locationPath = redirector.createLocationPath()
        else:
            locationPath = self.defaultPostManipulateLocation()
        return locationPath

    def setMinorNavigationItems(self):
        viewPosition = self.getViewPosition()
        if viewPosition in self.navigation:
            navigationClass = self.navigation[viewPosition]
            navigation = navigationClass(view=self)
            self.minorNavigation = navigation.createMinorItems()
        else:
            self.minorNavigation = []

    def getMajorNavigationItem(self):
        majorItem = ''
        viewPosition = self.getViewPosition()
        if viewPosition in self.navigation:
            navigationClass = self.navigation[viewPosition]
            navigation = navigationClass(view=self)
            majorItem = navigation.createMajorItem()
        if not majorItem:
            majorItem = self.path
        return majorItem

    def getMinorNavigationItem(self):
        minorItem = ''
        viewPosition = self.getViewPosition()
        if viewPosition in self.navigation:
            navigationClass = self.navigation[viewPosition]
            navigation = navigationClass(view=self)
            minorItem = navigation.createMinorItem()
        if not minorItem:
            minorItem = self.path
        return minorItem


class RegistryListView(RegistryView, AbstractListView):
    
    def __init__(self, actionName='list', **kwds):
        kwds['actionName'] = actionName
        super(RegistryListView, self).__init__(**kwds)


class RegistryListallView(RegistryListView):
    
    def __init__(self, actionName='list', **kwds):
        kwds['actionName'] = actionName
        super(RegistryListallView, self).__init__(**kwds)

    def setContext(self, **kwds):
        super(RegistryListallView, self).setContext(**kwds)
        self.context.update({
            'showRegisterTable': True,
            'showRegisterIndex': True,
            'showRegisterAllLink': False,
        })

    def makeTemplatePath(self):
        return self.getViewPosition() + 'all'
        

class RegistrySearchView(RegistryView, AbstractSearchView):

    def __init__(self, actionName='search', **kwds):
        kwds['actionName'] = actionName
        super(RegistrySearchView, self).__init__(**kwds)

    def searchManipulatedRegister(self):
        register = self.getManipulatedObjectRegister()
        # todo: factor out 'startsWith' and 'userQuery' attributes
        if self.actionValue:
            if self.actionName == 'find':
                actionValueCap = self.actionValue.capitalize()
                searchResults = register.startsWith(actionValueCap)
            if self.actionName == 'search':
                searchResults = register.search(self.actionValue)
        elif self.startsWith:
            startsWithCap = self.startsWith.capitalize()
            searchResults = register.startsWith(startsWithCap)
        elif self.userQuery:
            searchResults = register.search(self.userQuery)
        resultsList = [i for i in searchResults]
        return resultsList


class RegistryFindView(RegistryView, AbstractFindView):

    def __init__(self, actionName='find', **kwds):
        kwds['actionName'] = actionName
        super(RegistryFindView, self).__init__(**kwds)
        if self.actionName:
            self.startsWith = self.actionValue
        
    def findDomainObjects(self):
        domainObjectRegister = self.getManipulatedObjectRegister()
        searchResults = domainObjectRegister.startsWith(self.startsWith)
        resultsList = [i for i in searchResults]
        return resultsList


class RegistryCreateView(RegistryView, AbstractCreateView):

    def __init__(self, actionName='create', **kwds):
        kwds['actionName'] = actionName
        super(RegistryCreateView, self).__init__(**kwds)

    def setContext(self):
        super(RegistryCreateView, self).setContext()

    def getManipulatedDomainObject(self):
        return None

    def defaultPostManipulateLocation(self):
        locationPath = '/'+ self.registryPath +'/'
        locationPath += str(self.domainObject.getRegisterKeyValue()) +'/'
        return locationPath

    
class RegistryReadView(RegistryListView, AbstractReadView):

    def __init__(self, actionName='read', **kwds):
        kwds['actionName'] = actionName
        super(RegistryReadView, self).__init__(**kwds)
        self.associationObject = None
        
    def getDomainObjectAsNamedValues(self):
        domainObject = self.getDomainObject()
        if not domainObject:
            raise Exception, "No domain object for registry path: %s" %self.registryPath
        namedValues = domainObject.asNamedValues()
        manipulator = self.getManipulator()
        # Todo: Refactor this to use the pickers.
        filteredNamedValues = []
        if manipulator and manipulator.fieldNames:
            for fieldName in manipulator.fieldNames:
                for namedValue in namedValues:
                    if namedValue['name'] == fieldName:
                        filteredNamedValues.append(namedValue)
        else:
            for namedValue in namedValues:
                metaAttrName = namedValue['name']
                metaAttr = domainObject.meta.attributeNames[metaAttrName]
                if not manipulator.isAttrExcluded(metaAttr):
                    filteredNamedValues.append(namedValue)
        return filteredNamedValues


class RegistryUpdateView(RegistryReadView, AbstractUpdateView):

    def __init__(self, actionName='update', **kwds):
        kwds['actionName'] = actionName
        super(RegistryUpdateView, self).__init__(**kwds)

    def defaultPostManipulateLocation(self):
        locationPath = '/'+ self.registryPath +'/'
        return locationPath


class RegistryDeleteView(RegistryReadView, AbstractDeleteView):

    def __init__(self, actionName='delete', **kwds):
        kwds['actionName'] = actionName
        super(RegistryDeleteView, self).__init__(**kwds)

    def defaultPostManipulateLocation(self):
        registryPath = '/'.join(self.getRegistryPathNames()[0:-1])
        return '/' + registryPath + '/'


def view(request, registryPath, actionName=''):
    pathNames = registryPath.split('/')
    if not actionName:
        if len(pathNames) % 2:
            actionName = 'list'
        else:
            actionName = 'read'
    if actionName == 'list':
        viewClass = RegistryListView
    elif actionName == 'create':
        viewClass = RegistryCreateView
    elif actionName == 'read':
        viewClass = RegistryReadView
    elif actionName == 'update':
        viewClass = RegistryUpdateView
    elif actionName == 'delete':
        viewClass = RegistryDeleteView
    elif actionName == 'undelete':
        viewClass = RegistryUndeleteView
    elif actionName == 'purge':
        viewClass = RegisryPurgeView
    else:
        raise Exception, "No view class for actionName '%s'." % actionName
    view = viewClass(
        request=request,
        registryPath=registryPath,
        actionName=actionName
    )
    return view.getResponse()

