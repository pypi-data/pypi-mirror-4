import unittest

# sanity test

def suite():
    suites = [
        unittest.makeSuite(UnitTestTestCase),
    ]
    return unittest.TestSuite(suites)

class UnitTestTestCase(unittest.TestCase):

    def test_failUnless(self):
        self.failUnless(True)

    def test_failIf(self):
        self.failIf(False)

    def test_failUnlessRaises(self):
        self.failUnlessRaises(Exception, self.fail)

