from kforge.test.customer.kui.base import KuiTestCase
import unittest
import time
from kforge.dictionarywords import APACHE_PYTHON_MODULE

def suite():
    suites = [
        unittest.makeSuite(TestAdminIndex),
        unittest.makeSuite(TestListObject),
        unittest.makeSuite(TestCreateObject),
        unittest.makeSuite(TestReadObject),
        unittest.makeSuite(TestUpdateObject),
        unittest.makeSuite(TestDeleteObject),
    ]
    return unittest.TestSuite(suites)


class AdminTestCase(KuiTestCase):

    fixtureKeyName  = 'testObject'
    fixtureFullname = 'Test Object'
    fixtureType     = 'Person'
    fixtureEmail    = 'test@test.com'

    personRegister = KuiTestCase.registry.people
    
    def setUp(self):
        super(AdminTestCase, self).setUp()
        # Create a new administrator account.
        self.registerPerson()
        self.visitor = self.personRegister[self.kuiPersonName]
        adminRole = self.registry.roles['Administrator']
        self.visitor.role = adminRole
        self.visitor.save()
        time.sleep(0.2)
        # Login new administrator account.
        self.loginPerson()
        # Prepare URLs.
        self.urlAdminModel = self.url_for('admin', model='model', offset='')
        self.urlAdminPersons = self.url_for('admin', offset='Person')
        self.urlAdminPersonCreate = self.url_for('admin', offset='create/Person/')
        offset = 'Person/%s/' % self.fixtureKeyName
        self.urlAdminPerson = self.url_for('admin', offset=offset)
        offset = 'update/Person/%s/' % self.fixtureKeyName
        self.urlAdminPersonUpdate = self.url_for('admin', offset=offset)
        offset = 'delete/Person/%s/' % self.fixtureKeyName
        self.urlAdminPersonDelete = self.url_for('admin', offset=offset)

    def tearDown(self):
        super(AdminTestCase, self).tearDown()
        register = self.personRegister.getAll()
        while self.fixtureKeyName in register:
            person = register[self.fixtureKeyName]
            person.delete()
            person.purge()


class TestAdminIndex(AdminTestCase):

    def testModel(self):
        self.checkPage(self.urlAdminModel, 'Domain Model Registry')
        #if self.dictionary[APACHE_PYTHON_MODULE] == 'mod_python':
        #    time.sleep(0.1)  # Seems to help avoid getting redirected.
        self.checkPage(self.urlAdminModel, 'Person')


class TestListObject(AdminTestCase):

    def testListObject(self):
        self.getAssertContent(self.urlAdminPersons, 'Person')
        self.getAssertContent(self.urlAdminPersons, 'admin')
        self.getAssertContent(self.urlAdminPersons, 'visitor')
        self.getAssertContent(self.urlAdminPersons, self.kuiPersonName)
        

class TestCreateObject(AdminTestCase):

    fixtureKeyName  = 'testCreateObject'
    
    def testCreateObject(self):
        self.failIf(self.fixtureKeyName in self.personRegister.getAll())
        self.getAssertContent(self.urlAdminPersons, 'Create Person', code=200)
        self.getAssertNotContent(self.urlAdminPersons, self.fixtureKeyName)
        self.getAssertContent(self.urlAdminPersonCreate, 'Create Person')
        params = {}
        params['name']     = self.fixtureKeyName
        params['fullname'] = self.fixtureFullname
        params['password'] = self.fixtureKeyName
        params['email']    = self.fixtureEmail
        content = "Role is required."
        self.postAssertContent(self.urlAdminPersonCreate, params, content, code=400)
        params['role']     = '/roles/Administrator'
        self.postAssertCode(self.urlAdminPersonCreate, params, code=302)
        self.getAssertContent(self.urlAdminPersons, self.fixtureFullname)
 

class TestReadObject(AdminTestCase):

    def testReadObject(self):
        person = self.personRegister.create(self.fixtureKeyName, fullname=self.fixtureFullname)
        self.getAssertContent(self.urlAdminPerson, self.fixtureFullname)
        self.getAssertContent(self.urlAdminPerson, self.fixtureKeyName)
        

class TestUpdateObject(AdminTestCase):

    fixtureFullnameUpdated = 'Fullname Update Test'

    def testUpdateObject(self):
        person = self.personRegister.create(
            name     = self.fixtureKeyName,
            fullname = self.fixtureFullname,
            role     = self.registry.roles['Visitor'],
        )
        person.email = self.fixtureEmail
        self.checkPage(self.urlAdminPersonUpdate, self.fixtureKeyName, code=200)
        self.checkPage(self.urlAdminPersonUpdate, self.fixtureFullname, code=200)
        self.getAssertNotContent(self.urlAdminPersonUpdate, self.fixtureFullnameUpdated)

        self.getAssertContent(self.urlAdminPersonUpdate, self.fixtureKeyName, code=200)
        self.getAssertContent(self.urlAdminPersonUpdate, self.fixtureFullname, code=200)
        self.getAssertNotContent(self.urlAdminPersonUpdate, self.fixtureFullnameUpdated, code=200)

        self.getAssertContent(self.urlAdminPersonUpdate, 'Update Person', code=200)
        self.getAssertContent(self.urlAdminPersonUpdate, self.fixtureKeyName, code=200)
        params = {}
        params['name']     = self.fixtureKeyName
        params['fullname'] = self.fixtureFullnameUpdated
        params['email']    = self.fixtureEmail
        content = "Role is required."
        self.postAssertContent(self.urlAdminPersonUpdate, params, content, code=400)
        params['role']     = '/roles/Administrator'
        self.postAssertCode(self.urlAdminPersonUpdate, params, code=302)
        self.getAssertContent(self.urlAdminPersonUpdate, self.fixtureFullnameUpdated, code=200)
        

class TestDeleteObject(AdminTestCase):

    def testDeleteObject(self):
        self.getAssertCode(self.urlAdminPerson, code=404)
        person = self.personRegister.create(self.fixtureKeyName, fullname=self.fixtureFullname)
        self.checkPage(self.urlAdminPerson, 'Delete Person')
        self.checkPage(self.urlAdminPersonDelete, 'Delete Person')
        self.checkPage(self.urlAdminPersonDelete, self.fixtureKeyName)
        params = {'Submit': 'Delete Person'}
        self.postAssertCode(self.urlAdminPersonDelete, params, code=302)
        if self.dictionary[APACHE_PYTHON_MODULE] == 'mod_python':
            time.sleep(0.1)  # Seems to help avoid getting 200.
        self.getAssertCode(self.urlAdminPerson, code=404)

