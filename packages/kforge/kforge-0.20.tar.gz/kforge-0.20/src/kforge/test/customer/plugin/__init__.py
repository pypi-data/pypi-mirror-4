import unittest

def suite():
    import kforge.test.customer.plugin.www
    import kforge.test.customer.plugin.dav
    import kforge.test.customer.plugin.mercurial
    import kforge.test.customer.plugin.git
    import kforge.test.customer.plugin.svn
    import kforge.test.customer.plugin.trac
    import kforge.test.customer.plugin.moin
    import kforge.test.customer.plugin.wordpress
    import kforge.test.customer.plugin.mailman
    import kforge.test.customer.plugin.ssh
    suites = [
        kforge.test.customer.plugin.www.suite(),
        kforge.test.customer.plugin.dav.suite(),
        kforge.test.customer.plugin.mercurial.suite(),
        kforge.test.customer.plugin.git.suite(),
        kforge.test.customer.plugin.svn.suite(),
        kforge.test.customer.plugin.trac.suite(),
        kforge.test.customer.plugin.moin.suite(),
        kforge.test.customer.plugin.wordpress.suite(),
        kforge.test.customer.plugin.mailman.suite(),
        kforge.test.customer.plugin.ssh.suite(),
    ]
    return unittest.TestSuite(suites)


