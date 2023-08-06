import unittest
from kforge.test.customer.plugin.base import PluginTestCase
from kforge.dictionarywords import *

# Tester account needs MySQL database.

def suite():
    suites = [
        unittest.makeSuite(TestWordpress),
    ]
    return unittest.TestSuite(suites)


class TestWordpress(PluginTestCase):

    requiredPlugins = ['wordpress']

    def testHttpClient(self):
        url = self.getServicePath('wordpress')
        self.getAssertCode(url, 404)
        self.createService('wordpress', 'wordpress')
        return
        # Fix this up. 
        # See http://kforge.appropriatesoftware.net/kforge/trac/ticket/103
        if self.dictionary[APACHE_PYTHON_MODULE] == 'mod_wsgi':
            self.getAssertCode(url, 401) # Cookies not accepted.
        elif self.dictionary[APACHE_PYTHON_MODULE] == 'mod_python':
            self.getAssertCode(url, 500) # Todo: Fix Wordpress database configuration (not implemented).
        self.logoutPerson()
        self.getAssertCode(url, 401)
        self.setBasicAuthPerson()
        # Todo: Configure Wordpress database.
        self.getAssertCode(url, 500)
        return
        content = "Database Error"
        self.getAssertContent(url, content, code=500)
        #content = "WordPress"
        #self.getAssertContent(url, content)
        #self.logoutPerson()
        #self.getAssertCode(url, 401)

