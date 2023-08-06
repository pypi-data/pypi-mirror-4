"""
The kforge.plugin unittest suite.
"""

import unittest
import os

from kforge.testunit import *
import kforge.plugin.basetest
import kforge.plugin.accesscontroltest
import kforge.plugin.wwwtest
import kforge.plugin.davtest
import kforge.plugin.svntest
import kforge.plugin.tractest
import kforge.plugin.mointest
import kforge.plugin.wordpresstest
import kforge.plugin.mailmantest
import kforge.plugin.mercurialtest
import kforge.plugin.notifytest

def suite():
    suites = [
        kforge.plugin.basetest.suite(),
        kforge.plugin.accesscontroltest.suite(),
        kforge.plugin.wwwtest.suite(),
        kforge.plugin.davtest.suite(),
        kforge.plugin.svntest.suite(),
        kforge.plugin.tractest.suite(),
        kforge.plugin.mointest.suite(),
        kforge.plugin.wordpresstest.suite(),
        kforge.plugin.mailmantest.suite(),
        kforge.plugin.mercurialtest.suite(),
        kforge.plugin.notifytest.suite(),
    ]
    return unittest.TestSuite(suites)

