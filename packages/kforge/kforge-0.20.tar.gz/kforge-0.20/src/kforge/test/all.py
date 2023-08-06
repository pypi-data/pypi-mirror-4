import unittest
import kforge.test.developer
import kforge.test.customer

def suite():
    suites = [
        kforge.test.customer.suite(),
        kforge.test.developer.suite(),
    ]
    return unittest.TestSuite(suites)

