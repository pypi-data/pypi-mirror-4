from dm.ioc import RequiredFeature
from dm.view.base import SessionView
from dm.dom.registry import RegistryPathGetter
from dm.on import json
import re

moddebug = False


class ViewWidget(SessionView):

    def canAccess(self):
        return True

    def markNavigation(self):
        pass

    def setContext(self, **kwds):
        pass

    def getJsonData(self):
        pass
    

class SimpleWidget(object):

    pass


class Autocompleter(SimpleWidget):

    def complete(self, queryString):
        data = []
        data.append(queryString)
        data.append('errors')
        data.append('errors1')
        data.append('errors2')
        data.append('errors3')
        data.append('errors4')
        return data


class RegistryAutocompleter(Autocompleter):

    registry = RequiredFeature('DomainRegistry')

    def __init__(self, *args, **kwds):
        super(Autocompleter, self).__init__(*args, **kwds)

    def complete(self, queryString, registryPath):
        pathGetter = RegistryPathGetter(registryPath)
        objectRegister = pathGetter.getRegister()
        optionsRegister = objectRegister.getOptionsRegister()
        results = optionsRegister.search(queryString, spaceSplit=False)
        return ["%s (#%s)" % (i.getLabelValue(), i.id) for i in results]


class RpcView(SessionView):

    def __init__(self, *args, **kwds):
        super(RpcView, self).__init__(*args, **kwds)

    def canAccess(self):
        return self.canReadSystem()

    def markNavigation(self):
        pass

    def createContent(self):
        self.content = ''


class JsonView(RpcView):

    def __init__(self, *args, **kwds):
        super(JsonView, self).__init__(*args, **kwds)
        self.jsonString = ''
        self.jsonHash = {'method': 'default'}
        self.jsonParams = ['']
        self.message = '' 

    def createContent(self):
        try:
            self.runProcedure()
            self.dumpMessageAsJsonContent()
        except Exception, inst:
            message = "AJAX View Error: %s" % str(inst)
            self.logger.warning(message)
            raise

    def setContext(self):
        pass

    def jsonStringToData(self, string):
        try:
            return json.loads(string)
        except Exception, inst:
            msg = "Can't convert JSON string to data structure: %s" % string
            self.logger.error(msg)
            raise Exception(msg)

    def jsonDataToString(self, string):
        try:
            return json.dumps(string)
        except Exception, inst:
            msg = "Can't convert data structure to JSON string: %s" % string
            self.logger.error(msg)
            raise Exception(msg)

    def readJsonPost(self):
        self.jsonHash = {}
        if self.request.POST:
            try:
                self.jsonString = self.request.POST.keys()[0]
                if moddebug and self.isDebug:
                    msg = "AJAX JSON raw string: %s" % self.jsonString
                    self.logger.debug(msg)
                self.jsonHash = self.jsonStringToData(self.jsonString)
                if moddebug and self.isDebug:
                    self.logger.debug("AJAX Request: %s" % self.jsonHash)
            except Exception, inst:
                raise Exception, "AJAX JSON Error: %s" % str(inst)
        elif self.isDebug:
            self.logger.debug("AJAX Error: No POST params in HTTP request.")

    def runProcedure(self, procedureName='default'):
        self.readJsonPost()
        procedureName = self.jsonHash['method']
        if self.isDebug:
            self.logger.debug("AJAX Procedure: %s" % procedureName)
        self.jsonParams = self.jsonHash['params']
        if self.isDebug:
            self.logger.debug("AJAX Params: %s" % self.jsonParams)
        if procedureName == '':
            procedureName = 'default'
        procedureMethod = getattr(self, 'do_'+procedureName)
        procedureMethod()

    def dumpMessageAsJsonContent(self):
        if self.isDebug:
            self.logger.debug("AJAX Response: %s" % self.message)
        try:
            self.content = self.jsonDataToString(self.message)
        except Exception, inst:
            raise Exception, "JSON Dump Error: %s" % str(inst)
        if moddebug and self.isDebug:
            self.logger.debug("AJAX JSON: %s" % self.content)

    def do_default(self):
        self.message = 'default message'


class AutocompleterView(JsonView):

    def __init__(self, completer, queryName='value', *args, **kwds):
        super(AutocompleterView, self).__init__(*args, **kwds)
        self.completer = completer
        self.queryName = queryName

    def canAccess(self):
        return self.canReadSystem()

    def runProcedure(self):
        queryString = self.getRequestParam(self.queryName)
        self.message = self.completer.complete(queryString)


