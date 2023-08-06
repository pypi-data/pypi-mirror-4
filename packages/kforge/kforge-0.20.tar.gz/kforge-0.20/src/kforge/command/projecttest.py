import unittest
from kforge.testunit import TestCase
from kforge.command.project import *
from kforge.exceptions import *

def suite():
    suites = [
        unittest.makeSuite(TestProjectList),
        unittest.makeSuite(TestProjectCreate),
        unittest.makeSuite(TestProjectRead),
        unittest.makeSuite(TestProjectDelete),
        unittest.makeSuite(TestProjectUndelete),
        unittest.makeSuite(TestProjectPurge),
    ]
    return unittest.TestSuite(suites)

class TestProjectList(TestCase):
    "TestCase for the ProjectList command."

    projectName = 'TestProjectList'

    def setUp(self):
        super(TestProjectList, self).setUp()
        if self.projectName in self.registry.projects.getAll():
            project = self.registry.projects[self.projectName]
            project.delete()
            project.purge()
        self.project = self.registry.projects.create(self.projectName)
        self.command = kforge.command.ProjectList()

    def tearDown(self):
        self.project.delete()
        self.project.purge()

    def testExecute(self):
        self.failUnless(self.projectName in self.registry.projects)
        self.command.execute()
        self.failUnless(len(self.command.results))


class TestProjectCreate(TestCase):
    "TestCase for the ProjectCreate command."

    projectName = 'TestProjectCreate'

    def setUp(self):
        super(TestProjectCreate, self).setUp()
        if self.projectName in self.registry.projects.getAll():
            project = self.registry.projects[self.projectName]
            project.delete()
            project.purge()
        self.command = kforge.command.ProjectCreate(self.projectName)

    def tearDown(self):
        if self.projectName in self.registry.projects.getAll():
            project = self.registry.projects[self.projectName]
            project.delete()
            project.purge()

    def testExecute(self):
        self.failIf(self.projectName in self.registry.projects)
        self.command.execute()
        self.failUnless(self.projectName in self.registry.projects)

    def testErrorProjectExists(self):
        self.command.execute()
        # Suspended isUnique=True.
        #self.failUnlessRaises(KforgeCommandError, self.command.execute)


class TestProjectRead(TestCase):
    "TestCase for the ProjectRead command."

    projectName = 'TestProjectRead'

    def setUp(self):
        super(TestProjectRead, self).setUp()
        if self.projectName in self.registry.projects.getAll():
            project = self.registry.projects[self.projectName]
            project.delete()
            project.purge()
        self.project = self.registry.projects.create(self.projectName)
        self.command = kforge.command.ProjectRead(self.projectName)

    def tearDown(self):
        self.project.delete()
        self.project.purge()

    def testExecute(self):
        self.failUnless(self.projectName in self.registry.projects)
        self.command.execute()
        self.assertEquals(self.command.project.name, self.projectName)

# todo: update?

class TestProjectDelete(TestCase):
    "TestCase for the ProjectDelete command."

    def setUp(self):
        super(TestProjectDelete, self).setUp()
        self.fixtureName = 'TestProjectDelete'
        if self.fixtureName in self.registry.projects.getAll():
            project = self.registry.projects[self.fixtureName]
            project.delete()
            project.purge()
        self.project = self.registry.projects.create(self.fixtureName)
        self.command = kforge.command.ProjectDelete(self.fixtureName)

    def tearDown(self):
        self.project.delete()
        self.project.purge()

    def testExecute(self):
        self.failUnless(self.fixtureName in self.registry.projects)
        self.command.execute()
        self.failIf(self.fixtureName in self.registry.projects)

    def testErrorNoProject(self):
        self.project.delete()
        self.failUnlessRaises(KforgeCommandError, self.command.execute)


class TestProjectUndelete(TestCase):
    "TestCase for the ProjectUndelete command."

    def setUp(self):
        super(TestProjectUndelete, self).setUp()
        self.fixtureName = 'TestProjectUndelete'
        if self.fixtureName in self.registry.projects.getAll():
            project = self.registry.projects[self.fixtureName]
            project.delete()
            project.purge()
        self.project = self.registry.projects.create(self.fixtureName)
        self.project.delete()
        self.command = ProjectUndelete(self.fixtureName)

    def tearDown(self):
        if self.fixtureName in self.registry.projects.getAll():
            project = self.registry.projects.getAll()[self.fixtureName]
            project.delete()
            project.purge()
        self.command = None

    def testExecute(self):
        self.failUnless(self.fixtureName in self.registry.projects.getDeleted())
        self.command.execute()
        self.failIf(self.fixtureName in self.registry.projects.getDeleted())
        self.failUnless(self.fixtureName in self.registry.projects)

    def testErrorNoProject(self):
        self.command.execute()
        self.failUnlessRaises(KforgeCommandError, self.command.execute)


class TestProjectPurge(TestCase):
    "TestCase for the ProjectPurge command."

    def setUp(self):
        super(TestProjectPurge, self).setUp()
        self.fixtureName = 'TestProjectPurge'
        if self.fixtureName in self.registry.projects.getAll():
            project = self.registry.projects[self.fixtureName]
            project.delete()
            project.purge()
        self.project = self.registry.projects.create(self.fixtureName)
        self.project.delete()
        self.command = ProjectPurge(self.fixtureName)

    def tearDown(self):
        if self.fixtureName in self.registry.projects.getAll():
            project = self.registry.projects.getAll()[self.fixtureName]
            project.delete()
            project.purge()
        self.command = None

    def testExecute(self):
        self.failUnless(self.fixtureName in self.registry.projects.getDeleted())
        self.command.execute()
        self.failIf(self.fixtureName in self.registry.projects.getDeleted())
        self.failIf(self.fixtureName in self.registry.projects)
        self.failIf(self.fixtureName in self.registry.projects.getAll())

    def testErrorNoProject(self):
        self.command.execute()
        self.failUnlessRaises(KforgeCommandError, self.command.execute)


