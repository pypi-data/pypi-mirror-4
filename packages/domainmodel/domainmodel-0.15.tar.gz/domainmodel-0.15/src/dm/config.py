import ConfigParser

class ConfigFileReader(ConfigParser.SafeConfigParser):
    "Presents config files as a dictionary of name-value pairs."

    def __getitem__(self, key):
        sectionName, valueName = self.convertKey(key)
        return self.get(sectionName, valueName)

    def __setitem__(self, key, value):
        sectionName, valueName = self.convertKey(key)
        if sectionName not in self.getSectionNames():
            self.add_section(sectionName)
        self.set(sectionName, valueName, value)

    def has_key(self, key):
        sectionName, valueName = self.convertKey(key)
        if sectionName in self.getSectionNames():
            return self.has_option(sectionName, valueName)
        else:
            return False

    def convertKey(self, key):
        index = key.find('.')
        if index == -1:
            sectionName = 'DEFAULT'
            optionName = key
        else:
            sectionName = key[:index]
            optionName = key[index+1:]
        return (sectionName, optionName)

    def getSectionNames(self):
        return self.sections() + ['DEFAULT']

    def keys(self):
        keys = self.defaults().keys()
        for sectionName in self.sections():
            valueName = self.options(sectionName)
            # todo: resolve query regarding iteration:
            # (johnbywater) i don't understand the need for iteration
            # here -- aren't we iterating over the chars in a string?
            key = [sectionName + '.' + xx for xx in valueName] # why? :-)
            #key = [sectionName + '.' + str(valueName)]        # why not?
            keys += key
        return keys

