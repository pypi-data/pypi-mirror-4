from kforge.test.customer.kui.admin.domainObject import AdminTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestHasManyAttribute),
    ]
    return unittest.TestSuite(suites)


class TestHasManyAttribute(AdminTestCase):

    def testMemberList(self):
        url = self.url_for('admin', offset='Project/administration/members/')
        self.checkPage(url, 'admin')

    def testMemberCreate(self):
        url = self.url_for('admin', offset='create/Project/administration/members/')
        self.checkPage(url, 'Create Member')

    def testMemberRead(self):
        url = self.url_for('admin', offset='Project/administration/members/admin/')
        self.checkPage(url, 'admin')

    def testMemberUpdate(self):
        url = self.url_for('admin', offset='update/Project/administration/members/admin/')
        self.checkPage(url, 'Update Member')

    def testMemberDelete(self):
        url = self.url_for('admin', offset='delete/Project/administration/members/admin/')
        self.checkPage(url, 'Delete Member')

