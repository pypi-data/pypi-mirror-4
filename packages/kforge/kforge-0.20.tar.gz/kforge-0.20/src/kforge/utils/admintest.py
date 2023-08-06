import unittest
import tempfile
import shutil

from kforge.utils.admin import *

def suite():
    suites = [
#        unittest.makeSuite(TestFilesystemCommand),
#        unittest.makeSuite(TestInitialiseFilesystem),
        unittest.makeSuite(TestEditConfiguration),
    ]
    return unittest.TestSuite(suites)


class TestFilesystemCommand(unittest.TestCase):

    commandClass = FilesystemCommand
    
    def setUp(self):
        self.tmpDir = tempfile.mkdtemp()
        self.cmd = self.createCommand()

    def tearDown(self):
        shutil.rmtree(self.tmpDir)
    
    def createCommand(self):
        return self.commandClass(self.tmpDir)

    def test_checkFilesystem(self):
        self.failUnless(self.cmd.noEnvironmentExists())


class TestInitialiseFilesystem(TestFilesystemCommand):
    
    commandClass = InitialiseFilesystem
    
    def setUp(self):
        super(TestInitialiseFilesystem, self).setUp()
        self.cmd.execute()
    
    def test_checkFilesystem(self):
        self.failIf(self.cmd.noEnvironmentExists())

    def test_createDirs(self):
        etcPath = os.path.join(self.tmpDir, 'etc')
        self.failUnless(os.path.exists(etcPath))
    
    def test_generateConfiguration(self):
        confPath = os.path.join(self.tmpDir, 'etc/kforge.conf')
        self.failUnless(os.path.exists(confPath))

    def test_cannotOverwriteEnvironment(self):
        self.failUnlessRaises(Exception, self.cmd.execute)


class TestEditConfiguration(unittest.TestCase):
    
    def setUp(self):
        self.inStr = \
"""
[DEFAULT]
# Name of service using the KForge system.
service_name = KForge

# Domain for the KForge service.
# Should *not* include 'www.' 
domain_name = kforge.your.domain.com

# Whether in production or development mode
# values: production (default) | development
#system_mode = production

[db]
# Name of database
name = kforgetest
"""
        substitutions = { 'service_name' : 'noname', 
                          'domain_name' : 'blah.com',
                          'system_mode' : 'development',
                          'name' : 'kforgenontest',
                          }
        self.expected = \
"""
[DEFAULT]
# Name of service using the KForge system.
service_name = noname

# Domain for the KForge service.
# Should *not* include 'www.' 
domain_name = blah.com

# Whether in production or development mode
# values: production (default) | development
system_mode = development

[db]
# Name of database
name = kforgenontest
"""
        from StringIO import StringIO
        self.templateFile = StringIO(self.inStr)
        self.cmd = EditConfiguration(self.templateFile, substitutions)
        self.templateFile.close()
        self.cmd.execute()
    
    def test_1(self):
        expLines = self.expected.splitlines()
        outLines = self.cmd.result.splitlines()
        for ii in range(max(len(expLines), len(outLines))):
            self.failUnlessEqual(expLines[ii], outLines[ii])
