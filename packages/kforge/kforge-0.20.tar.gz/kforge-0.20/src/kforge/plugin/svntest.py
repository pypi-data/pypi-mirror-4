import unittest
import tempfile
import os

from kforge.testunit import *
import kforge.plugin.svn

def suite():
    suites = [
            unittest.makeSuite(PluginTest),
            unittest.makeSuite(SvnUtilsTest)
        ]
    return unittest.TestSuite(suites)

class PluginTest(TestCase):
    """
    TestCase for the Subversion plugin.
    """
    
    def setUp(self):
        super(PluginTest, self).setUp()
        if not self.registry.plugins.has_key('svn'):
            self.registry.plugins.create('svn')
        self.plugin = self.registry.plugins['svn']
        self.project = self.registry.projects['annakarenina']
        if 'svn' in self.project.services:
            service = self.project.services['svn']
            service.delete()
            service.purge()
        self.project.services.create('svn', plugin=self.plugin)
        self.service = self.project.services['svn']
    
    def tearDown(self):
        # do all of them to deal with errors elsewhere
        self.service.delete()
        self.service.purge()
    
    def testServicePaths(self):
        self.failUnless(self.service.hasDir(), self.service.getDirPath())
    

class SvnUtilsTest(unittest.TestCase):
    
    def setUp(self):
        # todo: remove this parentPath 'feature'
        self.parentPath = tempfile.mkdtemp(prefix='kforge-svnutils-test-')
        self.utils = kforge.plugin.svn.SvnUtils(self.parentPath)
        self.name = 'annakarenina'
        self.expectedRepoPath = os.path.join(self.parentPath, self.name)
    
    def tearDown(self):
        os.system('rm -rf %s' % self.parentPath)
    
    def testGetRepositoryPath(self):
        outPath = self.utils.getRepositoryPath(self.name)
        self.assertEquals(outPath, self.expectedRepoPath )
    
    def testCreateAndDeleteRepository(self):
        self.utils.createRepository(self.name)
        self.failUnless(os.path.exists(self.expectedRepoPath))
        self.utils.deleteRepository(self.name)
        self.failIf(os.path.exists(self.expectedRepoPath))

