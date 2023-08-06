from dm.view.base import SessionView
from dm.view.base import DomainObjectManipulator
from dm.view.base import HasManyManipulator
from dm.dom.base import DomainObject
from dm.dom.base import DomainObjectRegister
from dm.dom.stateful import PagedCompoundRegister
from dm.dictionarywords import SYSTEM_VERSION
from dm.dictionarywords import URI_PREFIX
from dm.util.datastructure import MultiValueDict
from dm.on import json
import traceback
from dm.exceptions import *
from dm.dom.pickers import GetInitableAttributes
from dm.dom.pickers import GetReadableAttributes
from dm.dom.pickers import GetEditableAttributes
import inspect
from dm.dictionarywords import API_KEY_HEADER_NAME
import os

class ApiView(SessionView):

    def getAuthenticatedPerson(self):
        self.setSessionFromCookie()
        person = super(ApiView, self).getAuthenticatedPerson()
        if person == None:
            headerName = self.dictionary[API_KEY_HEADER_NAME]
            if not headerName:
                raise Exception, "Dictionary word '%s' not set." % API_KEY_HEADER_NAME
            headerName = 'HTTP_%s' % headerName.upper().replace('-', '_')
            if headerName in self.request.META:
                headerValue = self.request.META[headerName]
                apiKeys = self.registry.apiKeys.findDomainObjects(key=headerValue)
                if len(apiKeys) == 1:
                    person = apiKeys[0].person
        return person

    def canAccess(self):
        return True

    def getRequestRegistryPath(self):
        if not hasattr(self, '_registryPath'):
            path = self.path
            if path[0:4] == '/api':
                path = path[4:]
            if path and path[-1] == '/':
                path = path[:-1]
            self._registryPath = path
        return self._registryPath

    def trimuris(self, data, manipulator, absoluteUriPrefix):
        def trimuri(uri):
            if type(uri) in [int, long]:
                pass
            elif uri.startswith(absoluteUriPrefix):
                uri = uri[len(absoluteUriPrefix):]
            return uri
        fieldedMetaAttrs = manipulator.fieldedMetaAttrs
        if manipulator.extnManipulator:
            fieldedMetaAttrs += manipulator.extnManipulator.fieldedMetaAttrs
        for metaAttr in fieldedMetaAttrs:
            if metaAttr.name not in data:
                continue
            if metaAttr.isAssociateList:
                data[metaAttr.name] = [trimuri(i) for i in data[metaAttr.name]]
            elif metaAttr.isDomainObjectRef:
                data[metaAttr.name] = trimuri(data[metaAttr.name])

    def getResponse(self):
        locationHeader = ''
        self.content = ''
        uriPrefix = self.dictionary[URI_PREFIX] + '/api'
        absoluteUriPrefix = self.buildAbsoluteUri(uriPrefix)
        accessedBy = None
        if self.session:
            accessedBy = self.session.person.name
        try:
            self.setPathFromRequest()
            path = self.getRequestRegistryPath()
            try:
                if path != '/proc':
                    dereference = self.registry.dereference(path, __accessedBy__=accessedBy)
                    dereferencedObject = dereference.target
                    dereferencedOwner = dereference.context
            # Todo: Define exception class for dereferencing error.
            except KforgeRegistryKeyError:
                self.responseStatusCode = 404
            except KforgeAttributeError:
                self.responseStatusCode = 404
            else:
                methodName = self.getMethodName()
                isRegistry = False
                isRegister = False
                isEntity = False
