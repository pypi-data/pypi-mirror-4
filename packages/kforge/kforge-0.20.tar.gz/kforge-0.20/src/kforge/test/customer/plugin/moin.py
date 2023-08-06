import unittest
from kforge.test.customer.plugin.base import PluginTestCase

# Tester account needs MySQL database.

def suite():
    suites = [
        unittest.makeSuite(TestMoin),
    ]
    return unittest.TestSuite(suites)


class TestMoin(PluginTestCase):

    requiredPlugins = ['moin']

    def testHttpClient(self):
        url = self.getServicePath('moin')
        self.getAssertCode(url, 404)
        self.createService('moin', 'moin')
        content = "This site uses the MoinMoin Wiki software."
        self.getAssertContent(url, content)
        self.logoutPerson()
        self.getAssertCode(url, 401)
        self.setBasicAuthPerson()
        self.getAssertContent(url, content)
        self.logoutPerson()
        self.getAssertCode(url, 401)

