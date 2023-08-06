from dm.ioc import *

import unittest

def suite():
    suites = [
        unittest.makeSuite(TestFeatureBroker),
    ]
    return unittest.TestSuite(suites)


class FixtureComponent(object):
    pass


class HandFixture(FixtureComponent):

   thumb  = RequiredFeature('Thumb')
   
   def __init__(self):
       self.value = 4

   def open(self):
       self.thumb.straighten()

   def isStraight(self):
       return self.thumb.isStraight


class DigitComponent(FixtureComponent):

    isStraight = False

    def straighten(self):
        self.isStraight = True


class ThumbFixture(DigitComponent):
    pass
    

class FingerFixture(DigitComponent):
    pass
    

class TestFeatureBroker(unittest.TestCase):
        
    def setUp(self):
        features.register('Thumb', ThumbFixture())
        self.hand = HandFixture()

    def tearDown(self):
        self.hand = None
        features.deregister('Thumb')

    def test_exists(self):
        self.failUnless(self.hand)
        self.failIf(self.hand.isStraight())
        self.hand.open()
        self.failUnless(self.hand.thumb.isStraight)
        self.failUnless(self.hand.isStraight())

