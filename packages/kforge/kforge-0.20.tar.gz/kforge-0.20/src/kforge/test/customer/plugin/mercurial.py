import unittest
from kforge.test.customer.plugin.base import PluginTestCase

# Tester account needs .hgrc file, for example.
#
#[ui]
#username = Your Name <your.name@appropriatesoftware.net>
#
#[auth]
#tag.prefix = http://kforge.dev.localhost
#tag.username = admin 
#tag.password = pass


def suite():
    suites = [
        unittest.makeSuite(TestMercurial),
    ]
    return unittest.TestSuite(suites)


class TestMercurial(PluginTestCase):

    requiredPlugins = ['mercurial']

    def testHttpClient(self):
        url = self.getServicePath('mercurial')
        self.getAssertCode(url, 404)
        self.createService('mercurial', 'mercurial')
        self.getAssertContent(url, 'hglogo.png', code=200)
        self.getAssertCode(url, 200)
        self.logoutPerson()
        self.getAssertCode(url, 401)
        self.setBasicAuthPerson()
        self.getAssertContent(url, 'hglogo.png', code=200)
        self.logoutPerson()
        self.getAssertCode(url, 401)

    def testMercurialClient(self):
        self.createService('mercurial', 'mercurial')
        commitMsg = 'Testing HTTP access client...'
        # Todo: Check the .hgrc file has necessary lines.
        self.mercurialCloneAddCommitPush('mercurial', commitMsg)
        self.setBasicAuthPerson()
        url = self.getServicePath('mercurial')
        self.getAssertContent(url, commitMsg)

    def testPerformance(self):
        self.createService('mercurial', 'mercurial2')
        # Check performance for project developer.
        self.changePersonProjectRole('Developer')
        self.mercurialCloneAddCommitPush('mercurial2', 'Testing Mercurial HTTP access (push performance)...', checkPushPerformance=30)
        self.mercurialCloneAddCommitPush('mercurial2', 'Testing Mercurial HTTP access (clone performance)...', checkClonePerformance=30)
        

