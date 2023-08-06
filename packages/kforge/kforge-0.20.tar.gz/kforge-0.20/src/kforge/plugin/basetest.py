from kforge.testunit import *
import kforge.plugin.base
import unittest
import os


def suite():
    suites = [
        unittest.makeSuite(ServicePluginBaseTest),
    ]
    return unittest.TestSuite(suites)


class ServicePluginBaseTest(TestCase):

    def setUp(self):
        super(ServicePluginBaseTest, self).setUp()
        self.fixtureName = 'TestServicePluginBase'
        self.pluginName = 'example'
        self.plugin = self.registry.plugins[self.pluginName]
        self.pluginSystem = self.plugin.getSystem()
        if self.fixtureName in self.registry.projects:
            project = self.registry.projects[self.fixtureName]
            project.delete()
            project.purge()
        self.project = self.registry.projects.create(self.fixtureName)
        if self.plugin.name in self.project.services:
            service = self.project.services[self.plugin.name]
            service.delete()
            service.purge()
        self.service = self.project.services.create(
            self.plugin.name, plugin=self.plugin
        )
    
    def tearDown(self):
        self.project.delete()
        self.project.purge()
    
    def test_ensureProjectPluginDirectoryExists(self):
        self.pluginSystem.ensureProjectPluginDirectoryExists(self.service)
        path = self.pluginSystem.paths.getProjectPluginPath(
            self.service.project, self.service.plugin
        )
        self.failUnless(os.path.exists(path))
        # check we can run it twice
        self.pluginSystem.ensureProjectPluginDirectoryExists(self.service)

