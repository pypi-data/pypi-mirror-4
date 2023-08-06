import unittest
import tempfile
import shutil
import os

from kforge.testunit import *
import kforge.filesystem
import kforge.plugin.mercurial

# TODO: test mercurial installed.

class PluginTest(TestCase):
    
    def setUp(self):
        super(PluginTest, self).setUp()
        if not self.registry.plugins.has_key('mercurial'):
            self.registry.plugins.create('mercurial')
        self.plugin = self.registry.plugins['mercurial']
        self.project = self.registry.projects['annakarenina']
        # double check ...
        if 'mercurial' in self.project.services:
            service = self.project.services['mercurial']
            service.delete()
            service.purge()
        self.project.services.create('mercurial', plugin=self.plugin)
        self.service = self.project.services['mercurial']
        self.filesystem = kforge.filesystem.FileSystem()
    
    def tearDown(self):
        # do all of them to deal with errors elsewhere
        self.service.delete()
        self.service.purge()
    
    def testServicePaths(self):
        self.failUnless(self.service.hasDir(), self.service.getDirPath())
    
    def testGetApacheConfig(self):
        self.plugin.getSystem().getApacheConfig(self.service)


from StringIO import StringIO
class MercurialUtilsTest(unittest.TestCase):
    
    def setUp(self):
        # todo: remove this parentPath 'feature'
        self.parentPath = tempfile.mkdtemp(prefix='kforge-mercurialutils-test-')
        self.utils = kforge.plugin.mercurial.MercurialUtils()
        self.name = 'annakarenina'
        self.repopath = os.path.join(self.parentPath, self.name)
    
    def tearDown(self):
        shutil.rmtree(self.parentPath)
    
    def test_create_and_delete(self):
        self.utils.create(self.repopath)
        assert os.path.exists(self.repopath)
        self.utils.delete(self.repopath)
        assert not os.path.exists(self.repopath)

    def test_make_cgi(self):
        cgi_fo = StringIO(kforge.plugin.mercurial.Plugin.hgweb_cgi)
        out = self.utils.make_cgi(cgi_fo, 'blah1', 'blah2')
        exp = 'return hgweb("%s", "%s")' % ('blah1', 'blah2')
        assert exp in out, (exp, out)

    def test_create_with_web(self):
        cgi = StringIO(kforge.plugin.mercurial.Plugin.hgweb_cgi)
        self.utils.create_with_web(self.repopath, cgi, self.name)
        repo_path = os.path.join(self.repopath, 'repo')
        hgrc_path = os.path.join(repo_path, '.hg', 'hgrc')
        index_path = os.path.join(self.repopath, 'hgweb.cgi')
        assert os.path.exists(repo_path)
        assert os.path.exists(index_path), index_path
        assert os.path.exists(hgrc_path), hgrc_path
        backup = os.path.join(self.parentPath, 'mybackup')
        self.utils.backup(self.repopath, backup)
        assert os.path.exists(backup + '.tgz')