class RegistryAutocompleterView(AutocompleterView):

    def canAccess(self):
        return self.canReadSystem()

    def runProcedure(self):
        queryString = self.getRequestParam(self.queryName)
        self.logger.debug("Autocompleter queryString: %s" % queryString)
        registryPath = self.getRequestParam('registryPath')
        self.logger.debug("Autocompleter registryPath: %s" % registryPath)
        if registryPath:
            self.message = self.completer.complete(queryString, registryPath)
        else:
            self.logger.error("No registryPath value in request params.")
            self.message = []
            self.setRedirect('/')


class RegistryAutopathView(JsonView):

    modelObject = None
    registryPath = None

    def canAccess(self):
        return self.canUpdate(self.getModelObject()) or self.canUpdateSystem()

    def getModelObject(self):
        if not self.modelObject:
            registryPath = self.getRegistryPath()
            o = self.registry.path.open(registryPath)
            self.modelObject = o
        return self.modelObject

    def getRegistryPath(self):
        if self.registryPath == None:
            registryPath = self.getRequestParam('registryPath')
            if not registryPath:
                raise Exception, "No registryPath in request."
            if registryPath[0] == '#':
                registryPath = registryPath[1:]
            self.logger.debug("Appender registryPath: %s" % registryPath)
            self.registryPath = registryPath
        return self.registryPath


class RegistryAutoappenderView(RegistryAutopathView):

    objectRegister = None
    targetAttribute = None
    completedString = None
    pathGetter = None

    # Todo: Finish refactoring this to actually use the inherited class.
    def runProcedure(self):
        self.message = ''
        register = self.getObjectRegister()
        optionKwds = self.createOptionKwds()
        # Todo: Rework association objects to be explicit in the model.
        if register.metaAttr and register.metaAttr.isKeyDomainObject():
            options = register.getOptionsRegister()
            optionKwds = self.createOptionKwds()
            selection = options.findDomainObjects(**optionKwds)
            if selection:
                for option in selection:
                    if not option in register.keys():
                        register.create(option)
                        self.message = 'OK'
            else:
                option = options.create(**optionKwds)
                register.create(option)
                self.message = 'OK'
        else:
            objectKwds = self.createOptionKwds()
            if not register.findDomainObjects(**objectKwds):
                register.create(**objectKwds)
                self.message = 'OK'

    def createOptionKwds(self):
        optionKwds = {
            self.getTargetAttribute(): self.getCompletedString()
        }
        return optionKwds

    def getObjectRegister(self):
        if self.objectRegister == None:
            self.objectRegister = self.getPathGetter().getRegister()
        return self.objectRegister
        
    def getPathGetter(self):
        if self.pathGetter == None:
            self.pathGetter = RegistryPathGetter(self.getRegistryPath())
        return self.pathGetter

    def getCompletedString(self):
        if self.completedString == None:
            completed = self.getRequestParam('completedString')
            self.logger.debug("Appender string: %s" % completed)
            if (not completed) and (completed != ''):
                raise Exception, "No completedString in request: %s" % (
                    self.getRequestParams()
                )
            else:
                self.completedString = re.sub('\s\(#\d+\)\s*$', '', completed)
        return self.completedString

    def getTargetAttribute(self):
        if self.targetAttribute == None:
            targetAttribute = self.getRequestParam('targetAttribute')
            # Python keywords must be strings (request params often unicode).
            # Todo: Write test to pass unicode in here.
            targetAttribute = str(targetAttribute)
            self.logger.debug("Appender targetAttribute: %s" % targetAttribute)
            if not targetAttribute:
                raise Exception, "No targetAttribute in request."
            self.targetAttribute = targetAttribute
        return self.targetAttribute


class RegistryAutodeleteView(RegistryAutopathView):

    def runProcedure(self):
        self.getModelObject().delete()
        self.message = 'OK'
    

class RegistryAttrupdateView(RegistryAutopathView):

    def runProcedure(self):
        domainObject = self.getModelObject()
        attrName = self.getRequestParam('attrName')
        attrValue = self.getRequestParam('attrValue')
        if attrName:
            # Todo: Process the attrValue properly.
            attrValue = attrValue
            setattr(domainObject, attrName, attrValue)
            domainObject.save()
            self.message = 'OK'


