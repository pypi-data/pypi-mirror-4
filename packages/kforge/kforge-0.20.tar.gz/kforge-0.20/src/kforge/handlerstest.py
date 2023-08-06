import unittest
import kforge.handlers.apachecodestest
import kforge.handlers.modpythontest
import kforge.handlers.modwsgitest

def suite():
    suites = [
        kforge.handlers.apachecodestest.suite(),
        kforge.handlers.modpythontest.suite(),
        kforge.handlers.modwsgitest.suite(),
    ]
    return unittest.TestSuite(suites)

