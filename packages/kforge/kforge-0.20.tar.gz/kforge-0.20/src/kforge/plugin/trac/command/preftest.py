import unittest
from kforge.plugin.trac.command.basetest import TracCommandTestCase
from kforge.plugin.trac.command.pref import InsertTracSessions
from kforge.plugin.trac.command.pref import SelectTracSessions
from kforge.plugin.trac.command.pref import AddTracSessions
from kforge.plugin.trac.command.pref import SetTracPreferences
from kforge.plugin.trac.command.pref import GetTracPreferences

def suite():
    suites = [
        unittest.makeSuite(TestInsertTracSessions),
        unittest.makeSuite(TestSelectTracSessions),
        unittest.makeSuite(TestAddTracSessions),
        unittest.makeSuite(TestSetTracPreferences),
    ]
    return unittest.TestSuite(suites)


class TestInsertTracSessions(TracCommandTestCase):

    def test(self):
        names = ['name%s' % i for i in range(10)]
        InsertTracSessions(self.tracProject, names).execute()


class TestSelectTracSessions(TracCommandTestCase):

    def setUp(self):
        super(TestSelectTracSessions, self).setUp()
        self.names = ['name%s' % i for i in range(10)]
        InsertTracSessions(self.tracProject, self.names).execute()

    def test(self):
        names = SelectTracSessions(self.tracProject).execute()
        expectNames = self.names + ['admin', 'levin', 'natasha', 'visitor']
        for name in self.names:
            self.failUnless(name in names, 
                "Name '%s' not selected: %s. \
                Inserted names are: %s." % (name, names, self.names)
            )


class TestAddTracSessions(TracCommandTestCase):

    def test(self):
        names = SelectTracSessions(self.tracProject).execute()
        len1 = len(names) # levin, natasha, etc.
        # Put 2 names.
        names = ['name%s' % i for i in range(2)]
        AddTracSessions(self.tracProject, names).execute()
        names = SelectTracSessions(self.tracProject).execute()
        self.failUnlessEqual(len(names) - len1, 2)
        # Put 4 names (only 2 are new).
        names = ['name%s' % i for i in range(4)]
        AddTracSessions(self.tracProject, names).execute()
        names = SelectTracSessions(self.tracProject).execute()
        self.failUnlessEqual(len(names) - len1, 4)
        # Put 4000 names (only 3996 are new).
        names = ['name%s' % i for i in range(4000)]
        AddTracSessions(self.tracProject, names).execute()
        names = SelectTracSessions(self.tracProject).execute()
        self.failUnlessEqual(len(names) - len1, 4000)


class TestSetTracPreferences(TracCommandTestCase):

    def test(self):
        username = 'name0'
        get = GetTracPreferences(self.tracProject, username)
        self.failUnlessEqual(get.execute(), (username, None, None))

        fullname = 'My Name'
        email = '%s@email' % username
        preferences = (username, fullname, email)
        SetTracPreferences(self.tracProject, [preferences]).execute()
        get = GetTracPreferences(self.tracProject, username)
        self.failUnlessEqual(get.execute(), preferences)

        # Update current values.
        fullname = 'My Real Name'
        email = '%s+label@email' % username
        preferences = (username, fullname, email)
        SetTracPreferences(self.tracProject, [preferences]).execute()
        get = GetTracPreferences(self.tracProject, username)
        self.failUnlessEqual(get.execute(), preferences)

        # Try with lots of people.
        usernames = ['name%s' % i for i in range(4000)]
        preferences = []
        for username in usernames:
            fullname = 'My %s' % username.capitalize()
            email = '%s+label@email' % username
            preferences.append((username, fullname, email))

        SetTracPreferences(self.tracProject, preferences).execute()
        for i in range(1000, 1005):
            get = GetTracPreferences(self.tracProject, usernames[i])
            self.failUnlessEqual(get.execute(), preferences[i])


