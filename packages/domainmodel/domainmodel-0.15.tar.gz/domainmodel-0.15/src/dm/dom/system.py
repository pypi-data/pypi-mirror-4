from dm.dom.stateful import DatedObject
from dm.dom.stateful import String
from dm.dictionarywords import SYSTEM_VERSION

class System(DatedObject):
    "Kforge installation."

    version = String(
        default=DatedObject.dictionary[SYSTEM_VERSION], isSystem=True
    )
    mode = String(isRequired=False)

    def getLabelValue(self):
        return "%s %s %s" % (
            self.version,
            self.dateCreated,
            self.mode,
        )

