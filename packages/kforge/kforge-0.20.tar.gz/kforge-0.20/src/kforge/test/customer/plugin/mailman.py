import unittest
from kforge.test.customer.plugin.base import PluginTestCase

# Tester account need sudo newlist configured for NOPASSWD.
# www-data ALL=(ALL) NOPASSWD: /usr/sbin/newlist

def suite():
    suites = [
        unittest.makeSuite(TestMailman),
    ]
    return unittest.TestSuite(suites)


class TestMailman(PluginTestCase):

    requiredPlugins = ['mailman']

    def testHttpClient(self):
        url = self.getServicePath('mailman')
        self.getAssertCode(url, 404)
        self.createService('mailman', 'mailman')
        self.getAssertCode(url, 302) # Redirect to list server.

