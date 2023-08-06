import unittest
import dm.testunit
        
class TestCase(dm.testunit.TestCase):
    
    def setUp(self):
        super(TestCase, self).setUp()
        self.activeState = self.registry.states['active']
        self.deletedState = self.registry.states['deleted']

