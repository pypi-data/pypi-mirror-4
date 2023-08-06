from dm.dom.stateful import *

class Image(DatedStatefulObject):
    "Registered image."

    isUnique = False
    
    file = ImageFile()

