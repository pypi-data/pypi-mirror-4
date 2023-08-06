from webunit import webunittest
import unittest

# Todo: Test access control for hidden projects. Viewer shouldn't be able to
# see other's memberships of hidden projects, unless also a member. Shouldn't
# be able to see hidden projects in list, index (startswith), and search
# unless a member. 

def suite():
    import kforge.test.customer.kui.welcome
    import kforge.test.customer.kui.admin
    import kforge.test.customer.kui.person
    import kforge.test.customer.kui.project
    import kforge.test.customer.kui.member
    import kforge.test.customer.kui.service
    import kforge.test.customer.kui.api
    suites = [
        kforge.test.customer.kui.welcome.suite(),
        kforge.test.customer.kui.admin.suite(),
        kforge.test.customer.kui.person.suite(),
        kforge.test.customer.kui.project.suite(),
        kforge.test.customer.kui.member.suite(),
        kforge.test.customer.kui.service.suite(),
        kforge.test.customer.kui.api.suite(),
    ]
    return unittest.TestSuite(suites)

