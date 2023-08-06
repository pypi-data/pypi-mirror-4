import dm.times

"""
Timepoint is used with the temporal model classes, used to represent a point
in universal time. There are two properties, recorded and actual.

All temporal aspects are sensitive to the time when values are recorded
("recorded time").  The usual assumption is that recording happens when
changes in the domain happen, so recorded time and actual time are identical.

By setting the timepoint's 'recorded' property, you retrieve values
from a recorded history of values (so you can find which value was recorded at
a given point in time).

However, some aspects are bi-temporal and are sensitive to when the actual
changes in the domain were thought to occur in distinction from when the
changes are recorded.

By setting the timepoint's 'actual' property you can retrieve values from the
currently recorded history of actual values. By also setting the 'recorded' 
property, you retrieve values from an older history.

Just setting the timepoint's 'recorded' property and retrieving the object
will return the "most recent actual" value, as it was recorded in the past.

So the primary time-frame is "when things were recorded". In addition to this,
bi-temporal values can vary across "when things actually happened". Changing 
only the 'actual' time is like asking "what do we currently think it was then".
Changing only the 'recorded' time is like asking "what did we think it was".

"""

class Timepoint(object):    

    def __init__(self):
        self.resetToPresent()

    def resetToPresent(self):
        self._recorded = None
        self._actual = None

    def isReset(self):
        return self._recorded == None and self._actual == None

    def reset(self):
        self.resetToPresent()

    def getRecorded(self):
        if self._recorded != None:
            return self._recorded
        else:
            return self.now()

    def setRecorded(self, value):
        self._recorded = value

    recorded = property(getRecorded, setRecorded)

    def getActual(self):
        if self._actual != None:
            return self._actual
        else:
            return self.now()

    def setActual(self, value):
        self._actual = value

    actual = property(getActual, setActual)
    
    def now(self):
        return dm.times.getUniversalNow()

