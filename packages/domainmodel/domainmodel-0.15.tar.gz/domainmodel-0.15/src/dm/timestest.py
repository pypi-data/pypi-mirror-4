import dm.times
import unittest
import os

def suite():
    suites = [
        unittest.makeSuite(TestTimeNow),
    ]
    return unittest.TestSuite(suites)


class TestTimeNow(unittest.TestCase):

    def testGetLocalNow(self):
        timeNow = dm.times.getLocalNow()
        self.failUnless(timeNow)
        self.failUnless(timeNow.year)
        
    def testResetTimezone(self):
        os.environ['TZ'] = 'Europe/Paris'
        dm.times.resetTimezone()
        # Todo: Check local time has changed but utc time hasn't.
