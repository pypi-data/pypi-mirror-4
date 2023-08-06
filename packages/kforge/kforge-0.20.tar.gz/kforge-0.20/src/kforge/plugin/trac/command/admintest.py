import unittest
from kforge.plugin.trac.command.basetest import TracCommandTestCase
from kforge.plugin.trac.command.admin import InitialiseTracEnvironment
from kforge.plugin.trac.command.admin import UpgradeTracEnvironment
from kforge.plugin.trac.command.admin import GetTracConfig
from kforge.plugin.trac.command.perm import SetTracPermissions
import os

def suite():
    suites = [
        unittest.makeSuite(TestInitialiseTracEnvironment),
        unittest.makeSuite(TestUpgradeTracEnvironment),
    ]
    return unittest.TestSuite(suites)


class TestInitialiseTracEnvironment(TracCommandTestCase):

    def test(self):
        # InitialiseTracEnvironment is executed in setUp().
        self.failUnless(os.path.exists(self.service.getDirPath()))
        self.failUnless(self.tracProject.isEnvironmentInitialised)
        # Assert permissions.
        cmd = SetTracPermissions(self.tracProject,
            ['assert levin TRAC_ADMIN'])
        cmd.execute()


class TestUpgradeTracEnvironment(TracCommandTestCase):

    def test(self):
        # InitialiseTracEnvironment is executed in setUp().
        UpgradeTracEnvironment(self.tracProject).execute()


class TestGetTracConfig(TracCommandTestCase):

    def test(self):
        get = GetTracConfig(self.tracProject, 'browser',
            'render_unsafe_content')
        self.failUnlessEqual(get.execute(), 'false')

