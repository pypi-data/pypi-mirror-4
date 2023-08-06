"""
This modules tests tests the kforge-admin cli

WARNING: as it does things like rebuild the database it is *very* slow
"""
import unittest
import os
import tempfile
import shutil
import commands

class KforgeAdminTest(unittest.TestCase):
    disable = True
    
    def setUp(self):
        self.tempDir = tempfile.mkdtemp()
        self.cmdStub = 'bin/kforge-admin '
        # cmd = self.cmdStub + 'data create'
        # self._testCommand(cmd)
    
    def tearDown(self):
        shutil.rmtree(self.tempDir)
    
    def _testCommand(self, cmd):
        status, output = commands.getstatusoutput(cmd)
        if status:
            self.fail('Error on cmd [%s]: %s' % (cmd, output))
        return output
    
    def test_help(self):
        cmd = self.cmdStub + 'help'
        output = self._testCommand(cmd)
        self.failUnless(len(output) > 0)

    def test_about(self):
        cmd = self.cmdStub + 'about'
        output = self._testCommand(cmd)
        self.failUnless(len(output) > 0)
    
    def test_help_data(self):
        cmd = self.cmdStub + 'help data'
        output = self._testCommand(cmd)
        self.failUnless(len(output) > 0)

    def test_backup(self):
        # running this requires provision of superuser password
        backupPath = os.path.join(self.tempDir, 'backup')
        cmd = self.cmdStub + 'backup ' + backupPath
        output = self._testCommand(cmd)
    
    def test_help_db(self):
        cmd = self.cmdStub + 'help db'
        output = self._testCommand(cmd)
        self.failUnless(len(output) > 0)
 
    def test_db(self):
        cmd1 = self.cmdStub + 'db delete'
        self._testCommand(cmd1)
        cmd2 = self.cmdStub + 'db create'
        self._testCommand(cmd2)
        cmd4 = self.cmdStub + 'db init'
        self._testCommand(cmd4)
        cmd3 = self.cmdStub + 'db rebuild'
        self._testCommand(cmd3)
    
    def test_www_buildconfig(self):
        cmd1 = self.cmdStub + 'www build'
        self._testCommand(cmd1)

    def test_www_reload(self):
        cmd2 = self.cmdStub + 'www reload'
        self._testCommand(cmd2)

    def test_shell_help(self):
        cmd = self.cmdStub + 'help shell'
        output = self._testCommand(cmd)
        self.failUnless('shell' in output)

if __name__ == '__main__':
    unittest.main()
