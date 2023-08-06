from dm.dom.stateful import *
from dm.on import json
import gc
import sys

class MemoryDump(DatedObject):

    dump = String(isSystem=True)

    def initialise(self, register=None):
        super(MemoryDump, self).initialise(register)
        self.dump = self.dumpMemory()
        self.isChanged = True

    def dumpMemory(self):
        objs = []
        for obj in gc.get_objects():
            objid = id(obj)
            objsize = sys.getsizeof(obj, 0)
            objtype = str(type(obj))
            referents = [id(o) for o in gc.get_referents(obj)]                
            objs.append({'id': objid, 'type': objtype, 'size': objsize, 'referents': referents})
        dump = json.dumps(objs)
        for obj in objs:
            del(obj)
        del(objs)
