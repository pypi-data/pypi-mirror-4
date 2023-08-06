import unittest
from kforge.testunit import TestCase
from kforge.filesystem import FileSystem
import os

def suite():
    suites = [
        unittest.makeSuite(PluginTest),
    ]
    return unittest.TestSuite(suites)

class PluginTest(TestCase):
    
    def setUp(self):
        super(PluginTest, self).setUp()
        if not self.registry.plugins.has_key('www'):
            self.registry.plugins.create('www')
        self.plugin = self.registry.plugins['www']
        self.project = self.registry.projects['annakarenina']
        if 'www' in self.project.services:
            service = self.project.services['www']
            service.delete()
            service.purge()
        self.project.services.create('www', plugin=self.plugin)
        self.service = self.project.services['www']
        self.filesystem = FileSystem()
    
    def tearDown(self):
        self.service.delete()
        self.service.purge()
    
    def testService(self):
        # Check the filesystem has been setup.
        path = self.filesystem.getServicePath(self.service)
        self.failUnless(path)
        self.failUnless(os.path.exists(path))

