import unittest
import os
import shutil
import tempfile

import kforge.plugin.wordpress
from kforge.ioc import *
from kforge.testunit import TestCase

def suite():
    suites = [
        unittest.makeSuite(TestWordpressUtil),
        unittest.makeSuite(PluginTest),
    ]
    return unittest.TestSuite(suites)

class PluginTest(TestCase):
    
    def setUp(self):
        super(PluginTest, self).setUp()
        if not self.registry.plugins.has_key('wordpress'):
            self.registry.plugins.create('wordpress')
        self.plugin = self.registry.plugins['wordpress']
        self.pluginSystem = self.plugin.getSystem()
        self.project = self.registry.projects['annakarenina']
        try:
            self.service = self.plugin.services.create(name='wordpress', project=self.project)
        except:
            for service in self.plugin.services.findDomainObjects(name='wordpress', project=self.project):
                service.delete()
                service.purge()
            raise
    
    def tearDown(self):
        super(PluginTest, self).tearDown()
        self.service.delete()
        self.service.purge()
        
    def testServicesPaths(self):
        self.failUnless(self.service.hasDir(), self.service.getDirPath())
    
    def test_backup(self):
        tmpdir = tempfile.mkdtemp(prefix='kforge-wordpress-')
        class backupPathBuilder:
            def getServicePath(self, service):
                dest = os.path.join(tmpdir, 'wpbackup.sql.gz')
                return dest
        self.pluginSystem.backup(self.service, backupPathBuilder())


class TestWordpressUtil(unittest.TestCase):

    dictionary = RequiredFeature('SystemDictionary')
    wordpress_install = dictionary['wordpress.master_path']
    
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='kforge-wordpress-')
        self.destpath = os.path.join(self.tmpdir, 'wp')
        self.utils = kforge.plugin.wordpress.WordpressUtil(
                self.wordpress_install)
        self.prefix = 'anyoldname'
        self.utils.create(self.destpath, self.prefix)
    
    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_exists(self):
        config_file_path = os.path.join(self.destpath, 'wp-config.php')
        index_file = os.path.join(self.destpath, 'index.php')
        self.failUnless(os.path.exists(index_file))
        self.failUnless(os.path.exists(config_file_path))

    def test_config(self):
        config_file_path = os.path.join(self.destpath, 'wp-config.php')
        config = file(config_file_path).read()
        self.failUnless("$table_prefix = '%s'" % self.prefix in config)

