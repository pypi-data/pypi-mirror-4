from kforge.plugin.trac.command.basetest import TracCommandTestCase
from kforge.plugin.trac.command.config import SetTracConfigOptions
from kforge.plugin.trac.command.admin import GetTracConfig

def suite():
    suites = [
        unittest.makeSuite(TestSetTracConfigOptions),
    ]
    return unittest.TestSuite(suites)

class TestSetTracConfigOptions(self):

    def test(self):
        get = GetTracConfig(self.tracProject, 'trac', 'timeout')
        self.failUnlessEqual(get.execute(), '20')
        SetTracConfigOptions(self.tracProject, [('trac', 'timeout', '30')]).execute()
        self.failUnlessEqual(get.execute(), '30')
        SetTracConfigOptions(self.tracProject, [('trac', 'timeout', None)]).execute()
        self.failUnlessEqual(get.execute(), '20')


