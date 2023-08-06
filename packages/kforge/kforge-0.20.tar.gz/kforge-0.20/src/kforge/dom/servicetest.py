import unittest
from kforge.exceptions import *
from kforge.dom.testunit import TestCase

def suite():
    suites = [
        unittest.makeSuite(TestService),
    ]
    return unittest.TestSuite(suites)


class TestService(TestCase):
    "TestCase for the Service class."
    
    def setUp(self):
        super(TestService, self).setUp()
        self.projects = self.registry.projects
        self.plugin = self.registry.plugins['example']
        try:
            project = self.projects.getAll()['TestService']
            project.delete()
            project.purge()
        except:
            pass
        
        self.project = self.projects.create('TestService')
        self.service = self.project.services.create(
            self.plugin.name, plugin=self.plugin
        )

    def tearDown(self):
        project = self.projects.getAll()['TestService']
        project.delete()
        project.purge()
        #super(TestService, self).tearDown()
        #try:
        #    self.service.delete()
        #finally:
        #    project = self.projects.getAll()['TestService']
        #    project.delete()
        #    project.purge()

    def test_class(self):
        self.failIf(self.service.getExtnRegister())

    def test_delete(self):
        self.service.delete()
        self.failUnlessRaises(KforgeRegistryKeyError, 
            self.project.services.__getitem__, self.plugin.name
        )
        
    def test_find(self):
        service = self.project.services[self.plugin.name]
        self.failUnless(service, "No service object found.")
        self.assertEquals(self.service, service, "Wrong service found!")
        
    def test_new(self):
        self.failUnless(self.service)
        self.failUnless(self.service.project)
        self.assertEquals(self.service.project, self.project)
        self.failIf(self.service.isSystemStartedAfterDateCreated())
        self.dictionary.setSystemStarted()
        self.failUnless(self.service.isSystemStartedAfterDateCreated())

