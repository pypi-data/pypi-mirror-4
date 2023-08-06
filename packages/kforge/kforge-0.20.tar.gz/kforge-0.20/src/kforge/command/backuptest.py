import unittest
from kforge.testunit import TestCase
import tempfile
import shutil
import os.path

import kforge.command.backup

def suite():
    "Return a TestSuite of kforge.command TestCases."
    suites = [
        unittest.makeSuite(BackupPathBuilderTest),
        unittest.makeSuite(BackupTest),
    ]
    return unittest.TestSuite(suites)

class BackupPathBuilderTest(TestCase):

    def setUp(self):
        super(BackupPathBuilderTest, self).setUp()
        self.baseDir = '/some/where/over/the/rainbow'
        self.backupPathBuilder = kforge.command.backup.BackupPathBuilder(self.baseDir)
    
    def testGetMiscBackupPath(self):
        out = self.backupPathBuilder.miscBackupPath
        self.assertEquals(out, os.path.join(self.baseDir, 'misc'))
    
    def testgetProjectPath(self):
        project = self.registry.projects['example']
        out = self.backupPathBuilder.getProjectPath(project)
        self.assertEquals(out, os.path.join(self.baseDir, 'projects', 'example'))
    
class BackupTest(TestCase):
    disable = True
    tags = [ 'cli' ]
    
    def setUp(self):
        super(BackupTest, self).setUp()
        self.tempDir = tempfile.mkdtemp()
        self.backupPathBuilder = kforge.command.backup.BackupPathBuilder(self.tempDir)
        self.cmd = kforge.command.backup.Backup(self.tempDir)
        self.cmd.execute()
        
        self.project = self.registry.projects['annakarenina']
        self.projectPath = self.backupPathBuilder.getProjectPath(self.project)
        self.svnPluginPath = os.path.join(self.projectPath, 'svn')
    
    def tearDown(self):
        super(BackupTest, self).tearDown()
        shutil.rmtree(self.tempDir)
    
    def testBackupOfDatabase(self):
        self.failUnless(os.path.exists(os.path.join(self.backupPathBuilder.miscBackupPath, 'db.sql.gz')))
    
    def testBackupOfProjects(self):
        self.failUnless(os.path.exists(self.projectPath))
    
    def testBackupOfService(self):
        if 'svn' in self.project.services:
            path = self.svnPluginPath
            self.failUnless(os.path.exists(path), path)

