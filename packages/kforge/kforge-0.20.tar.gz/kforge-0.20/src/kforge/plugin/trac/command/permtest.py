import unittest
from kforge.plugin.trac.command.basetest import TracCommandTestCase
from kforge.plugin.trac.command.perm import SetTracPermissions
from kforge.plugin.trac.exceptions import TracPermissionSpecError
import os

def suite():
    suites = [
        unittest.makeSuite(TestSetTracPermissions),
    ]
    return unittest.TestSuite(suites)


class TestSetTracPermissions(TracCommandTestCase):

    def test(self):
        self.executeSpecs(['assert levin TRAC_ADMIN'])
        self.failUnlessRaises(TracPermissionSpecError, self.executeSpecs, ['assert levin'])
        self.failUnlessRaises(TracPermissionSpecError, self.executeSpecs, ['asserts levin TRAC_ADMIN'])
        self.failUnlessRaises(TracPermissionSpecError, self.executeSpecs, ['assert levin TRAC_ADMINS'])
        self.executeSpecs(['assertnot natasha TRAC_ADMIN'])
        self.executeSpecs(['grant natasha TRAC_ADMIN'])
        self.executeSpecs(['assert natasha TRAC_ADMIN'])
        self.executeSpecs(['revoke natasha TRAC_ADMIN'])
        self.executeSpecs(['assertnot natasha TRAC_ADMIN'])
        self.executeSpecs(['revoke levin *'])
        self.executeSpecs(['assertnot levin TRAC_ADMIN'])
        self.executeSpecs([
            'grant levin TRAC_ADMIN',
            'assertnot natasha TRAC_ADMIN',
            'grant natasha TRAC_ADMIN',
            'assert natasha TRAC_ADMIN',
            'revoke natasha TRAC_ADMIN',
            'assertnot natasha TRAC_ADMIN',
            'revoke levin *',
            'assertnot levin TRAC_ADMIN',
        ])

    def executeSpecs(self, specs):
        SetTracPermissions(self.tracProject, specs).execute()

