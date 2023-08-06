import unittest
from kforge.test.customer.plugin.base import PluginTestCase
from kforge.dictionarywords import APACHE_PYTHON_MODULE

# Tester account needs ~/.netrc file with permission 600.
#
#machine kforge.dev.lilac
#login admin
#password pass

def suite():
    suites = [
        unittest.makeSuite(TestGit),
    ]
    return unittest.TestSuite(suites)


class TestGit(PluginTestCase):

    requiredPlugins = ['git']

    def testHttpClient(self):
        url = self.getServicePath('git')
        self.getAssertCode(url, 404)
        self.createService('git', 'git')
        content = 'Git repository' 
        self.getAssertContent(url, content, code=200)
        self.getAssertContent(url+'?p=git;a=summary', content, code=200)
        self.logoutPerson()
        self.getAssertCode(url, 401)
        self.setBasicAuthPerson()
        self.getAssertContent(url, content)
        self.getAssertContent(url, 'No commits')
        self.logoutPerson()
        self.getAssertCode(url, 401)

    # Commented out this test, because it prompts for user input 4 times
    # and can't seem to suppress that. 
    # Todo: Suppress prompting for username/password/username/password.
    # Todo: Fix this by using pexpect.
    def testGitClient(self):
        # Todo: Code to check the .netrc file has necessary lines.
        # As project administrator.
        canAnswerUsernamePasswordPrompt = False
        self.createService('git', 'git')
        self.createService('git', 'git2')
        self.createService('git', 'git3')
        self.createService('git', 'git4')
        self.createService('git', 'git5')
        self.gitCloneAddCommitPush('git', 'Testing SSH access (project admin)...')
        # As project developer.
        self.changePersonRole('admin', 'Developer')
        #print "Dev access...................."
        self.gitCloneAddCommitPush('git2', 'Testing SSH access (project developer)...')
        # As project friend.
        self.changePersonRole('admin', 'Friend')
        #print "Friend access...................."
        if canAnswerUsernamePasswordPrompt:
            self.gitCloneAddCommitPush('git3', 'Testing SSH access (project friend)...', expectPushFail=True)
            # As project visitor.
            self.changePersonRole('admin', 'Visitor')
            #print "Visitor access...................."
            self.gitCloneAddCommitPush('git4', 'Testing SSH access (project visitor)...', expectCloneFail=True)
        # As project administrator, again.
        self.changePersonRole('admin', 'Administrator')
        self.gitCloneAddCommitPush('git5', 'Testing SSH access (project admin, again)...')
        
    def tearDown(self):
        self.changePersonRole('admin', 'Administrator')
        super(TestGit, self).tearDown()

