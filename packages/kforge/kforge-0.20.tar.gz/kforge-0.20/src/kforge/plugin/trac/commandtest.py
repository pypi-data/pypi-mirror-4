import unittest
import kforge.plugin.trac.command.admintest
import kforge.plugin.trac.command.permtest
import kforge.plugin.trac.command.tickettest
import kforge.plugin.trac.command.dbtest
import kforge.plugin.trac.command.preftest
import kforge.plugin.trac.command.searchtest

def suite():
    suites = [
        kforge.plugin.trac.command.admintest.suite(),
        kforge.plugin.trac.command.permtest.suite(),
        kforge.plugin.trac.command.tickettest.suite(),
        kforge.plugin.trac.command.dbtest.suite(),
        kforge.plugin.trac.command.preftest.suite(),
        kforge.plugin.trac.command.searchtest.suite(),
    ]
    return unittest.TestSuite(suites)