# Todo: In Kforge, authoriseActionObject() that picks off top-level entity. If it's a project, then pass it into super authoriseActionObject() method so project roles are taken into account.
                if path == '/proc':
                    if not self.canReadSystem():
                        # Forbidden.
                        self.responseStatusCode = 403
                    if methodName in ['GET']:
                        self.setResponseData({
                            'version': self.dictionary[SYSTEM_VERSION],
                            'vsize': self.getVsize(),
                            'pid': os.getpid(),
                        })
                elif dereferencedObject == self.registry:
                    # Registry.
                    if not self.canReadSystem():
                        # Forbidden.
                        self.responseStatusCode = 403
                    if methodName in ['GET']:
                        # OK.
                        resources = []
                        for (name, value) in inspect.getmembers(self.registry):
                            if issubclass(type(value), DomainObjectRegister):
                                domainClass = value.getDomainClass()
                                if self.authoriseActionObject('Read', domainClass):
                                    # Translate attributes to URLs.
                                    resourceUri = absoluteUriPrefix + '/' + name
                                    resources.append(resourceUri)
                        self.setResponseData(resources)
                        #self.setResponseData({'resources': resources})
                    else:
                        # Forbidden.
                        self.responseStatusCode = 403
                elif isinstance(dereferencedObject, PagedCompoundRegister):
                    # Paged register.
                    # Not supported.
                    self.responseStatusCode = 404
                elif isinstance(dereferencedObject, DomainObjectRegister):
                    # Register.
                    objectRegister = dereferencedObject
                    domainClass = objectRegister.getDomainClass()
                    if methodName in ['GET']:
                        # Register-Get.
                        if not self.authoriseActionObject('Read', domainClass):
                            # Forbidden.
                            self.responseStatusCode = 403
                        else:
                            # OK.
                            resources = objectRegister.getUris(absoluteUriPrefix, __accessedBy__=accessedBy)
                            self.setResponseData(resources)
                    elif methodName in ['POST']:
                        # Register-Post.
                        if not self.authoriseActionObject('Create', domainClass):
                            # Forbidden.
                            self.responseStatusCode = 403
                        else:
                            # Not forbidden...
                            data = self.getRequestData()
                            manipulator = HasManyManipulator(objectRegister, pickerClass=GetInitableAttributes)
                            self.trimuris(data, manipulator, absoluteUriPrefix)
                            validationErrors = {}

                            # Create.
                            try:
                                manipulator.create(data)
                            except FormError, inst:
                                # Bad request.
                                self.setResponseData(inst.errors)
                                self.responseStatusCode = 400
                            else:
                                # OK.
                                self.responseStatusCode = 201
                                locationHeader = manipulator.domainObject.getUri(absoluteUriPrefix)
                    else:
                        raise Exception, "Method '%s' not supported on registers." % methodName
                elif isinstance(dereferencedObject, DomainObject):
                    # Entity.
                    domainObject = dereferencedObject
                    objectRegister = dereference.context
                    if methodName in ['GET']:
                        # Entity-Get.
                        if not self.authoriseActionObject('Read', domainObject):
                            # Forbidden.
                            self.responseStatusCode = 403
                        else:
                            # OK.
                            manipulator = HasManyManipulator(objectRegister, domainObject, pickerClass=GetReadableAttributes)
                            data = manipulator.domainObjectAsDictValues(absoluteUriPrefix=absoluteUriPrefix)
                            if manipulator.extnManipulator:
                                extnData = manipulator.extnManipulator.domainObjectAsDictValues(absoluteUriPrefix=absoluteUriPrefix)
                                data.update(extnData)
                            # Translate keys to URLs.
                            #for attrName in manipulator.fields.keys():
                            #    metaAttr = manipulator.metaObject.attributeNames[attrName]
                            #    if metaAttr.isAssociateList:
                            #        keys = data[attrName]
                            #        prefix = self.dictionary[URI_PREFIX]
                            #        associateClass = metaAttr.getDomainClass()
