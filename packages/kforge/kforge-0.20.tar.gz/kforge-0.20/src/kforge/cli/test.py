import os
import sys
import re
from optparse import OptionParser

class UtilityRunner(object):

    def __init__(self):
	os.environ['DJANGO_SETTINGS_MODULE'] = 'kforge.django.settings.main'
#	os.umask(2)

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
        parser.add_option('-c', '--config',
            action='store', dest='config', default='',
            help='Path to configuration file. If not provided please ensure ' + \
              'relevant environment variable is set.'
            )
        parser.add_option('-p', '--profile',
            action='store_true', dest='profile', default=False,
            help='Profile the performance of a test suite')
        
        (options, args) = parser.parse_args()
        if options.config:
            os.environ['KFORGE_SETTINGS'] = options.config

        # Import after making sure KFORGE_SETTINGS has been set.
        import kforge.testrunner
        testSuiteName = 'kforge.test'
        if len(args) == 1:
            testSuiteName = args[0]
        elif len(args) >= 1:
            parser.print_help()
            sys.exit(1)
        if options.profile:
            import profile
            code = "result = kforge.testrunner.run(testSuiteName, options.level)"
            profile.run(code)
        else:
            result = kforge.testrunner.run(testSuiteName, options.level)
        if not result.wasSuccessful():
            sys.exit(1)


