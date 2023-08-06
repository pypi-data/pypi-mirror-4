from kforge.testunit import TestCase
from kforge.dom.projecttest import ProjectTestCase
import unittest
import kforge.command
import kforge.plugin.accesscontrol
from kforge.exceptions import *

def suite():
    suites = [
            unittest.makeSuite(TestPlugin),
            unittest.makeSuite(TestProjectAccess),
        ]
    return unittest.TestSuite(suites)


class TestPlugin(TestCase):
    """
    TestCase for the access control plugin.
    """

    def setUp(self):
        super(TestPlugin, self).setUp()
        domainObject = type('Plugin', (), {})
        domainObject.name = 'accesscontrol'
        self.plugin = kforge.plugin.accesscontrol.Plugin(domainObject)
        self.fixtureName = 'TestAccessControlPlugin'
        if self.fixtureName in self.registry.people:
            person = self.registry.people[self.fixtureName]
            person.delete()
            person.purge()
        self.person = self.registry.people.create(self.fixtureName)

    def tearDown(self):
        self.command = None
        self.plugin = None
        if self.fixtureName in self.registry.people:
            person = self.registry.people[self.fixtureName]
            person.delete()
            person.purge()
            person = None

    def test_pluginSystemExists(self):
        self.failUnless(self.plugin)

    def test_onCreatePerson(self):
        # Remove all the grants.
        for grant in self.person.grants:
            grant.delete()
        self.failIf(len(self.person.grants.keys()),
            "There are grants: %s" % len(self.person.grants.keys()))
        # Setup the grants again.
        self.plugin.onPersonCreate(self.person)
        self.failUnless(len(self.person.grants.keys()),
            "There are no grants: %s" % self.person.grants.keys())