#
#                                    if metaAttr.key == 'id':
#                                        keyAttr = None
#                                    else:
#                                        keyAttr = associateClass.meta.attributeNames[metaAttr.key]
#                                    if keyAttr and keyAttr.isDomainObjectRef:
#                                        # Infer keys are many-many associates (values merely associations).
#                                        registryAttrName = keyAttr.getRegistryAttrName(domainObject)
#                                        prefix += '/api' + '/' + registryAttrName + '/'
#                                    else:
#                                        prefix += '/api' + path + '/' + attrName + '/'
#                                    urls = [self.buildAbsoluteUri(prefix + key) for key in keys]
#                                    data[attrName] = urls
#                                elif metaAttr.isDomainObjectRef:
#                                    key = data[attrName]
#                                    registryAttrName = metaAttr.getRegistryAttrName(domainObject)
#                                    prefix = self.dictionary[URI_PREFIX]
#                                    prefix += '/api' + '/' + registryAttrName + '/'
#                                    data[attrName] = self.buildAbsoluteUri(prefix + key)
                            self.setResponseData(data)
                    elif methodName in ['PUT', 'POST']:
                        # Entity-Put.
                        if not self.authoriseActionObject('Update', domainObject):
                            # Forbidden.
                            self.responseStatusCode = 403
                        else:
                            # Not forbidden...
                            data = self.getRequestData()
                            manipulator = DomainObjectManipulator(objectRegister, domainObject, pickerClass=GetEditableAttributes)
                            self.trimuris(data, manipulator, absoluteUriPrefix)
                            #for attrName in manipulator.fields.keys():
                            #    metaAttr = manipulator.metaObject.attributeNames[attrName]
                            #    if metaAttr.isAssociateList:
                            #        urls = data[attrName]
                            #        keys = [url.strip('/').split('/')[-1] for url in urls]
                            #        data[attrName] = keys
                            #    elif metaAttr.isDomainObjectRef:
                            #        url = data[attrName]
                            #        key = url.strip('/').split('/')[-1]
                            #        data[attrName] = key
                            #validationErrors = {}
                            #for k,v in manipulator.getValidationErrors(data).items():
                            #   validationErrors[k] = v.as_text().strip('* ')
                            #if validationErrors:
                            #    # Bad request.
                            #    self.setResponseData(validationErrors)
                            #    self.responseStatusCode = 400
                            #else:

                            # Update.
                            try:
                                manipulator.update(data)
                            except FormError, inst:
                                # Bad request.
                                self.setResponseData(inst.errors)
                                self.responseStatusCode = 400
                            else:
                                # OK.
                                self.responseStatusCode = 200
                    elif methodName in ['DELETE']:
                        # Entity-Delete.
                        if not self.authoriseActionObject('Delete', domainObject):
                            # Forbidden.
                            self.responseStatusCode = 403
                        else:
                            domainObject.delete()
                            self.responseStatusCode = 200
                    else:
                        raise Exception, "Method '%s' not supported on entities." % methodName
                else:
                    raise Exception, "Path '%s' resolves to neither the registry, nor a register, nor a domain object: %s" % (path, dereferencedObject)
        except Exception, inst:
            # Internal error.
            self.responseStatusCode = 500
            self.content = ''
            msg = "API View Error: %s: %s" % (inst, traceback.format_exc())
            self.logger.error(msg)
        self.createResponse()
        self.response['Content-Type'] = 'application/json;charset=utf-8'
        if locationHeader:
            self.response['Location'] = locationHeader
        return self.response

    def getVsize(self):
        import commands
        def cmd(cmd):
            s,o = commands.getstatusoutput(cmd)
            if not s:
                return o
            else:
                raise Exception, "Command '%s' exited with non-zero status: %s %s" % (cmd, s, o)

        vsize = cmd('ps -p %d -o vsize=' % os.getpid())
        try:
            vsize = int(vsize.strip())
        except Exception, inst:
            msg = "Couldn't convert vsize string to integer value: %s: %s" % (vsize, inst)
            raise Exception, msg
        return vsize

    def getRequestData(self):
        message = self.request.POST.keys()[0]
        try:
            data = json.loads(message)
        except Exception, inst:
            raise Exception, "Couldn't load JSON from request '%s': %s" % (message, inst)
        return data

    def setResponseData(self, data):
        self.content = json.dumps(data)

