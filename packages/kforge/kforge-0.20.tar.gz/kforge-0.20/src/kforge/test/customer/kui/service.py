from kforge.test.customer.kui.base import KuiTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestServiceCRUD),
    ]
    return unittest.TestSuite(suites)


class TestServiceCRUD(KuiTestCase):

    def setUp(self):
        super(TestServiceCRUD, self).setUp()
        self.registerPerson()
        self.loginPerson()
        self.registerProject()

    def test_project_services(self):
        self.getAssertContent(self.urlProjectServices, 'Services')
        self.getAssertContent(self.urlProjectServiceCreate, 'Add new service')

