from kforge.test.customer.kui.base import KuiTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestReadProjects),
        unittest.makeSuite(TestProjectCRUD),
    ]
    return unittest.TestSuite(suites)


class TestReadProjects(KuiTestCase):
 
    kuiProjectName = 'administration'

    def testProjectIndex(self):
        self.getAssertContent(self.urlProjects, 'Projects')
        self.getAssertContent(self.urlProjectSearch, 'Search projects')

    def testProjectSearch(self):
        params = {'userQuery': 'z'}
        self.postAssertNotContent(self.urlProjectSearch, params, self.kuiProjectName)
        params = {'userQuery': 'a'}
        self.postAssertContent(self.urlProjectSearch, params, self.kuiProjectName)
        
    def testProjectRead(self):
        self.getAssertContent(self.urlProjectRead, self.kuiProjectName)
        
    def testMembersRead(self):
        self.getAssertContent(self.urlProjectMembers, self.kuiProjectName)
        self.getAssertContent(self.urlProjectMembers, 'Administrator')
        self.getAssertContent(self.urlProjectMembers, 'Visitor')
        
    def testServicesRead(self):
        self.getAssertContent(self.urlProjectServices, self.kuiProjectName)


class TestProjectCRUD(KuiTestCase):

    def setUp(self):
        super(TestProjectCRUD, self).setUp()
        self.registerPerson()
        self.loginPerson()

    def testCRUD(self):
        # Create
        self.failIf(self.kuiProjectName in self.registry.projects)
        content = 'Register a new project'
        self.getAssertContent(self.urlProjectCreate, content)

        content = 'Please enter the details of your new project below'
        self.getAssertContent(self.urlProjectCreate, content)

        params = {}
        params['title'] = self.kuiProjectTitle
        params['licenses'] = self.kuiProjectLicense
        params['description'] = self.kuiProjectDescription
        params['name'] = self.kuiProjectName
        self.postAssertCode(self.urlProjectCreate, params)

        self.failUnless(self.kuiProjectName in self.registry.projects)
        project = self.registry.projects[self.kuiProjectName]
        person = self.registry.people[self.kuiPersonName]
        self.failUnless(person in project.members)
        membership = project.members[person]
        self.failUnlessEqual(membership.role.name, 'Administrator')

        # Read
        self.failUnless(self.kuiProjectName in self.registry.projects)
        content = 'Edit'
        self.getAssertContent(self.urlProjectRead, content)

        content = '%s' % self.kuiProjectName
        self.getAssertContent(self.urlProjectRead, content)

        content = '%s' % self.kuiProjectDescription
        self.getAssertContent(self.urlProjectRead, content)

        content = '%s' % self.kuiProjectTitle
        self.getAssertContent(self.urlProjectRead, content)

        # Update
        self.failUnless(self.kuiProjectName in self.registry.projects)
        content = '%s settings' % self.kuiProjectTitle
        self.getAssertContent(self.urlProjectUpdate, content)
        self.getAssertContent(self.urlProjectUpdate, self.kuiProjectName)
        self.getAssertContent(self.urlProjectUpdate, self.kuiProjectTitle)
        self.getAssertContent(self.urlProjectUpdate, self.kuiProjectDescription)

        content = 'Delete'
        self.getAssertContent(self.urlProjectUpdate, content)

        # Delete
        self.failUnless(self.kuiProjectName in self.registry.projects)
        params = {}
        self.deleteProject()
        self.failIf(self.kuiProjectName in self.registry.projects)

