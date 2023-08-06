import unittest
import kforge.apache.configtest
import kforge.apache.urlpermissiontest

def suite():
    suites = [
        kforge.apache.configtest.suite(),
        kforge.apache.urlpermissiontest.suite(),
    ]
    return unittest.TestSuite(suites)

