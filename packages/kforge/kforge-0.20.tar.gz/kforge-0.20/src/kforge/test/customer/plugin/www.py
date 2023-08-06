import unittest
from kforge.test.customer.plugin.base import PluginTestCase

def suite():
    suites = [
        unittest.makeSuite(TestWww),
    ]
    return unittest.TestSuite(suites)


class TestWww(PluginTestCase):

    requiredPlugins = ['www']
    
    def testHttpClient(self):
        self.createService('www', 'www')
        self.logoutPerson()
        url = self.urlSiteHome + '%s/www' % self.kuiProjectName
        content = 'Index of /%s/www' % self.kuiProjectName
        self.getAssertCode(url, code=301) # Redirect to '.../'
        url += '/'
        self.getAssertContent(url, content, code=200)
