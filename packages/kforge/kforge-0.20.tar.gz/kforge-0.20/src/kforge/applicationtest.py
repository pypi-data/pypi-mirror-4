from kforge.application import Application
from kforge.ioc import *
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestApplication),
    ]
    return unittest.TestSuite(suites)

features.allowReplace = True

class TestApplication(unittest.TestCase):

    def setUp(self):
        import kforge.soleInstance
        self.application = kforge.soleInstance.application

    def tearDown(self):
        self.application = None

    def test_exists(self):
        self.failUnless(self.application)

    def test_commands(self):
        self.failUnless(self.application.commands)

    def test_registry(self):
        self.failUnless(self.application.registry)

    def test_dictionary(self):
        self.failUnless(self.application.dictionary)


