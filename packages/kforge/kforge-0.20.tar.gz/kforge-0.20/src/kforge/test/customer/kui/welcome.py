from kforge.test.customer.kui.base import KuiTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestVisitServer),
    ]
    return unittest.TestSuite(suites)

class TestVisitServer(KuiTestCase):
   
    def testHome(self):
        url = self.url_for('home')
        self.getAssertContent(url, 'Welcome to')
    
    def testAbout(self):
        url = self.url_for('about')
        self.getAssertContent(url, 'provisions common tools on demand')
        self.getAssertContent(url, 'single sign-on access control')

    def testUserLogin(self):
        url = self.url_for('login')
        self.getAssertContent(url, 'Log in')


