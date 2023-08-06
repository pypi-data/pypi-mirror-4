import unittest
from kforge.exceptions import *
from kforge.dom.testunit import TestCase

def suite():
    suites = [
        unittest.makeSuite(TestMember),
        unittest.makeSuite(TestPendingMember),
    ]
    return unittest.TestSuite(suites)

class TestMember(TestCase):
    "TestCase for the Member class."
    
    def setUp(self):
        super(TestMember, self).setUp()
        self.person = self.registry.people.create('TestPendingMemberPerson')
        self.project = self.registry.projects.create('TestPendingMemberProject')
        try:
            self.member = self.project.members.create(self.person)
        except:
            self.project.delete()
            self.project.purge()
            self.person.delete()
            self.person.purge()
            raise

    def tearDown(self):
        self.project.delete()
        self.project.purge()
        self.person.delete()
        self.person.purge()

    def test(self):    
        # Check state is active.
        self.failUnless(self.member.isActive())
        # Check member URI.
        self.failUnlessEqual(self.member.getUri('/x'), '/x/projects/TestPendingMemberProject/members/TestPendingMemberPerson')
        # Check member in all and active lists.
        self.failUnless(self.person in self.project.members.all)
        self.failUnless(self.person in self.project.members)
        # Check member not in pending or deleted lists.
        self.failIf(self.person in self.project.members.deleted)
        self.failIf(self.person in self.project.members.pending)
        # Check delete.
        self.member.delete()
        # Check member in all and deleted lists.
        listAll = list(self.project.members.all)
        self.failUnless(self.person in self.project.members.all, listAll)
        self.failUnless(self.person in self.project.members.deleted, listAll)
        # Check member not in active or pending lists.
        self.failIf(self.person in self.project.members, listAll)
        self.failIf(self.person in self.project.members.pending, listAll)


class TestPendingMember(TestCase):
    "TestCase for the PendingMember class."
    
    def setUp(self):
        super(TestPendingMember, self).setUp()
        self.person = self.registry.people.create('TestPendingMemberPerson')
        self.project = self.registry.projects.create('TestPendingMemberProject')
        try:
            self.member = self.project.members.pending.create(self.person)
        except:
            self.project.delete()
            self.project.purge()
            self.person.delete()
            self.person.purge()
            raise

    def tearDown(self):
        self.project.delete()
        self.project.purge()
        self.person.delete()
        self.person.purge()
    
    def test(self):
        self.failUnless(self.member, "New member could not be created.")
        # Check state is pending.
        self.failUnless(self.member.isPending())
        # Check member URI.
        self.failUnlessEqual(self.member.getUri('/x'), '/x/projects/TestPendingMemberProject/members/pending/TestPendingMemberPerson')
        # Check member in all and pending lists.
        self.failUnless(self.person in self.project.members.all)
        self.failUnless(self.person in self.project.members.pending)
        # Check member not in active or deleted lists.
        self.failIf(self.person in self.project.members)
        self.failIf(self.person in self.project.members.deleted)
        # Check delete.
        self.member.delete()
        # Check member in all and deleted lists.
        self.failUnless(self.person in self.project.members.all)
        self.failUnless(self.person in self.project.members.deleted)
        # Check member not in active or pending lists.
        self.failIf(self.person in self.project.members)
        self.failIf(self.person in self.project.members.pending, list(self.project.members.all))


