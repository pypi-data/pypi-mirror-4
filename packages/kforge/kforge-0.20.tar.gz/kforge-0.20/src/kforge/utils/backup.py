"""
Function to provide backup functionality for standard applications such as
files, databases, subversion.

This module should not **anything** from the rest of kforge so that it can
remain standalone and be used without anything else from kforge.
"""
import os
from kforge.ioc import *

logger = RequiredFeature('Logger')

class BackupItemBase(object):
    """
    Base class for backup item classes which perform backup activities for a single archive of items of a particular type (e.g. filesystem, dbs, etc).
    """
    
    def __init__(self, backupBaseDirPath, archiveName):
        """
        @param archiveName: name of archive to write to. NB: extension may get
        added to this.
        """
        self._backupBaseDirPath = backupBaseDirPath
        self._archiveName = archiveName
    
    def doBackup(self):
        """
        Performs backup for this backup item.
        In base class performs no function and **must** be overridden in derived classes
        """
        pass
    
    def runCommand(self, command):
        """
        Run a shell command (UNIX or windows)
        
        @return the resulting error code
        """
        # [[TODO: use pipes and get back stderr etc ...]]
        err_code = os.system(command)
        if(err_code != 0):
            logger.error('Shell command failed: ' + command)
        return err_code
    
    def getBackupFilePath(self, extension):
        """
        @param extension: additional extension to add to file name (should be
        without leading '.'
        """
        return os.path.join(self._backupBaseDirPath,
            self._archiveName + '.' + extension)

        
## ********************************************************************
## File System Backup
## ********************************************************************

import tarfile

class BackupItemFile(BackupItemBase):
    
    def __init__(self, backupBaseDirPath, archiveName, files):
        """
        @param files: list of paths to backup (files or directories)
        """
        super(BackupItemFile, self).__init__(backupBaseDirPath, archiveName)
        self._fileList = files
    
    def doBackup(self):
        """
        @see BackupItemBase.doBackup()
        Add files/directories in list supplied on creation to archive
        See __init__ for more information on parameters used
        
        By default recurse into subdirectories.
        Uses integrated gzip by default.
        Auto naming of destination file if destination is a directory with first name of first source.
        Existing destination file will be overwritten.
        """
        backupFilePath = os.path.join(self._backupBaseDirPath, self._archiveName + '.tgz')
        tar = tarfile.open(backupFilePath, 'w:gz')
        # don't do posix compatible archives as this seems to lead to errors with long names
        tar.posix = False
        for ff in self._fileList:
            tar.add(ff)
        tar.close()

## ********************************************************************
## Subversion Backup
## ********************************************************************

class BackupItemSvn(BackupItemBase):
    """
    Backup svn repositories using svnadmin dump
    
    Can set backup method to either 'dump' or 'hotcopy' (default is hotcopy)
    """
    def __init__(self, backupBaseDirPath, archiveName, repoPath):
        super(BackupItemSvn, self).__init__(backupBaseDirPath, archiveName)
        self.repoPath = repoPath
        self.backupMethod = 'hotcopy'
    
    def doBackup(self):
        destPath = os.path.join(self._backupBaseDirPath, self._archiveName)
        self._backup(self.repoPath, destPath)
    
    def _backup(self, repoPath, destPath):
        if self.backupMethod == 'dump':
            self._dumpBackup(repoPath, destPath)
        elif self.backupMethod == 'hotcopy':
            self._hotCopyBackup(repoPath, destPath)
        else: raise Exception('Unknown backup method: %s' % self.backupMethod)
    
    def _dumpBackup(self, repoPath, destPath):
        destPath = destPath + '.gz'
        logger.info('Backing up repository ' + repoPath + ' to ' +  destPath + ' .... ')
        cmd = 'svnadmin dump --quiet ' +  repoPath + ' | gzip >' +  destPath
        self.runCommand(cmd)
    
    def _hotCopyBackup(self, repoPath, destPath):
        logger.info('Backing up repository ' + repoPath + ' to ' +  destPath + ' .... ')
        cmd = 'svnadmin hotcopy ' +  repoPath + ' ' +  destPath + ' --clean-logs'
        self.runCommand(cmd)

class BackupItemSvnFromParentPath(BackupItemSvn):
    def __init__(self, backupBaseDirPath, archiveName, parentPath):
        """
        @param archiveName: subdirectory if backupBaseDirPath into which to
        put the backups (if you don't want to use it set it to ''
        @param parentPath: parentPath to repos (i.e. all repos are subdirectories of parent path)
        
        """
        super(BackupItemSvnFromParentPath, self).__init__(backupBaseDirPath, archiveName, None)
        self.basePath = os.path.join(backupBaseDirPath, archiveName)
        self.parentPath = parentPath
    
    def doBackup(self):
        repos = os.listdir(parentPath)
        for repo in repos:
            repoPath = os.path.join(parentPath, repo)
            destPath = os.path.join(self.basePath, repo)
            self._backup(repoPath, destPath)

## ********************************************************************
## Database
## ********************************************************************

class BackupItemDb(BackupItemBase):
    """
    @attribute dbName: name of database or special value __all__ which
    indicates that all databases should be backed up. Defaults to __all__
    @attribute username: username to use in connecting to database.
    @attribute extraParams: array of extra params to use in running backup
        Should be provided in correct string form i.e. --lock-tables or -d NOT 
        as lock-tables or d
    @attribute password: password for database
    """
    
    def __init__(self, backupBaseDirPath, archiveName):
        """
        @archiveName: name of archive to write to. NB: name should not have
        extension as this will be added
        """ 
        super(BackupItemDb, self).__init__(backupBaseDirPath, archiveName)
        self.dbName = ''
        self.username = ''
        self.password = ''
        self.extraParams = []
        

class BackupItemDbPgsql(BackupItemDb):
    """
    Use ident authentication so:
        1. username may be blank in which case connect as current user
        2. password not relevant
    """
    
    def __init__(self, backupBaseDirPath, archiveName):
        super(BackupItemDbPgsql, self).__init__(backupBaseDirPath, archiveName)
    
    def doBackup(self):
        if self.dbName == '__all__':
            backupCmd = 'pg_dumpall '
        else:
            backupCmd = 'pg_dump '
        backupCmd += ' '.join(self.extraParams)
        if self.dbName != '__all__':
            backupCmd += ' ' + self.dbName
            
        if self.username != '':
            # assume using ident auth and have to work using that
            # backupCmd += ' --user ' + self._userName
            backupCmd = 'sudo -u ' + self.username + ' ' + backupCmd
        backupCmd += ' --inserts'

        backupCmd += ' | gzip > ' + self.getBackupFilePath('gz')
        self.runCommand(backupCmd)


class BackupItemDbMysql(BackupItemDb):
    """
    See BackupItemDb.
    """ 
    
    def doBackup(self):
        backupCmd = 'mysqldump'
        if self.username != '':
            backupCmd += ' --user ' + self.username
        if self.password != '':
            backupCmd += ' --password=' + self.password
        backupCmd += ' ' + ' '.join(self.extraParams)
        if self.dbName == '__all__':
            backupCmd += ' --all-databases'
        else:
            backupCmd += ' ' + self.dbName
        
        backupCmd += ' | gzip > ' + self.getBackupFilePath('gz')
        self.runCommand(backupCmd)
