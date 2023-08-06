import unittest
from kforge.testunit import TestCase
import os
import shutil
import kforge.plugin.moin
from kforge.ioc import *

def suite():
    suites = [
        #unittest.makeSuite(MoinUtilsTest),
        unittest.makeSuite(PluginTest),
    ]
    return unittest.TestSuite(suites)

class PluginTest(TestCase):
    
    def setUp(self):
        super(PluginTest, self).setUp()
        if 'moin' not in self.registry.plugins:
            self.registry.plugins.create('moin')
        self.plugin = self.registry.plugins['moin']
        self.project = self.registry.projects['annakarenina']
        try:
            self.service = self.plugin.services.create(name='moin', project=self.project)
        except:
            for service in self.plugin.services.findDomainObjects(name='moin', project=self.project):
                service.delete()
                service.purge()
            raise
    
    def tearDown(self):
        super(PluginTest, self).tearDown()
        self.service.delete()
        self.service.purge()
        
    def testServicesPaths(self):
        self.failUnless(self.service.hasDir(), self.service.getDirPath())
    
    #def testBackup(self):
    #    # TODO
    #    pass

class MoinUtilsTest(unittest.TestCase):
    
    dictionary = RequiredFeature('SystemDictionary')
    
    def setUp(self):
        import tempfile
        self.tempdir = tempfile.mkdtemp()  
        self.moinUtils = kforge.plugin.moin.MoinUtils(self.tempdir)  
        self.moinUtils = kforge.plugin.moin.MoinUtils(
            self.dictionary['moin.system_path'], self.tempdir
        )
        self.wikiName = 'test-create-new-wiki'  
        self.moinUtils.createWiki(self.wikiName)
    
    def tearDown(self):
        shutil.rmtree(self.tempdir)
    
    def testCreateWiki(self):
        self.failUnless(self.moinUtils.wikiExists(self.wikiName))
    
    def testDeleteWiki(self):
        self.moinUtils.deleteWiki(self.wikiName)
        self.failIf(self.moinUtils.wikiExists(self.wikiName))
    
    def testBackupWiki(self):
        destPath = os.path.join(self.tempdir, 'backup')
        outPath = destPath + '.tgz'
        self.moinUtils.backupWiki(self.wikiName, destPath)
        self.failUnless(os.path.exists(outPath))
