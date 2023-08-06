from dm.dom.stateful import *
import uuid

def makeUuid():
    return

class ApiKey(SimpleObject):

    person = HasA('Person', isRequired=True)
    key = String(isRequired=True, default=lambda: str(uuid.uuid4()))