class TestProjectAccess(ProjectTestCase):

    def testAdjustPrivacyOfMembersProject(self):
        # Start with public project, neither levin nor natasha are members.
        # Add and remove members and then make the project hidden. The project
        # should be visible to the project members and the site admins only.
        self.failIfProjectNotVisible()
        self.failIfProjectNotVisible('levin')
        self.failIfProjectNotVisible('natasha')
        self.failIfProjectNotVisible('admin')

        self.addMember('levin')
        self.failIfProjectNotVisible()
        self.failIfProjectNotVisible('levin')
        self.failIfProjectNotVisible('natasha')
        self.failIfProjectNotVisible('admin')

        self.setProjectPrivate()
        self.failIfProjectVisible()
        self.failIfProjectNotVisible('levin')
        self.failIfProjectVisible('natasha')
        self.failIfProjectNotVisible('admin')

        self.setProjectPublic()
        self.failIfProjectNotVisible()
        self.failIfProjectNotVisible('levin')
        self.failIfProjectNotVisible('natasha')
        self.failIfProjectNotVisible('admin')

        self.addMember('natasha')
        self.failIfProjectNotVisible()
        self.failIfProjectNotVisible('levin')
        self.failIfProjectNotVisible('natasha')
        self.failIfProjectNotVisible('admin')

        self.setProjectPrivate()
        self.failIfProjectVisible()
        self.failIfProjectNotVisible('levin')
        self.failIfProjectNotVisible('natasha')
        self.failIfProjectNotVisible('admin')

        self.setProjectPublic()
        self.failIfProjectNotVisible()
        self.failIfProjectNotVisible('levin')
        self.failIfProjectNotVisible('natasha')
        self.failIfProjectNotVisible('admin')

        self.removeMember('levin')
        self.failIfProjectNotVisible()
        self.failIfProjectNotVisible('levin')
        self.failIfProjectNotVisible('natasha')
        self.failIfProjectNotVisible('admin')

        self.setProjectPrivate()
        self.failIfProjectVisible()
        self.failIfProjectVisible('levin')
        self.failIfProjectNotVisible('natasha')
        self.failIfProjectNotVisible('admin')

        self.setProjectPublic()
        self.failIfProjectNotVisible()
        self.failIfProjectNotVisible('levin')
        self.failIfProjectNotVisible('natasha')
        self.failIfProjectNotVisible('admin')

        self.removeMember('natasha')
        self.failIfProjectNotVisible()
        self.failIfProjectNotVisible('levin')
        self.failIfProjectNotVisible('natasha')
        self.failIfProjectNotVisible('admin')

        self.setProjectPrivate()
        self.failIfProjectVisible()
        self.failIfProjectVisible('levin')
        self.failIfProjectVisible('natasha')
        self.failIfProjectNotVisible('admin')

    def testAdjustMembersOfPrivateProject(self):
        # Start with public project, neither levin nor natasha are members.
        # Make the project hidden and then add and remove members. The project
        # should be visible to the project members and the site admins only.
        self.failIfProjectNotVisible()
        self.failIfProjectNotVisible('levin')
        self.failIfProjectNotVisible('natasha')
        self.failIfProjectNotVisible('admin')

        self.setProjectPrivate()
        self.failIfProjectVisible()
        self.failIfProjectVisible('levin')
        self.failIfProjectVisible('natasha')
        self.failIfProjectNotVisible('admin')

        self.addMember('levin')
        self.failIfProjectVisible()
        self.failIfProjectNotVisible('levin')
        self.failIfProjectVisible('natasha')
        self.failIfProjectNotVisible('admin')

        self.addMember('natasha')
        self.failIfProjectVisible()
        self.failIfProjectNotVisible('levin')
        self.failIfProjectNotVisible('natasha')
        self.failIfProjectNotVisible('admin')

        self.removeMember('natasha')
        self.failIfProjectVisible()
        self.failIfProjectNotVisible('levin')
        self.failIfProjectVisible('natasha')
        self.failIfProjectNotVisible('admin')

        self.removeMember('levin')
        self.failIfProjectVisible()
        self.failIfProjectVisible('levin')
        self.failIfProjectVisible('natasha')
        self.failIfProjectNotVisible('admin')

    def setProjectPrivate(self):
        self.setProjectIsHidden(True)

    def setProjectPublic(self):
        self.setProjectIsHidden(False)

    def setProjectIsHidden(self, isHidden):
        self.project.isHidden = isHidden
        self.project.save()

    def addMember(self, personName):
        person = self.registry.people[personName]
        self.project.members.create(person=person)
        assert person in self.project.members

    def removeMember(self, personName):
        person = self.registry.people[personName]
        del(self.project.members[person])
        assert person not in self.project.members

    def failIfProjectNotVisible(self, viewerName=None):
        #print "Project is now: isHidden: '%s' readableBy: '%s'" % (self.project.isHidden, self.project.readableBy)
        self.failIfProjectNotListed(viewerName)
        self.failIfProjectNotReadable(viewerName)
        self.failIfProjectNotSearchable(viewerName)
        self.failIfProjectNotIndexed(viewerName)

    def failIfProjectVisible(self, viewerName=None):
        #print "Project is now: isHidden: '%s' readableBy: '%s'" % (self.project.isHidden, self.project.readableBy)
        self.failIfProjectListed(viewerName)
        self.failIfProjectReadable(viewerName)
        self.failIfProjectSearchable(viewerName)
        self.failIfProjectIndexed(viewerName)

    def failIfProjectNotListed(self, viewerName=None):
        msg = "Project is not listed (project.readableBy: '%s')." % self.project.readableBy
        self.failUnless(self.isProjectListed(viewerName=viewerName), msg)

    def failIfProjectListed(self, viewerName=None):
        msg = "Project is listed (project.readableBy: '%s')." % self.project.readableBy
        self.failIf(self.isProjectListed(viewerName=viewerName), msg)

    def isProjectListed(self, viewerName=''):
        projects = self.projects.findDomainObjects(__accessedBy__=viewerName)
        return self.fixtureName in [p.name for p in projects]

    def failIfProjectNotReadable(self, viewerName=None):
        msg = "Project is not readable (project.isHidden: '%s' project.readableBy: '%s')." % (self.project.isHidden, self.project.readableBy)
        self.failUnless(self.isProjectReadable(viewerName=viewerName), msg)

    def failIfProjectReadable(self, viewerName=None):
        msg = "Project is readable (project.isHidden: '%s' project.readableBy: '%s')." % (self.project.isHidden, self.project.readableBy)
        self.failIf(self.isProjectReadable(viewerName=viewerName), msg)

    def isProjectReadable(self, viewerName=''):
        try:
            self.projects.find(self.fixtureName, __accessedBy__=viewerName)
        except KforgeRegistryKeyError:
            return False
        else:
            return True

        
    def failIfProjectNotSearchable(self, viewerName=None):
        msg = "Project is not searchable (project.isHidden: '%s' project.readableBy: '%s')." % (self.project.isHidden, self.project.readableBy)
        self.failUnless(self.isProjectSearchable(viewerName=viewerName), msg)

    def failIfProjectSearchable(self, viewerName=None):
        msg = "Project is searchable (project.isHidden: '%s' project.readableBy: '%s')." % (self.project.isHidden, self.project.readableBy)
        self.failIf(self.isProjectSearchable(viewerName=viewerName), msg)

    def isProjectSearchable(self, viewerName=''):
        results = self.projects.search(userQuery=self.fixtureName, attributeNames=['name'], __accessedBy__=viewerName)
        return len(results) == 1 and results[0].name == self.fixtureName
        
    def failIfProjectNotIndexed(self, viewerName=None):
        msg = "Project is not indexed (project.isHidden: '%s' project.readableBy: '%s')." % (self.project.isHidden, self.project.readableBy)
        self.failUnless(self.isProjectIndexed(viewerName=viewerName), msg)

    def failIfProjectIndexed(self, viewerName=None):
        msg = "Project is indexed (project.isHidden: '%s' project.readableBy: '%s')." % (self.project.isHidden, self.project.readableBy)
        self.failIf(self.isProjectIndexed(viewerName=viewerName), msg)

    def isProjectIndexed(self, viewerName=''):
        results = self.projects.startsWith(value=self.fixtureName,attributeName='name', __accessedBy__=viewerName)
        return len(results) == 1 and results[0].name == self.fixtureName
        
