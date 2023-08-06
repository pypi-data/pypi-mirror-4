import dm.timestest
import dm.timepointtest
import dm.strategytest
import dm.environmenttest
import dm.apachetest
import dm.logtest
import dm.debugtest
import dm.dbtest
import dm.domtest
import dm.plugintest
import dm.ioctest
import dm.configtest
import dm.configwritertest
import dm.dictionarytest
import dm.commandtest
import dm.filesystemtest
import dm.accesscontroltest
import dm.applicationtest
import dm.migratetest
import dm.viewtest
import dm.djangotest
import dm.pylonstest
import dm.datetimeconvertortest
import dm.utiltest
from dm.testunit import ApplicationTestSuite

def suite():
    suites = [
        dm.timestest.suite(),
        dm.timepointtest.suite(),
        dm.strategytest.suite(),
        dm.environmenttest.suite(),
        dm.apachetest.suite(),
        dm.logtest.suite(),
        dm.debugtest.suite(),
        dm.dbtest.suite(),
        dm.domtest.suite(),
        dm.plugintest.suite(),
        dm.ioctest.suite(),
        dm.configtest.suite(),
        dm.configwritertest.suite(),
        dm.dictionarytest.suite(),
        dm.commandtest.suite(),
        dm.accesscontroltest.suite(),
        dm.viewtest.suite(),
        dm.migratetest.suite(),
        dm.djangotest.suite(),
        dm.pylonstest.suite(),
        dm.utiltest.suite(),
        #dm.filesystemtest.suite(),
        #dm.applicationtest.suite(),
    ]
    return ApplicationTestSuite(suites)

