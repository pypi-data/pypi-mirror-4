"""A generic sub-domain for temporal persistence."""

from dm.dom.base import DomainObjectRegister, DomainObject
from dm.dom.meta import DateTime, String, Integer
from dm.ioc import RequiredFeature




# Todo: Constraints regarding stateful requirements of temporal objects.

class BaseTemporalCollection(DomainObjectRegister):
    """Base class for historical registers."""

    ownerName = 'parent'
    timepoint = RequiredFeature('Timepoint')

    def getCreateTime(self):
        return self.timepoint.recorded

    def getFindTime(self):
        return self.timepoint.recorded

    def create(self, dateCreated=None, loadedList=None, **kwds):
        if dateCreated == None:
            dateCreated = self.getCreateTime()
        return super(BaseTemporalCollection, self).create(
            dateCreated=dateCreated, __loadedList__=loadedList, **kwds
        )

    def findFirstDomainObject(self, loadedList=None):
        referenceTime = self.getFindTime()
        return super(BaseTemporalCollection, self).findFirstDomainObject(
            __loadedList__=loadedList,
            __dateCreatedOnOrBefore__=referenceTime
        )

    def getCurrent(self):
        loadedList = set([self.owner])
        return self.findFirstDomainObject(loadedList=loadedList)
  

class TemporalCollection(BaseTemporalCollection):
    """Register for simple history of values."""

    def create(self, recordedValue, loadedList=None, dateCreated=None):
        return super(TemporalCollection, self).create(
            recordedValue=recordedValue,
            loadedList=loadedList,
            dateCreated=dateCreated,
        )


class BitemporalActualCollection(TemporalCollection):
    """Register for simple history of actual values."""

    def getCreateTime(self):
        return self.timepoint.actual

    def getFindTime(self):
        return self.timepoint.actual


class BitemporalCollection(BaseTemporalCollection):
    """Register for history of recorded history of actual values."""

    def create(self, recordedValue, loadedList=None, dateCreated=None):
        oldHistory = self.findCurrentHistory(loadedList=loadedList)
        newHistory = self.createNewHistory(loadedList=loadedList)
        if oldHistory:
            oldActuals = oldHistory.getActualsRegister()
            newActuals = newHistory.getActualsRegister()
            for oldActual in oldActuals:
                newActual = newActuals.create(
                    recordedValue=oldActual.recordedValue,
                    loadedList=loadedList,
                    dateCreated=oldActual.dateCreated
                )
        newHistory.recordedValue = recordedValue
        newHistory.save()
        return newHistory

    def findCurrentHistory(self, loadedList=None):
        return super(
            BitemporalCollection, self
        ).findFirstDomainObject(loadedList=loadedList)

    def createNewHistory(self, loadedList=None):
        return super(
            BitemporalCollection, self
        ).create(loadedList=loadedList)

    def findFirstDomainObject(self, loadedList=None):
        history = self.findCurrentHistory(loadedList=loadedList)
        if history:
            actualsRegister = history.getActualsRegister()
            return actualsRegister.findFirstDomainObject(loadedList)
        else:
            return None

    def getActualsRegister(self, history):
        actualsMeta = history.meta.attributeNames['recordedValue']
        return actualsMeta.createTemporalCollection(history)


class BaseTemporal(DomainObject):

    isUnique = False
    isConstant = True
    sortOnName = 'dateCreated'
    sortAscending = False

    dateCreated = DateTime(isIndexed=True, isRequired=True)
    parent = Integer(default=1)  # This gets overidden.

    ownerNames = ['parent', 'temporalHistory']

    def makeTemporalName(self, className, attrName=None):
        if attrName:
            return "%sHist_%s" % (className, attrName)
        else:
            return "%sHist" % className

    makeTemporalName = classmethod(makeTemporalName)

    def getSortOnValue(self):
        return (self.dateCreated, self.id)


class TemporalProperty(BaseTemporal):

    registerClass = TemporalCollection
    recordedValue = String(default='')  # This gets overidden.


class BitemporalActual(TemporalProperty):

    registerClass = BitemporalActualCollection


class BitemporalProperty(BaseTemporal):

    registerClass = BitemporalCollection

    def getActualsRegister(self):
        actualsMeta = self.meta.attributeNames['recordedValue']
        return actualsMeta.createTemporalCollection(self)


class TemporalRevisionCollection(BaseTemporalCollection):

    def create(self, loadedList=None, dateCreated=None):
        return super(TemporalRevisionCollection, self).create(
            loadedList=loadedList,
            dateCreated=dateCreated,
        )


class TemporalRevision(BaseTemporal):

    registerClass = TemporalRevisionCollection


class TemporalAssociateListCollection(BaseTemporalCollection):

    def create(self, recordedValue, recordedKey, loadedList=None, dateCreated=None):
        return super(TemporalAssociateListCollection, self).create(
            recordedKey=recordedKey,
            recordedValue=recordedValue,
            loadedList=loadedList,
            dateCreated=dateCreated,
        )


class TemporalAssociateList(BaseTemporal):

    registerClass = TemporalAssociateListCollection


