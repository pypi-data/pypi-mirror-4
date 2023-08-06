import unittest
from dm.dom.testunit import TestCase
import dm.dom.image
from dm.exceptions import *

def suite():
    suites = [
        unittest.makeSuite(TestImage),
    ]
    return unittest.TestSuite(suites)

class TestImage(TestCase):
    "TestCase for the Image class."
    
    def setUp(self):
        super(TestImage, self).setUp()
        self.images = self.registry.images
        self.image = self.images.create()
        self.image.file = 'lalalalala'

    def tearDown(self):
        try:
            self.image.delete()
            self.image.purge()
        except:
            pass

    def test_new(self):
        self.failUnless(self.image, "New image could not be created.")
        self.assertEquals(self.image.state, self.activeState,
            "Not in active state after create."
        )

    def test_create(self):
        self.image = self.images.create()
        
    def test_file(self):
        self.failUnlessEqual(self.image.file, 'lalalalala')

    def test_ImageFile(self):
        metaAttr = self.image.meta.attributeNames['file']
        self.failUnless(metaAttr)

