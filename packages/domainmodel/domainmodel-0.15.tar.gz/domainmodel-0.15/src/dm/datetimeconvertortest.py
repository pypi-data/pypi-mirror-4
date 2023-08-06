import unittest
from dm.testunit import *
from dm.datetimeconvertor import DateTimeConvertor
from dm.datetimeconvertor import RDateTimeConvertor
from dm.datetimeconvertor import RNSDateTimeConvertor
from dm.datetimeconvertor import DateConvertor
from dm.datetimeconvertor import RDateConvertor
import datetime

def suite():
    suites = [
        unittest.makeSuite(TestDateTimeConvertor),
        unittest.makeSuite(TestRDateTimeConvertor),
        unittest.makeSuite(TestRNSDateTimeConvertor),
        unittest.makeSuite(TestDateConvertor),
        unittest.makeSuite(TestRDateConvertor),
    ]
    return unittest.TestSuite(suites)

class TestDateTimeConvertor(TestCase):

    def setUp(self):
        self.convertor = DateTimeConvertor()

    def test_fromHTML(self):
        dateHtml = "2007-07-01 06:07:08"
        dateDom = datetime.datetime(2007, 07, 01, 6, 7, 8)
        date = self.convertor.fromHTML(dateHtml)
        self.failUnlessEqual(date, dateDom)

    def test_toHTML(self):
        dateHtml = "2007-07-01 06:07:08"
        dateDom = datetime.datetime(2007, 07, 01, 6, 7, 8)
        date = self.convertor.toHTML(dateDom)
        self.failUnlessEqual(date, dateHtml)

    def test_toLabel(self):
        dateLabel = "06:07:08, Sun  1 Jul, 2007"
        dateDom = datetime.datetime(2007, 07, 01, 6, 7, 8)
        date = self.convertor.toLabel(dateDom)
        self.failUnlessEqual(date, dateLabel)


class TestRDateTimeConvertor(TestCase):

    def setUp(self):
        self.convertor = RDateTimeConvertor()

    def test_fromHTML(self):
        dateHtml = "06:07:08 01-07-2007"
        dateDom = datetime.datetime(2007, 07, 01, 6, 7, 8)
        date = self.convertor.fromHTML(dateHtml)
        self.failUnlessEqual(date, dateDom)

    def test_toHTML(self):
        dateHtml = "06:07:08 01-07-2007"
        dateDom = datetime.datetime(2007, 07, 01, 6, 7, 8)
        date = self.convertor.toHTML(dateDom)
        self.failUnlessEqual(date, dateHtml)

    def test_toLabel(self):
        dateLabel = "06:07:08, Sun  1 Jul, 2007"
        dateDom = datetime.datetime(2007, 07, 01, 6, 7, 8)
        date = self.convertor.toLabel(dateDom)
        self.failUnlessEqual(date, dateLabel)


class TestRNSDateTimeConvertor(TestCase):

    def setUp(self):
        self.convertor = RNSDateTimeConvertor()

    def test_fromHTML(self):
        dateHtml = "06:07 01-07-2007"
        dateDom = datetime.datetime(2007, 07, 01, 6, 7, 0)
        date = self.convertor.fromHTML(dateHtml)
        self.failUnlessEqual(date, dateDom)

    def test_toHTML(self):
        dateHtml = "06:07 01-07-2007"
        dateDom = datetime.datetime(2007, 07, 01, 6, 7, 0)
        date = self.convertor.toHTML(dateDom)
        self.failUnlessEqual(date, dateHtml)

    def test_toLabel(self):
        dateLabel = "06:07, Sun  1 Jul, 2007"
        dateDom = datetime.datetime(2007, 07, 01, 6, 7, 8)
        date = self.convertor.toLabel(dateDom)
        self.failUnlessEqual(date, dateLabel)


class TestDateConvertor(TestCase):

    def setUp(self):
        self.convertor = DateConvertor()

    def test_fromHTML(self):
        # Should allow dates in 'normal' order.
        dateHtml = "2007-07-01"
        dateDom = datetime.datetime(2007, 07, 01)
        date = self.convertor.fromHTML(dateHtml)
        self.failUnlessEqual(date, dateDom)

    def test_toHTML(self):
        dateHtml = "2007-07-01"
        dateDom = datetime.datetime(2007, 07, 01)
        date = self.convertor.toHTML(dateDom)
        self.failUnlessEqual(date, dateHtml)

    def test_toLabel(self):
        dateLabel = "Sun,  1 Jul, 2007"
        dateDom = datetime.datetime(2007, 07, 01, 6, 7, 8)
        date = self.convertor.toLabel(dateDom)
        self.failUnlessEqual(date, dateLabel)


class TestRDateConvertor(TestCase):

    def setUp(self):
        self.convertor = RDateConvertor()

    def test_fromHTML(self):
        dateHtml = "01-07-2007"
        dateDom = datetime.datetime(2007, 07, 01)
        date = self.convertor.fromHTML(dateHtml)
        self.failUnlessEqual(date, dateDom)
        # Should also allow dates in 'normal' order.
        dateHtml = "2007-07-01"
        dateDom = datetime.datetime(2007, 07, 01)
        date = self.convertor.fromHTML(dateHtml)
        self.failUnlessEqual(date, dateDom)

    def test_toHTML(self):
        dateHtml = "01-07-2007"
        dateDom = datetime.datetime(2007, 07, 01)
        date = self.convertor.toHTML(dateDom)
        self.failUnlessEqual(date, dateHtml)

    def test_toLabel(self):
        dateLabel = "Sun,  1 Jul, 2007"
        dateDom = datetime.datetime(2007, 07, 01, 6, 7, 8)
        date = self.convertor.toLabel(dateDom)
        self.failUnlessEqual(date, dateLabel)

