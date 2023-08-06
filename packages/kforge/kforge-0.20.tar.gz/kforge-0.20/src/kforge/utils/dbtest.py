import unittest

from kforge.utils.db import Database

def suite():
    suites = [
        unittest.makeSuite(DatabaseTest),
        ]
    return unittest.TestSuite(suites)

class DatabaseTest(unittest.TestCase):
    """
    WARNING: once we run any command that creates a db connection
    (i.e. uses kforge.soleInstance.application e.g. init() or rebuild())
    any following stuff will break because you can't delete/create db
    
    This is why test_rebuild is commented out.
    test_init() runs last so it works
    """
    tags = [ 'cli' ]
    disable = True

    def setUp(self):
        self.db = Database()
        try:
            self.db.delete()
        except Exception, inst:
            # print 'Failed to delete: %s' % inst
            pass
        self.db.create()

    def test_delete(self):
        self.db.delete()
        # verify deletion?

    def test_init(self):
        self.db.init()
        # do a crude check that this has run
        import kforge
        app = kforge.getA()
        admin = app.registry.people['admin']

#    def test_rebuild(self):
#        self.db.rebuild()

if __name__ == '__main__':
    unittest.main()
