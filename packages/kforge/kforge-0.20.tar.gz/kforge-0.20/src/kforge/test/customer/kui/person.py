from kforge.test.customer.kui.base import KuiTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestPersonRegister),
        unittest.makeSuite(TestPersonEntity),
    ]
    return unittest.TestSuite(suites)


class TestPersonRegister(KuiTestCase):

    kuiPersonName = 'admin'
   
    def testRegister(self):
        # Index page.
        content = 'There are %s people' % self.registry.people.count()
        self.getAssertContent(self.urlPersons, content)

        # Search page.
        params = {'userQuery': 'z'}
        url = self.urlPersonSearch
        self.postAssertNotContent(url, params, self.kuiPersonName)
        params = {'userQuery': 'a'}
        self.postAssertContent(url, params, self.kuiPersonName)
    
        # Find page.
        url = self.url_for('people', action='find', id='z')
        self.getAssertNotContent(url, self.kuiPersonName)
        url = self.url_for('people', action='find', id='a')
        self.getAssertContent(url, self.kuiPersonName)


class TestPersonEntity(KuiTestCase):

    def testEntity(self):
        # Make sure not logged in.
        self.getAssertNotContent(self.urlSiteHome, "Log out")

        # Make sure login fails.
        params = {}
        params['name'] = self.kuiPersonName
        params['password'] = self.kuiPersonPassword
        self.postAssertContent(self.urlLogin, params, "Sorry, wrong user name or password.")

        # Create.
        content = 'Please register user details below'
        page = self.getAssertContent(self.urlPersonCreate, content)
        self.registerPerson()

        # Read.
        content = self.kuiPersonFullname
        self.getAssertContent(self.urlPersonRead, content)

        self.loginPerson()
        self.urlSiteHome = self.url_for('home')
        self.getAssertContent(self.urlSiteHome, 'Log out')
        self.getAssertContent(self.urlPersonUpdate, self.kuiPersonEmail)

        # Update.
        self.getAssertContent(self.urlPersonUpdate, self.kuiPersonFullname + '&#x2019;s settings')
        self.getAssertContent(self.urlPersonUpdate, self.kuiPersonName)
        self.getAssertContent(self.urlPersonUpdate, self.kuiPersonFullname)
        params = {}
        params['submission'] = '1'
        params['password'] = ''
        params['passwordconfirmation'] = ''
        kuiFullnameCorrection = 'newCorrectFullname'
        params['fullname'] = kuiFullnameCorrection
        params['email'] = self.kuiPersonEmail
        self.postAssertCode(self.urlPersonUpdate, params)

        self.getAssertContent(self.urlPersonRead, self.kuiPersonName)
        self.getAssertContent(self.urlPersonRead, kuiFullnameCorrection)
        
        # Recovery.
        self.logoutPerson()
        # - check link to recovery page
        self.getAssertContent(self.urlLogin, 'Forgotten your password?')
        self.getAssertContent(self.urlLogin, self.urlPersonRecover)
        # - check title of recovery page
        self.getAssertContent(self.urlPersonRecover, 'Identify your account')
        # - check recovery form submission
        params = {}
        #   - blank submission
        self.postAssertContent(self.urlPersonRecover, params, 'Identify your account')
        #   - unregistered username
        params = {'name': 'unregistered' + self.kuiPersonName}
        self.postAssertContent(self.urlPersonRecover, params, 'unregistered' + self.kuiPersonName)
        self.postAssertContent(self.urlPersonRecover, params, "Sorry, we couldn't find your account with those details.")
        #   - registered username
        params = {'name': self.kuiPersonName}
        self.postAssertContent(self.urlPersonRecover, params, 'A new password has been sent. Please check your email account.')
        #   - unregistered email
        params = {'email': 'unregistered' + self.kuiPersonEmail}
        self.postAssertContent(self.urlPersonRecover, params, "Sorry, we couldn't find your account with those details.")
        #   - registered email
        params = {'email': self.kuiPersonEmail}
        self.postAssertContent(self.urlPersonRecover, params, 'A new password has been sent. Please check your email account.')

        # Delete.
        self.loginPerson()
        self.getAssertContent(self.urlSiteHome, 'Log out')
        page = self.getAssertCode(self.urlPersonRead, code=200)
        self.deletePerson()
        page = self.getAssertCode(self.urlPersonRead, code=404)

        self.getAssertNotContent(self.urlSiteHome, 'Log out')
        
