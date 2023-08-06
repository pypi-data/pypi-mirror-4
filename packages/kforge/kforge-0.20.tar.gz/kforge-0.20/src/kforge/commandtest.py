import unittest
from kforge.testunit import TestCase
import kforge.command.initialisetest
import kforge.command.projecttest
import kforge.command.membertest
import kforge.command.servicetest
import kforge.command.emailjoinrequesttest
import kforge.command.emailmailmanpasswordtest
#import kforge.command.projectwithadministratortest
from kforge.exceptions import *

def suite():
    "Return a TestSuite of kforge.command TestCases."
    suites = [
        kforge.command.initialisetest.suite(),
        kforge.command.projecttest.suite(),
        kforge.command.membertest.suite(),
        kforge.command.servicetest.suite(),
        kforge.command.emailjoinrequesttest.suite(),
        kforge.command.emailmailmanpasswordtest.suite(),
#        kforge.command.projectwithadministratortest.suite(),
    ]
    return unittest.TestSuite(suites)

