import unittest
from kforge.test.customer.plugin.base import PluginTestCase
from kforge.dictionarywords import *
from kforge.plugin.svn import SVN_VIEWVC_IS_ENABLED

def suite():
    suites = [
        unittest.makeSuite(TestSvnWithHttpClient),
        unittest.makeSuite(TestSvnWithSvnClient),
        unittest.makeSuite(TestSvnNavigationBar),
    ]
    return unittest.TestSuite(suites)


class SvnTestCase(PluginTestCase):

    requiredPlugins = ['svn']

    def urlViewvc(self, url):
        urlSplit = url.strip().split('/')
        urlSplit[2] = 'viewvc/'+urlSplit[2]+''
        return '/'.join(urlSplit)


class TestSvnWithHttpClient(SvnTestCase):

    def testHttpClient(self):
        url = self.getServicePath('svn')
        self.getAssertCode(url, 404)
        self.createService('svn', 'svn')
        content = 'svn - Revision 0: /'
        # A 401 return indicates the access control handlers are running in mod_wsgi.
        # See ticket #94. http://kforge.appropriatesoftware.net/kforge/trac/ticket/94
        self.getAssertCode(url, 200)
        self.logoutPerson()
        self.getAssertCode(url, 401)
        self.setBasicAuthPerson()
        self.getAssertContent(url, content)
        self.logoutPerson()
        self.getAssertCode(url, 401)
        # Check viewVC location.
        if not self.dictionary[SVN_VIEWVC_IS_ENABLED]:
            return
        url = self.urlViewvc(url)
        self.getAssertCode(url, 401)
        self.loginPerson()
        self.getAssertContent(url, 'ViewVC Help', code=200)


class TestSvnWithSvnClient(SvnTestCase):

    def testSubversionClient(self):
        self.createService('svn', 'svn')
        self.svnCheckoutAddCommit('svn', 'Just testing...')

    def testPerformance(self):
        self.createService('svn', 'svn2')
        # Check performance for project developer.
        self.changePersonProjectRole('Developer')
        self.svnCheckoutAddCommit('svn2', 'Testing Subversion HTTP access (commit performance)...', checkCommitPerformance=30)
        self.svnCheckoutAddCommit('svn2', 'Testing Subversion HTTP access (checkout performance)...', checkCheckoutPerformance=30)


class TestSvnNavigationBar(SvnTestCase):

    def testNavigationBar(self):
        if not self.dictionary[SVN_VIEWVC_IS_ENABLED]:
            return
        self.createService('svn', 'svn')
        url = self.urlViewvc(self.getServicePath('svn'))
        # Check the Navigation bar has been included.
        self.getAssertContent(url, 'Profile', code=200)
        # Commit an HTML file to the repository.
        fileName = 'index.html'
        content = "<html><head></head><body></body></html>"
        #content = "<html></html>"
        self.svnCheckoutAddCommit('svn', 'Nav. bar test', fileName=fileName, content=content)
        self.getAssertContent(url, 'Profile', code=200)
        url += '/index.html?revision=1&view=co'
        # Check the Navigation bar has not been included in the download.
        self.getAssertNotContent(url, 'Profile', code=200)


    def urlViewvc(self, url):
        urlSplit = url.strip().split('/')
        urlSplit[2] = 'viewvc/'+urlSplit[2]+''
        return '/'.join(urlSplit)

