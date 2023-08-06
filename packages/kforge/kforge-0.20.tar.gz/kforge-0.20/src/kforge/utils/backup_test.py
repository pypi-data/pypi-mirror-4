# NOT to be run as part of the overall kforge test suite
import os
import stat
import os.path
import shutil

import unittest
import tempfile

from backup import *

# db tests need a db to be set up in order to work so disabled by default
# see comments on methods below for more details
doDbTests = False

class BackupItemBaseTest(unittest.TestCase):
    tags = [ 'cli' ]
    disable = True
    
    def setUp(self):
        self.tmpDirPath = tempfile.mkdtemp()
        self.archiveName = 'test_archive'
        self.instance = BackupItemBase(self.tmpDirPath, self.archiveName)
    
    def tearDown(self):
        shutil.rmtree(self.tmpDirPath)
    
    def testGetBackupFilePath(self):
        ext = 'txt'
        out = self.instance.getBackupFilePath(ext)
        self.assertEquals(out, os.path.join(self.tmpDirPath,
                                            self.archiveName + '.' + ext))

class BackupItemFileTest(unittest.TestCase):
    tags = [ 'cli' ]
    disable = True
    
    def setUp(self):
        self.tmpDirPath = tempfile.mkdtemp()
        self.tmpInFilePath = os.path.join(self.tmpDirPath, 'to_backup_1.txt')
        ff = file(self.tmpInFilePath, 'w')
        ff.write('Hello World')
        ff.close()
    
    def tearDown(self):
        shutil.rmtree(self.tmpDirPath)
    
    def testAddFilesToTarArchive(self):
        # checks we can backup something trivial without problems:
        backupDirPath = self.tmpDirPath
        fileName = 'backup_item_file_test'
        files = [self.tmpInFilePath]
        outFilePath = os.path.join(backupDirPath, fileName + '.tgz')
        bb = BackupItemFile(backupDirPath, fileName, files)
        bb.doBackup()
        
        # check the file exists (will get exception if it doesn't)
        ff = open(outFilePath, 'r')
        ff.close()

class BackupItemSvnTest(unittest.TestCase):
    tags = [ 'cli' ]
    disable = True
    
    def setUp(self):
        self.tmpDirPath = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.tmpDirPath)
    
    def testDoBackup(self):
        repoName = 'svn_test_repo'
        backupBaseDirPath = self.tmpDirPath
        repoPath = os.path.join(backupBaseDirPath, repoName)
        
        archiveName = 'svn_backup_dir'
        destArchivePath = os.path.join(backupBaseDirPath, archiveName)
        
        # create the repo
        os.system('svnadmin create ' + repoPath)
        
        bb = BackupItemSvn(backupBaseDirPath, archiveName, repoPath)
        bb.doBackup()
        
        # unfortunately svn makes some files read only which messes this up on windows so need to make writable
        self._chmodTree(repoPath, 0666, 0666)
        shutil.rmtree(repoPath)
        self._chmodTree(destArchivePath, 0666, 0666)
        shutil.rmtree(destArchivePath)
    
    def _chmodTree(self, path, mode, mask):
        def visit(arg, dirname, names):
            mode, mask = arg
            for name in names:
                fullname = os.path.join(dirname, name)
                if not os.path.islink(fullname):
                    new_mode = (os.stat(fullname)[stat.ST_MODE] & ~mask) | mode
                    os.chmod(fullname, new_mode)
        os.path.walk(path, visit, (mode, mask))

class BackupItemDbTest(unittest.TestCase):
    """
    These tests require a machine to be set up with test databases named
    test for both mysql and pgsql and to have the correct owners etc
    [[TODO: setup init function where this can all be configured]]
    """
    tags = [ 'cli' ]
    disable = True
    
    def setUp(self):
        self.tmpDirPath = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.tmpDirPath)
    
    # WARNING: for this test to work you will need to execute as root
    def testBackupDbPostgres(self):
        if doDbTests:
            dbName = 'test'
            username = 'postgres'
            archiveName = dbName + '.sql'
            
            bb = BackupItemDbPgsql(self.tmpDirPath, archiveName)
            bb.dbName = dbName
            bb.username = username
            
            bb.doBackup()
        else:
            pass
    
    def testBackupDbMysql(self):
        if doDbTests:
            dbName = 'test'
            archiveName  = 'mysql_' + dbName  
            bb = BackupItemDbMysql(self.tmpDirPath, archiveName)
            bb.dbName = 'test'
            bb.username = 'root'
            bb.password = 'password'
            bb.extraParams = ['--lock-tables=false',
                              '--skip-add-locks',
                              '--skip-extended-insert'
                             ]
            bb.doBackup()
        else:
            pass

if __name__ == '__main__':
    unittest.main()

