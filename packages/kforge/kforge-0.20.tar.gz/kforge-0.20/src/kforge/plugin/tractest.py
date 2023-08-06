import unittest
import kforge.plugin.trac.commandtest
from kforge.plugin.trac.basetest import TracTestCase
from kforge.plugin.trac.dictionarywords import TRAC_ADMIN_SCRIPT

def suite():
    suites = [
        kforge.plugin.trac.commandtest.suite(),
        #unittest.makeSuite(TestTrac),
    ]
    return unittest.TestSuite(suites)


class TestTrac(TracTestCase):

    def test(self):
        pass


class TestTracWrongTracAdminScript(TracTestCase):

    def setUp(self):
        self.dictionary[TRAC_ADMIN_SCRIPT] = 'foo'
        super(TestTracWrongTracAdminScript, self).setUp()

    def test(self):
        pass

