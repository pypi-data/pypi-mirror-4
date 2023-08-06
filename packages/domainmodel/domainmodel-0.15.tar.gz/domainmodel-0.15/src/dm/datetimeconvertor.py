import datetime
import time
import re as sre
import dm.times

class DateTimeConvertor(object):  
    "Converts between HTML (string) and Python."
        
    acceptableFormats = [
        "%H:%M:%S %d-%m-%Y",
        "%H:%M:%S %d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%H:%M %d-%m-%Y",
        "%H:%M %d/%m/%Y",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m",
        "%Y/%m",
        "%m-%Y",
        "%m/%Y",
        "%Y",
    ]
    normalFormat = "%Y-%m-%d %H:%M:%S"
    labelFormat = "%a %e %b %Y, %H:%M:%S"
    
    def fromHTML(self, dateHtml):
        if dateHtml in ['', None]:
            return None
        if isinstance(dateHtml, basestring):
            if 'now' == dateHtml.strip():
                return dm.times.getLocalNow()
            dateTime = self.generouslyParse(dateHtml)
            if dateTime == None:
                msg = "Couldn't accept '%s' for a DateTime." % dateHtml
                raise Exception, msg
            else:
                return dateTime
        if isinstance(dateHtml, datetime.date):
            day = int(dateHtml.day)
            month = int(dateHtml.month)
            year = int(dateHtml.year)
            if isinstance(dateHtml, datetime.datetime):
                hour = int(dateHtml.hour)
                minute = int(dateHtml.minute)
                second = int(dateHtml.second)
            else:
                hour = 0
                minute = 0
                second = 0
        else:
            msg = "Unsupported date input type: %s" % type(dateHtml)
            raise Exception(msg)
        return datetime.datetime(year, month, day, hour, minute, second)

    def toHTML(self, dateTimeObject):
        if dateTimeObject in ['', None]:
            return ''
        return dateTimeObject.strftime(self.normalFormat)

    def toLabel(self, dateTimeObject):
        if dateTimeObject in ['', None]:
            return ''
        return dateTimeObject.strftime(self.labelFormat)

    def generouslyParse(self, string):
        dateTime = None
        for format in self.acceptableFormats:
            try:
                dateTime = datetime.datetime(*(time.strptime(string, format)[0:6]))
            except:
                pass
        return dateTime


class RDateTimeConvertor(DateTimeConvertor):  
    normalFormat = "%H:%M:%S %d-%m-%Y"

class RNSDateTimeConvertor(DateTimeConvertor):  
    normalFormat = "%H:%M %d-%m-%Y"
    labelFormat = "%H:%M, %a %e %b, %Y"

class DateConvertor(DateTimeConvertor):  
    normalFormat = "%Y-%m-%d"
    labelFormat = "%a, %e %b, %Y"

class RDateConvertor(DateConvertor):  
    normalFormat = "%d-%m-%Y"
    labelFormat = "%a, %e %b, %Y"

class DateOfBirthConvertor(RDateConvertor):  
    normalFormat = "%d-%m-%Y"
    labelFormat = "%d/%m/%Y"

