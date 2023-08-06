import unittest
from kforge.plugin.trac.command.basetest import TracCommandTestCase
from kforge.plugin.trac.command.db import TracDbCommand
import os

def suite():
    suites = [
        unittest.makeSuite(TestTracDbCommand),
    ]
    return unittest.TestSuite(suites)


class TestTracDbCommand(TracCommandTestCase):

    def test(self):
        self.failUnlessRaises(Exception, TracDbCommand, None)
        cmd = TracDbCommand(self.tracProject)
        self.failUnlessEqual(cmd.tracProject, self.tracProject)
        self.failUnless(cmd.envPath)
        self.failUnlessEqual(cmd.envPath, cmd.tracProject.service.getDirPath())
        self.failUnless(os.path.exists(cmd.envPath))
        self.failIf(cmd.env)
        from trac.env import Environment
        self.failUnless(cmd.getEnvClass())
        self.failUnlessEqual(cmd.getEnvClass(), Environment)
        self.failUnless(cmd.getEnv())
        self.failUnlessEqual(type(cmd.getEnv()), Environment)
        self.failUnless(cmd.env)
        self.failUnlessEqual(cmd.env, cmd.getEnv())
        cmd.resetEnvPath('/foo')
        self.failUnlessEqual(cmd.envPath, '/foo')
        self.failIf(cmd.env)


