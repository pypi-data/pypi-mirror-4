import os.path
import commands
import unittest

from kforge.ioc import *
from kforge.apache.config import ApacheConfigBuilder
import kforge.utils
from kforge.testunit import TestCase
from kforge.dictionarywords import APACHE_CONFIGTEST_CMD
from kforge.dictionary import SystemDictionary


def suite():
    suites = [
        unittest.makeSuite(TestApacheConfigBuilder),
    ]
    return unittest.TestSuite(suites)


class TestApacheConfigBuilder(TestCase):
    """
    We call setUp and tearDown in __init__ as we do not alter domain during
    run
    """
    
    def setUp(self):
        super(TestApacheConfigBuilder, self).setUp()
        self.configBuilder = ApacheConfigBuilder()
        self.dictionary = SystemDictionary()
   
    def failUnlessFragInFrag(self, expectedFragment, configFragment):
        self.failUnless(expectedFragment in configFragment, "%s not in %s" % (
            expectedFragment, configFragment
        ))
    
    def testGetAdminHostConfig(self):
        self.configBuilder.createWebuiConfig()

    def testGetAccessControl(self):
        self.project = self.registry.projects['warandpeace']
        expFrag = 'AuthType basic'
        configFrag = self.configBuilder.getModWsgiAccessControl()
        self.failUnlessFragInFrag(expFrag, configFrag)
        configFrag = self.configBuilder.getModPythonAccessControl()
        self.failUnlessFragInFrag(expFrag, configFrag)

    def test_getWebuiPathPatterns(self):
        out = self.configBuilder.getWebuiPathPatterns()
        exp = '^/$|'
        self.failUnlessFragInFrag(exp, out)
        exps = [ '|^/people($|/.*)',
                '|^/admin($|/.*)',
                '|^/projects($|/.*)',
                '|^/login($|/.*)',
                '|^/logout($|/.*)',
                '|^/accessDenied($|/.*)',
                ]
        for exp in exps:
            self.failUnlessFragInFrag(exp, out)

