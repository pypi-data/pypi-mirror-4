import unittest
from kforge.exceptions import *
from kforge.dom.testunit import TestCase

def suite():
    suites = [
        unittest.makeSuite(TestProject),
    ]
    return unittest.TestSuite(suites)

class ProjectTestCase(TestCase):

    def setUp(self):
        super(ProjectTestCase, self).setUp()
        self.fixtureName = 'TestProject'
        self.projects = self.registry.projects
        try:
            self.project = self.projects.create(self.fixtureName)
        except:
            project = self.projects[self.fixtureName]
            project.delete()
            project.purge()
            raise

    def tearDown(self):
        self.project.delete()
        self.project.purge()
        self.project = None
        super(ProjectTestCase, self).tearDown()

    
class TestProject(ProjectTestCase):
    
    def test_new(self):
        self.failUnless(self.project, "New project could not be created.")
        # Suspended isUnique=True.
        #self.failUnlessRaises(KforgeDomError, self.projects.create, self.fixtureName)

    def test___getitem__(self):
        self.failUnless(self.projects[self.fixtureName], "New project could not be found.")
        self.failUnlessRaises(KforgeRegistryKeyError, self.projects.__getitem__, 'TestAlien')

    def test_delete(self):
        self.project.delete()
        self.project.purge()
        self.failUnlessRaises(KforgeRegistryKeyError, self.projects.__getitem__, self.fixtureName)

    def test___delitem__(self):
        del self.projects[self.fixtureName]
        self.failUnlessRaises(KforgeRegistryKeyError, self.projects.__getitem__, self.fixtureName)

    def test_is(self):
        self.failUnless(self.projects.has_key(self.fixtureName), "New project doesn't appear to be there.")
        self.failIf(self.projects.has_key('TestAlien'), "Strange project does appear to be there.")
        self.project.delete()
        self.project.purge()
        self.failIf(self.projects.has_key(self.fixtureName), "New project still appears to be there.")

    def test_save(self):
        self.assertEquals(self.project.title, "", "Already has a title.")
        self.project.title = "Test Title"
        self.project.purpose = "Test Purpose"
        self.project.description = "Test Description"
        self.assertEquals(self.project.title, "Test Title", "Project doesn't have title attribute.")
        self.assertEquals(self.project.purpose, "Test Purpose", "Project doesn't have purpose attribute.")
        self.assertEquals(self.project.description, "Test Description", "Project doesn't have purpose attribute.")
        self.project.save()
        project = self.projects[self.fixtureName]
        self.assertEquals(project.title, "Test Title", "Retrieved project has wrong title.")
        self.assertEquals(project.purpose, "Test Purpose", "Project doesn't have purpose attribute.")
        self.assertEquals(project.description, "Test Description", "Project doesn't have purpose attribute.")
        project.title = "Other Title"
        self.assertEquals(self.project.title, "Other Title", "Suspect duplicate domain objects!!")

    def test_licenses(self):
        self.failIf(self.project.licenses.count(), "Already has a license...")
        l1 = self.registry.licenses[1]
        l2 = self.registry.licenses[2]
        l3 = self.registry.licenses[3]
        l4 = self.registry.licenses[4]
        self.project.licenses.create(l1)
        self.project.licenses.create(l2)
        self.project.licenses.create(l3)
        self.project.licenses.create(l4)
        count = self.project.licenses.count()
        self.assertEquals(count, 4, "Wrong number of licenses: %s" % count)
        [l.delete() for l in self.project.licenses]


