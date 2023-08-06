from kforge.test.customer.kui.base import KuiTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestMemberRegister),
        unittest.makeSuite(TestMemberAdmin),
        unittest.makeSuite(TestMemberJoin),
        unittest.makeSuite(TestMemberLeave),
    ]
    return unittest.TestSuite(suites)


class MemberTestCase(KuiTestCase):

    pass


class TestMemberRegister(MemberTestCase):

    def setUp(self):
        super(TestMemberRegister, self).setUp()
        self.registerPerson()
        self.loginPerson()
        self.registerProject()

    def test_list(self):
        self.getAssertContent(self.urlProjectMembers, 'Members')
        # Check the creator of the project is a member of the project.
        self.getAssertContent(self.urlProjectMembers, self.kuiPersonName)
        # Check Levin is not a member of the project.
        self.getAssertNotContent(self.urlProjectMembers, 'levin')
        self.getAssertNotContent(self.urlProjectMembers, 'Levin')


class TestMemberAdmin(MemberTestCase):

    def setUp(self):
        super(TestMemberAdmin, self).setUp()
        self.registerPerson()
        self.loginPerson('admin', 'pass')
        self.registerProject()

    def test_create(self):
        # Check not already on members page.
        self.getAssertNotContent(self.urlProjectMembers, self.kuiPersonName)
        self.getAssertNotContent(self.urlProjectMembers, ' Friend')
        # Check the 'add' button exists.
        self.getAssertContent(self.urlProjectMemberCreate, 'Add new member')
        # Check the form submission redirects.
        postdata = {'person': '/people/%s' % self.kuiPersonName, 'role': '/roles/Friend'}
        self.postAssertCode(self.urlProjectMemberCreate, postdata, code=302)
        # Check now on members page.
        self.getAssertContent(self.urlProjectMembers, self.kuiPersonName)
        self.getAssertContent(self.urlProjectMembers, ' Friend')

    def test_update(self):
        # Create the member. 
        postdata = {'person': '/people/%s' % self.kuiPersonName, 'role': '/roles/Friend'}
        self.postAssertCode(self.urlProjectMemberCreate, postdata, code=302)
        # Check not already on members page as a 'Developer'.
        self.getAssertContent(self.urlProjectMembers, self.kuiPersonName)
        self.getAssertContent(self.urlProjectMembers, ' Friend')
        self.getAssertNotContent(self.urlProjectMembers, ' Developer')
        # Check the 'edit' button exists.
        self.getAssertContent(self.urlProjectMemberUpdate, 'Update member')
        # Check the form submission redirects.
        postdata = {'role': '/roles/Developer'}
        self.postAssertCode(self.urlProjectMemberUpdate, postdata, code=302)
        # Chekc now on members page as a 'Developer'.
        self.getAssertContent(self.urlProjectMembers, self.kuiPersonName)
        self.getAssertNotContent(self.urlProjectMembers, ' Friend')
        self.getAssertContent(self.urlProjectMembers, ' Developer')

    def test_delete(self):
        # Create the member. 
        postdata = {'person': '/people/%s' % self.kuiPersonName, 'role': '/roles/Friend'}
        self.postAssertCode(self.urlProjectMemberCreate, postdata, code=302)
        # Check on members page.
        self.getAssertContent(self.urlProjectMembers, self.kuiPersonName)
        # Check the delete confirmation page.
        self.getAssertContent(self.urlProjectMemberDelete, 'Delete member')
        # Check the form submission redirects.
        postdata = {'Submit': 'Delete membership'}
        self.postAssertCode(self.urlProjectMemberDelete, postdata, code=302)
        # Check not on members page.
        self.getAssertNotContent(self.urlProjectMembers, self.kuiPersonName)


class TestMemberJoin(MemberTestCase):

    def setUp(self):
        super(TestMemberJoin, self).setUp()
        self.registerPerson()
        self.loginPerson()
        self.registerProject()

    def test_join(self):
        self.logoutPerson()

        members = self.registry.projects[self.kuiProjectName].members
        levin = self.registry.people['levin']

        # Check levin is not a member.
        self.failIfContains(levin, members)
        self.failIfContains(levin, members.pending)

        # Switch to existing user.
        self.loginPerson('levin', 'levin')
        self.getAssertContent(self.urlSiteHome, 'Levin')

        # Check button exists.
        joinButtonText = 'Request membership'
        self.getAssertContent(self.urlProjectRead, joinButtonText)
        # Request membership of project.
        self.postAssertContent(self.urlProjectJoin, {}, 'Thank you for your interest')
        # Check button no longer exists.
        self.getAssertNotContent(self.urlProjectRead, joinButtonText)

        # Check levin is now a pending member.
        self.failIfContains(levin, members)
        self.failUnlessContains(levin, members.pending)
        self.getAssertContent(self.urlProjectMembers, 'Levin')
        self.getAssertContent(self.urlProjectRead, 'Levin')

        # Switch back to newly registered user.
        self.logoutPerson()
        self.loginPerson()

        # Reject join request.
        self.urlProjectMembersReject = self.url_for('projects.admin', project=self.kuiProjectName,
            subcontroller='members', action='reject', id='levin')
        self.getAssertContent(self.urlProjectMembersReject, "Please confirm rejection of this membership request.")
        self.postAssertCode(self.urlProjectMembersReject, {'Submit': 'Reject member'})

        # Check levin is no longer a member.
        self.failIfContains(levin, members)
        self.failIfContains(levin, members.pending)
        # Check no longer on members page.
        self.getAssertNotContent(self.urlProjectMembers, 'Levin')
        self.getAssertNotContent(self.urlProjectRead, 'Levin')

        # Switch to existing user.
        self.logoutPerson()
        self.loginPerson('levin', 'levin')

        # Check button exists.
        self.getAssertContent(self.urlProjectRead, joinButtonText)

        # Request membership of project.
        self.postAssertContent(self.urlProjectJoin, {}, 'Thank you for your interest')

        # Switch back to newly registered user.
        self.logoutPerson()
        self.loginPerson()

        # Check levin is now a pending member.
        self.failUnlessContains(levin, members.pending)
        self.failIfContains(levin, members)
        self.getAssertContent(self.urlProjectMembers, 'Levin')
        self.getAssertContent(self.urlProjectRead, 'Levin')

        # Check we do not have any developers.
        self.failIfEqual(members.pending[levin].role.name, 'Developer')
        self.getAssertNotContent(self.urlProjectMembers, 'Developer')

        # Approve join request.
        self.urlProjectMembersApprove = self.url_for('projects.admin', project=self.kuiProjectName,
            subcontroller='members', action='approve', id='levin')
        self.getAssertContent(self.urlProjectMembersApprove, "Please select an appropriate role for this member.")
        self.postAssertCode(self.urlProjectMembersApprove, {'approve-submission': 'submit your changes', 'role': '/roles/Developer'})

        # Check levin is now a member.
        self.failUnlessContains(levin, members)
        self.failIfContains(levin, members.pending)
        self.getAssertContent(self.urlProjectMembers, 'Levin')
        self.getAssertContent(self.urlProjectRead, 'Levin')

        # Check we do have a developers.
        self.failUnlessEqual(members[levin].role.name, 'Developer')
        self.getAssertContent(self.urlProjectMembers, 'Developer')



class TestMemberLeave(MemberTestCase):

    def test_join(self):
        self.logoutPerson()


