# To adjust the system time and timezone:
#  - use `ntpdate' to set host time (/etc/init.d/ntpdate restart).
#  - use `tzconfig' to set host timezone (/usr/sbin/tzconfig).

import time
import datetime

def resetTimezone():
    time.tzset()

def getUniversalNow():
    return datetime.datetime.utcnow()

def getLocalNow():
    return datetime.datetime.now()

def getDelta(days, seconds=0, microseconds=0):
    return datetime.timedelta(days, seconds, microseconds)

