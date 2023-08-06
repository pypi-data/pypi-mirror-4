import unittest
import tempfile
from kforge.testunit import TestCase

def suite():
    "Return a TestSuite of kforge.command TestCases."
    suites = [
            unittest.makeSuite(TestUtils),
        ]
    return unittest.TestSuite(suites)

class TestUtils(TestCase):

    def test_import(self):
        if self.dictionary['captcha.enable']:
            # check module imports
            import kforge.utils.captcha  

