import unittest
from kforge.testunit import TestCase
import kforge.plugin.trac.dom
from kforge.exceptions import *
#import kforge.command

def suite():
    suites = [
        unittest.makeSuite(TestTracProject)
    ]
    return unittest.TestSuite(suites)

class TestTracProject(TestCase):
    """
    TestCase for the TracProject DomainObject.
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_register(self):
        domainClass = self.registry.getDomainClass('TracProject')
        self.failUnless(domainClass)
        register = domainClass.createRegister()
        self.failIf(register == None, "No register: " + str(register))

    def test_Register(self):
        domainClass = self.registry.getDomainClass('TracProject')

