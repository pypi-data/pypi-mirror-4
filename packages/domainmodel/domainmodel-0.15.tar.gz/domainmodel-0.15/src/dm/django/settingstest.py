import unittest
import dm.django.settings.main as settings

def suite():
    suites = [
        unittest.makeSuite(TestSettings),
        unittest.makeSuite(TestUrls),
    ]
    return unittest.TestSuite(suites)

class TestSettings(unittest.TestCase):

    def test_main(self):
        self.failUnless(settings.TIME_ZONE)
        self.failUnless(settings.SECRET_KEY)
        self.failUnless(settings.TEMPLATE_DIRS)
        self.failUnlessEqual(settings.ROOT_URLCONF, '')

class TestUrls(unittest.TestCase):
    
    pass


