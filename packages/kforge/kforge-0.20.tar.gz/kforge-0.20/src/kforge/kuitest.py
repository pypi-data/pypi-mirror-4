import unittest

import kforge.test.customer.kui

def suite():
    suites = [
        kforge.test.customer.kui.suite(),
    ]
    return unittest.TestSuite(suites)

