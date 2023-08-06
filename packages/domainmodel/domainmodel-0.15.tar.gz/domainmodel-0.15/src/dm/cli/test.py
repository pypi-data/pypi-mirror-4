import os
import sys
import re
import unittest
from optparse import OptionParser

os.environ['DJANGO_SETTINGS_MODULE'] = 'dm.django.settings.main'

class UtilityRunner(object):

    def __init__(self):
        usage  = 'usage: %prog [options] [module_name]'
        usage += '\n\tmodule_name specifies the module to test. '
        usage += 'If none supplied then run all tests.'
        parser = OptionParser(usage)
        parser.add_option('-v', '--verbose',
        action='store_true', dest='verbose', default=False,
        help='Be verbose in printing status messages')
        parser.add_option('-l', '--level',
        action='store', type='int', dest='level', default=1,
        help='Verbosity level of test runner')
        # todo: fix this, which breaks optparse v1.4.1:
        # optparse.OptionError: option -c/--config: invalid option type: 'str'
        parser.add_option('-c', '--config',
        action='store', dest='config', default='',
        #    action='store', type='str', dest='config', default='',
        help='Path to configuration file. If not provided please ensure relevant environment variable is set.'
        )
        parser.add_option('-p', '--profile',
        action='store_true', dest='profile', default=False,
        help='Profile the performance of a test suite')

        (options, args) = parser.parse_args()
        if options.config:
            os.environ['DOMAINMODEL_SETTINGS'] = options.config
        
        import dm.testunit
        dm.testunit.DevApplication()

        (options, args) = parser.parse_args()
        # by default always 1 argument (name of file itself)
        suiteToRun = None
        moduleName = ''
        moduleName = 'dm.test'
        if len(args) == 1:
            moduleName = args[0]
        elif len(args) >= 1:
            parser.print_help()
            sys.exit(1)

        testModuleName = moduleName
        testModule = __import__(testModuleName,'','','*')
        testSuite = testModule.suite()
        
        testRunner = unittest.TextTestRunner(verbosity=options.level)
        if options.profile:
            code = "result = testRunner.run(testSuite)"
            import profile
            profile.run(code)
        else:
            result = testRunner.run(testSuite)

        if not result.wasSuccessful():
            sys.exit(1)

