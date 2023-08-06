import unittest

# Todo: Figure out why "Exception: Domain class 'TracProject' is not defined."
# is raised when plugintest suite is run at the end. Hence it runs first....

def suite():
    import kforge.testunit
    import kforge.unittesttest
    import kforge.domtest
    import kforge.utilstest
    import kforge.dictionarytest
    import kforge.apachetest
    import kforge.accesscontroltest
    import kforge.commandtest
    import kforge.urltest
    import kforge.django.apps.kui.views.test
    import kforge.applicationtest
    import kforge.handlerstest
    import kforge.plugintest
    suites = [
        kforge.plugintest.suite(),
        kforge.unittesttest.suite(),
        kforge.domtest.suite(),
        kforge.utilstest.suite(),
        kforge.dictionarytest.suite(),
        kforge.apachetest.suite(),
        kforge.accesscontroltest.suite(),
        kforge.commandtest.suite(),
        kforge.urltest.suite(),
        kforge.django.apps.kui.views.test.suite(),
        kforge.applicationtest.suite(),
        kforge.handlerstest.suite(),
    ]
    return unittest.TestSuite(suites)

