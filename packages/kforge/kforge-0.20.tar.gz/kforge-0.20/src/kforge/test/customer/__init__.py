import unittest

def suite():
    import kforge.test.customer.plugin
    import kforge.test.customer.kui

    suites = [
        kforge.test.customer.plugin.suite(),
        kforge.test.customer.kui.suite(),
    ]
    return unittest.TestSuite(suites)


