import dm.exceptions
from dm.dom.base import *
from dm.dom.meta import *
from dm.ioc import *

class State(NamedObject):
    "Recorded state of StatefulObject instances."

    name = String(isIndexed=True, isRequired=True, regex='', isSystem=True)
    isConstant = True

    def __init__(self):
        super(State, self).__init__()
        self.behaviour = None

    def deleteObject(self, domainObject):
        self.getBehaviour().deleteObject(domainObject)

    def approveObject(self, domainObject):
        self.getBehaviour().approveObject(domainObject)

    def undeleteObject(self, domainObject):
        self.getBehaviour().undeleteObject(domainObject)

    def purgeObject(self, domainObject):
        self.getBehaviour().purgeObject(domainObject)

    def getBehaviour(self):
        if not self.behaviour:
            self.checkBehavioursHaveStates()
            self.checkName()
            self.behaviour = self.createBehaviour()
        return self.behaviour

    def checkBehavioursHaveStates(self):
        abstractStateClass = State.__dict__['AbstractStateBehaviour']
        if not abstractStateClass.states:
            abstractStateClass.states = self.registry.states

    def checkName(self):
        if not self.name:
            raise Exception("State has no name: %s" % self)

    def createBehaviour(self):
        stateName = self.name
        behaviourClassName = stateName[0].upper()+stateName[1:]+'Behaviour' 
        behaviourClass = State.__dict__[behaviourClassName]
        return behaviourClass()

    class AbstractStateBehaviour(object):

        states = None
    
        def deleteObject(self, domainObject):
            pass
            
        def approveObject(self, domainObject):
            pass
            
        def undeleteObject(self, domainObject):
            pass
            
        def purgeObject(self, domainObject):
            pass
    
    class ActiveBehaviour(AbstractStateBehaviour):
    
        def deleteObject(self, domainObject):
            domainObject.deleteAggregates()
            domainObject.raiseDelete()
            domainObject.decacheItem()
            domainObject.state = self.states['deleted']
            domainObject.saveSilently()
            domainObject.raiseAfterDelete()
            
        def purgeObject(self, domainObject):
            message = 'An active object cannot be purged: %s' % str(domainObject)
            raise dm.exceptions.KforgeDomError(message) 
    
    class DeletedBehaviour(AbstractStateBehaviour):
    
        def undeleteObject(self, domainObject):
            domainObject.decacheItem()
            domainObject.state = self.states['active']
            domainObject.saveSilently()
            domainObject.raiseUndelete()
    
        def purgeObject(self, domainObject):
            domainObject.raisePurge()
            domainObject.purgeAggregates()
            domainObject.dropHasAs()
            domainObject.decacheItem()
            domainObject.state = None 
            domainObject.destroySelf()

    class PendingBehaviour(AbstractStateBehaviour):
    
        def approveObject(self, domainObject):
            domainObject.decacheItem()
            domainObject.state = self.states['active']
            domainObject.saveSilently()
            domainObject.raiseApprove()
    
        def deleteObject(self, domainObject):
            domainObject.deleteAggregates()
            domainObject.raiseDelete()
            domainObject.decacheItem()
            domainObject.state = self.states['deleted']
            domainObject.saveSilently()
            
        def purgeObject(self, domainObject):
            message = 'A pending object cannot be purged: %s' % str(domainObject)
            raise dm.exceptions.KforgeDomError(message) 
    
