from kforge.filesystem import FileSystem
import unittest
from kforge.testunit import TestCase

def suite():
    suites = [
        unittest.makeSuite(FileSystemTest),
    ]
    return unittest.TestSuite(suites)

class FileSystemTest(TestCase):
    
    def setUp(self):
        super(FileSystemTest, self).setUp()
        self.filesystem = FileSystem()
    
    def getAllServices(self):
        servicesList = []
        for project in self.registry.projects:
            for service in project.services:
                servicesList.append(service)
        return servicesList
        
    def testGetProjectPath(self):
        for project in self.registry.projects:
            path = self.filesystem.getProjectPath(project)
            self.failUnless(project.name in path)
    
    def testGetProjectPluginPath(self):
        for service in self.getAllServices():
            project = service.project
            plugin = service.plugin
            path = self.filesystem.getProjectPluginPath(project, plugin)
            self.failUnless(project.name in path)
    
    def testGetServicePath(self):
        for service in self.getAllServices():
            self.filesystem.getServicePath(service)
 
