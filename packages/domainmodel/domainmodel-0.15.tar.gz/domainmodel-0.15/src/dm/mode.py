from dm.ioc import *
from dm.dictionarywords import SYSTEM_MODE

class SystemMode(object):

    dictionary = RequiredFeature('SystemDictionary')
    MODE_NAME_PRODUCTION = 'production'
    MODE_NAME_DEVELOPMENT = 'development'

    def __init__(self):
        self.name = self.dictionary[SYSTEM_MODE]

    def isProduction(self):
        return self.name == self.MODE_NAME_PRODUCTION

