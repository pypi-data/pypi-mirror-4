class DomainClassRegister(dict):
    pass

class __DomainClassRegister(object):
    
    class __singletonDomainClassRegister(dict):
        pass

    __instance = __singletonDomainClassRegister()

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)

    def __getitem__(self, key):
        return self.__instance.__getitem__(key)

    def __setitem__(self, key, value):
        return self.__instance.__setitem__(key, value)

    def __contains__(self, key):
        return self.__instance.__contains__(key)

    def __len__(self):
        return self.__instance.__len__()

    def __iter__(self):
        return self.__instance.__iter__()

