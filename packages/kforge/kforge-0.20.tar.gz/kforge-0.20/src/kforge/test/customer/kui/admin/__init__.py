from kforge.test.customer.kui.base import KuiTestCase
import kforge.test.customer.kui.admin.domainObject
import kforge.test.customer.kui.admin.hasMany
import unittest

def suite():
    suites = [
        kforge.test.customer.kui.admin.domainObject.suite(),
        kforge.test.customer.kui.admin.hasMany.suite(),
    ]
    return unittest.TestSuite(suites)

