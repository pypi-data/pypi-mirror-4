import unittest
from kforge.testunit import TestCase
from kforge.command.service import *
from kforge.exceptions import *

def suite():
    suites = [
#        unittest.makeSuite(TestServiceCreate),
#        unittest.makeSuite(TestServiceDelete),
    ]
    return unittest.TestSuite(suites)

#class ServiceTestCase(TestCase):
#
#    pluginName = 'example'
#    fixtureName = 'ServiceTestCase'
#    
#    def setUp(self):
#        super(ServiceTestCase, self).setUp()
#        self.service = None
#        self.plugin = self.registry.plugins[self.pluginName]
#        self.projects = self.registry.projects
#        try: 
#            self.failIf(self.fixtureName in self.registry.projects.getAll())
#        except:
#            project = self.registry.projects.getAll()[self.fixtureName]
#            project.delete()
#            project.purge()
#        
#        self.project = self.projects.create(self.fixtureName)
#        try: 
#            self.failIf(self.plugin.services.findDomainObjects(project=self.project))
#        except:
#            try:
#                self.project.delete()
#                self.project.purge()
#            finally:
#                raise
#        self.failUnless(self.project)
#        self.failUnless(self.plugin)
#
#        try:
#            self.command = self.buildCommand()
#        except:
#            try:
#                self.pluginName = ""
#            finally:
#                self.project.delete()
#                self.project.purge()
#            raise
#        else:
#            return 1
#            
#    def tearDown(self):
#        try:
#            if self.command and self.command.service:
#                self.command.service.delete()
#                self.command.service.purge()
#            elif self.service:
#                self.service.delete()
#                self.service.purge()
#        finally:
#            self.command = None
#            self.project.delete()
#            self.project.purge()
#
#
#class TestServiceCreate(ServiceTestCase):
#    "TestCase for the ServiceCreate command."
#
#    fixtureName = 'TestServiceCreate'
#
#    def buildCommand(self):
#        return ServiceCreate(
#            plugin=self.plugin,
#            project=self.project,
#            name=self.fixtureName,
#        )
#
#    def testExecute(self):
#        self.failIf(self.fixtureName in self.project.services.getAll())
#        self.command.execute()
#        self.failUnless(self.command.service, "No service on command.")
#        self.service = self.command.service
#        self.failUnless(self.fixtureName in self.project.services)
#
#    def testErrorServiceExists(self):
#        self.command.execute()
#        # Suspended isUnique=True.
#        #self.failUnlessRaises(KforgeCommandError, self.command.execute)
#        
#    def testErrorNoPlugin(self):
#        self.command = ServiceCreate(
#            project=self.project,
#            name=self.fixtureName,
#        )
#        self.failUnlessRaises(KforgeCommandError, self.command.execute)
#
#    def testErrorNoProject(self):
#        self.command = ServiceCreate(
#            plugin=self.plugin,
#            name=self.fixtureName,
#        )
#        self.failUnlessRaises(KforgeCommandError, self.command.execute)
#
#
#class TestServiceDelete(ServiceTestCase):
#    "TestCase for the ServiceDelete command."
#
#    fixtureName = 'TestServiceDelete'
#    
#    def setUp(self):
#        super(TestServiceDelete, self).setUp()
#        self.service = self.project.services.create(
#            self.fixtureName, plugin=self.plugin
#        )
#        self.failUnless(self.service)
#
#    def buildCommand():
#        self.command = ServiceDelete(
#            project=self.project,
#            plugin=self.plugin,
#            name=self.fixtureName,
#        )
#
#    def testExecute(self):
#        self.failUnless(self.fixtureName in self.project.services)
#        self.command.execute()
#        self.failIf(self.fixtureName in self.project.services)
#
#    def testErrorNoService(self):
#        self.command.execute()
#        self.failUnlessRaises(KforgeCommandError, self.command.execute)
#        self.command = ServiceDelete(
#            project=self.project,
#            plugin=self.plugin,
#            name=self.fixtureName,
#        )
#
