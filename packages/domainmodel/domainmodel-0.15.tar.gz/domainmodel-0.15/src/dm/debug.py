from dm.ioc import *

class Debug(object):

    dictionary = RequiredFeature('SystemDictionary')

    def isDebug(self):
        if self.dictionary['logging.level'] == 'DEBUG':
            return True
        else:
            return False

