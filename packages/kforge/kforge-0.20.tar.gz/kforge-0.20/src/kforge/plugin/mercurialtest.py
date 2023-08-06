import unittest
import tempfile
import os

from kforge.testunit import *
import kforge.plugin.mercurial

def suite():
    suites = [
        unittest.makeSuite(PluginTest),
    ]
    return unittest.TestSuite(suites)

class PluginTest(TestCase):
    """
    TestCase for the Subversion plugin.
    """
    
    def setUp(self):
        super(PluginTest, self).setUp()
        if not 'mercurial' in self.registry.plugins:
            self.registry.plugins.create('mercurial')
        mercurial = self.registry.plugins['mercurial']
        project = self.registry.projects['annakarenina']
        if 'hg' in project.services:
            del(project.services['hg'])
        self.service = project.services.create('hg', plugin=mercurial)
    
    def tearDown(self):
        # do all of them to deal with errors elsewhere
        self.service.delete()
    
    def testServicePaths(self):
        self.failUnless(self.service.hasDir(), self.service.getDirPath())
    
