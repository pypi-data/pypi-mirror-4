"""
Inversion of control. Used to inject dependencies between features.

"""

class FeatureBroker(object):

    __slots__ = ["features", "allowReplace"]

    def __init__(self, allowReplace=False):
        self.allowReplace = allowReplace
        self.clear()

    def clear(self):
        self.features = {}
      
    def register(self, featureName, feature, *args, **kwargs):
        if not self.allowReplace:
            if featureName in self.features:
                message = "Duplicate feature: %r" % featureName
                raise Exception(message)
        if callable(feature):
            def call():
                return feature(*args, **kwargs)
        else:
            def call(): 
                return feature
        self.features[featureName] = call
      
    def deregister(self, featureName):
        if featureName in self.features:
            del(self.features[featureName])
        else:
            message = "No feature: %r" % featureName
            raise Exception(message)
     
    def __contains__(self, featureName):
        return featureName in self.features
     
    def __getitem__(self, featureName):
        try:
            feature = self.features[featureName]
        except KeyError:
            raise KeyError, "Unknown feature %r" % featureName
        return feature()

    def __delitem__(self, featureName):
        try:
            feature = self.features[featureName]
        except KeyError:
            raise KeyError, "Unknown feature %r" % featureName
        return feature()


features = FeatureBroker()


class FeatureAssertion(object):

    def __init__(self, feature):
        self.feature = feature

    def execute(self):
        pass
        

class NoAssertion(FeatureAssertion):
    pass


class IsInstanceOf(FeatureAssertion):

    def __init__(self, feature, *classes):
        super(IsInstanceOf, self).__init__(feature)
        self.classes = classes
        
    def execute(self):
        super(IsInstanceOf, self).execute()
        assert isinstance(self.feature, self.classes)


class HasAttributes(FeatureAssertion):

    def __init__(self, feature, *attributes):
        super(HasAttributes, self).__init__(feature)
        self.attributes = attributes
        
    def execute(self):
        super(HasAttributes, self).execute()
        for attribute in self.attributes:
            assert hasattr(self.feature, attribute) 


class HasMethods(FeatureAssertion):

    def __init__(self, feature, *methods):
        super(HasMethods, self).__init__(feature)
        self.methods = methods
        
    def execute(self):
        super(HasMethods, self).execute()
        for method in self.methods:
            assert hasattr(self.feature, method) 
            assert callable(getattr(self.feature, method))


class RequiredFeature(object):

    __slots__ = ["featureName", "assertionClass"]

    def __init__(self, featureName, assertion=NoAssertion):
        self.featureName = featureName
        self.assertionClass = assertion
      
    def __get__(self, obj, type=None):
        return getattr(self, 'feature')

    def __getattr__(self, attrName):
        if attrName == 'feature':
            return self.findFeature()
        else:
            return getattr(self.feature, attrName)
                
    def __setattr__(self, attrName, value):
        if attrName in self.__slots__:
            super(RequiredFeature, self).__setattr__(attrName, value)
        else:
            setattr(self.feature, attrName, value)
                
    def findFeature(self):
        feature = features[self.featureName]
        self.assertionClass(feature).execute()
        return feature
    
    #
    # Built-in handler registrations and delegations.
    
    def __getitem__(self, key):
        return self.feature[key]

    def __contains__(self, key):
        try:
            self.feature[key]
        except:
            return False
        else:
            return True

    # todo: Other __...__ methods 


