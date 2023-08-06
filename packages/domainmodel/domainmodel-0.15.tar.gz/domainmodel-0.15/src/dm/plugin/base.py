import os, shutil

from dm.ioc import *
import dm.exceptions

class PluginBase(object):
    """
    Supertype for domain model object lifetime-event listeners.
    """

    logger = RequiredFeature('Logger')
    registry = RequiredFeature('DomainRegistry')
    dictionary = RequiredFeature('SystemDictionary')
    paths = RequiredFeature('FileSystem') # Deprecated. Todo: Rename everywhere to filesystem.
    filesystem = RequiredFeature('FileSystem')

    modelExtnClassName = None
    
    def __init__(self, domainObject):
        self.domainObject = domainObject   # The application's model of this plugin.
        self.register = self.getRegister() # A register of extention model objects.

    def getModelExtnClass(self):
        if self.modelExtnClassName:
            return self.registry.getDomainClass(self.modelExtnClassName)
        else:
            return None

#    def checkDir(self):
#        pluginPath = self.getDirPath()
#        if not os.path.exists(pluginPath):
#            os.makedirs(pluginPath)
#
#    def getDirPath(self):
#        return self.paths.getPluginPath(self.domainObject)
    
    def getRegister(self):
        if self.modelExtnClassName:
            raise Exception, "Abstract method not implemented on '%s'." % (
                self.__class__
            )
        else:
            return None

    def hasRegister(self):
        return self.register != None
    
    def log(self, message):
        self.logger.info(message)

    def assertDependencies(self):
        for requiredName in self.listDependencies():
            if not requiredName in self.registry.plugins:
                raise Exception("depends on missing '%s' plugin." % requiredName)

    assertDependencies = classmethod(assertDependencies)

    def listDependencies(self):
        return []

    listDependencies = classmethod(listDependencies)

    def assertNoDependents(self):
        thisName = self.domainObject.name
        for plugin in self.registry.plugins:
            dependentSystem = plugin.getSystem()
            if not dependentSystem:
                continue
            dependentName = plugin.name
            for requiredName in dependentSystem.listDependencies():
                if requiredName == thisName:
                    msg = "dependened upon by '%s' plugin." % (dependentName)
                    raise Exception(msg)
    
    def getMetaDomainObject(self):
        return None
   
    def initialise(self, register):
        pass
   

    ## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    ## Event Handlers
    ## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    # todo: remove mention of specific event handlers from base class?
    
    def onRun(self, sender):
        pass
    
    def onCreate(self):
        "Called when this plugin domain object is created."
        pass
    
    def onDelete(self):
        "Called when this plugin domain object is deleted."
        pass
    
    ## ********************************************************************
    ## Project
    ## ********************************************************************
    
    def onProjectCreate(self, project):
        pass
    
    def onProjectUpdate(self, project):
        pass
    
    def onProjectDelete(self, project):
        pass
    
    def onProjectPurge(self, project):
        pass
    
    ## ********************************************************************
    ## Person
    ## ********************************************************************
    
    def onPersonCreate(self, person):
        pass
    
    def onPersonUpdate(self, person):
        pass
    
    def onPersonDelete(self, person):
        pass
    
    def onPersonPurge(self, person):
        pass
    
    ## ********************************************************************
    ## Service
    ## ********************************************************************
    
    def onServiceCreate(self, service):
        pass
    
    def onServiceUpdate(self, service):
        pass
    
    def onServiceDelete(self, service):
        pass
    
    def onServicePurge(self, service):
        pass
    
    ## ********************************************************************
    ## Member
    ## ********************************************************************
    
    def onMemberCreate(self, member):
        pass
    
    def onMemberDelete(self, member):
        pass
    
    def onMemberPurge(self, member):
        pass
