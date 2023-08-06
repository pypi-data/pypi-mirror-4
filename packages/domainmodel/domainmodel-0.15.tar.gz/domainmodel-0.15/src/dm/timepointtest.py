import unittest
import os
from dm.timepoint import Timepoint
import dm.times

def suite():
    suites = [
        unittest.makeSuite(TestTimepoint),
    ]
    return unittest.TestSuite(suites)


class TestTimepoint(unittest.TestCase):

    def setUp(self):
        self.timepoint = Timepoint()
        self.yesterday = dm.times.getLocalNow() - dm.times.getDelta(days=1)
        self.lastweek = dm.times.getLocalNow() - dm.times.getDelta(days=7)

    def tearDown(self):
        self.timepoint.reset()
        self.timepoint = None

    def test_recorded(self):
        self.timepoint.recorded = self.yesterday
        self.failUnlessEqual(self.timepoint.recorded, self.yesterday)

    def test_actual(self):
        self.timepoint.actual = self.lastweek
        self.failUnlessEqual(self.timepoint.actual, self.lastweek)

    def test_reset(self):
        self.failUnless(self.timepoint.actual > self.lastweek)
        self.failUnless(self.timepoint.recorded > self.yesterday)
        self.timepoint.actual = self.lastweek
        self.timepoint.recorded = self.yesterday
        self.failUnlessEqual(self.timepoint.actual, self.lastweek)
        self.failUnlessEqual(self.timepoint.recorded, self.yesterday)
        self.timepoint.reset()
        self.failUnless(self.timepoint.actual > self.lastweek)
        self.failUnless(self.timepoint.recorded > self.yesterday)
        now1 = self.timepoint.recorded
        import time
        time.sleep(1)
        now2 = self.timepoint.recorded
        self.failUnless(now2 > now1)

