import unittest
from kforge.dom.testunit import TestCase
import kforge.dom.person
from kforge.exceptions import *

def suite():
    suites = [
        unittest.makeSuite(TestPerson),
    ]
    return unittest.TestSuite(suites)


class TestPerson(TestCase):
    "TestCase for the Person class."
    
    def setUp(self):
        super(TestPerson, self).setUp()
        self.fixtureName = 'TestPerson'
        try:
            self.people = self.registry.people
            self.person = self.people.create(self.fixtureName)
        except:
            person = self.people.getAll()[self.fixtureName]
            person.delete()
            person.purge()

    def tearDown(self):
        try:
            person = self.people.getAll()[self.fixtureName]
            person.delete()
            person.purge()
        except:
            pass
        self.person = None
   
    def test_new(self):
        self.failUnless(self.person, "New person could not be created.")
        self.assertEquals(self.person.state, self.activeState,
            "Not in active state after create."
        )
        self.failUnless(self.person.role,
            "No role for new person."
        )
        self.failUnlessRaises(KforgeDomError,
            self.registry.people.create, self.fixtureName
        )
        self.failUnlessEqual(self.person.getUri('/x'), '/x/people/TestPerson')

    def test_find(self):
        self.failUnless(self.registry.people['TestPerson'],
            "New person could not be found."
        )
        self.failUnlessRaises(KforgeRegistryKeyError,
            self.registry.people.__getitem__, 'TestAlien'
        )

    def test_delete(self):
        self.assertEquals(self.person.state, self.activeState,
            "Not in active state to start with: " + self.person.state.name
        )
        self.person.delete()
        self.assertEquals(self.person.state, self.deletedState,
            "Not deleted after deleting active object: "+self.person.state.name
        )
        self.person.undelete()
        self.assertEquals(self.person.state, self.activeState,
            "Not active state: %s" % self.person.state
        )
        self.person.delete()
        self.assertEquals(self.person.state, self.deletedState,
            "Not deleted state: %s" % self.person.state
        )

    def test_purge(self):
        self.failUnless(self.registry.people['TestPerson'],
            "Purged active person could not be found."
        )
        self.person.delete()
        self.assertEquals(self.person.state, self.deletedState,
            "Not deleted after deleting active object: %s" % self.person.state
        )
        self.person.purge()
        self.failUnlessRaises(KforgeRegistryKeyError,
            self.registry.people.__getitem__, self.fixtureName
        )

    def test___delitem__(self):
        del self.people[self.fixtureName]
        self.failUnlessRaises(KforgeRegistryKeyError,
            self.registry.people.__getitem__, self.fixtureName
        )

    def test_is(self):
        self.failUnless(self.people.has_key(self.fixtureName),
            "New person doesn't appear to be there."
        )
        self.failIf(self.people.has_key('TestAlien'),
            "Strange person does appear to be there."
        )
        self.failUnless(self.person.state,
            "No state assigned."
        )
        self.assertEquals(self.person.state.name, 'active',
            "Not active state: %s" % self.person.state
        )
        self.person.delete()
        self.person.purge()
        self.failIf(self.people.has_key(self.fixtureName),
            "New person still appears to be there."
        )

    def test_save(self):
        self.assertEquals(self.person.fullname, "", "Already has a fullname.")
        self.person.fullname = "Test Person"
        self.assertEquals(self.person.fullname, "Test Person",
            "Person doesn't have attribute."
        )
        self.person.save()
        person = self.people[self.fixtureName]
        self.assertEquals(person.fullname, "Test Person",
            "Retrieved person has wrong fullname."
        )
        person.fullname = "Other Person"
        self.assertEquals(self.person.fullname, "Other Person",
            "Suspect duplicate domain objects!!"
        )
        
    def test_count(self):
        self.failUnless(self.people.count(), "Problem with person count.")

    def test_keys(self):
        self.failUnless(self.people.keys(), "Problem with person list.")

    def test_iter(self):
        self.failUnless(self.people.__iter__(), "Problem with person iter.")
        for p in self.people:
            self.failUnless(p.name, "Problem with person from iterator.")
