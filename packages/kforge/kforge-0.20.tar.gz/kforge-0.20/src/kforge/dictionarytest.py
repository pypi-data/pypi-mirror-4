import unittest
import os
import kforge.dictionary
from kforge.dictionarywords import PROJECTS_PATH
from kforge.dictionarywords import PLUGINS_AVAILABLE

def suite():
    "Return a TestSuite of kforge.dom TestCases."
    suites = [
        unittest.makeSuite(SystemDictionaryTest),
    ]
    return unittest.TestSuite(suites)


class SystemDictionaryTest(unittest.TestCase):
    "TestCase for the SystemDictionary class."
    
    def setUp(self):
        self.dictionary = kforge.dictionary.SystemDictionary()
    
    def testInit(self):
        self.failUnless(self.dictionary)
    
    def testGetValues(self):
        self.failUnless(self.dictionary.has_key(PROJECTS_PATH))
        self.failUnless(self.dictionary.has_key(PLUGINS_AVAILABLE))

