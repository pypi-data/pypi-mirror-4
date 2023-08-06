import unittest
from kforge.testunit import TestCase
from kforge.command.member import *
from kforge.exceptions import *

def suite():
    suites = [
        unittest.makeSuite(TestMemberCreate),
    #    unittest.makeSuite(TestMemberDelete),
    ]
    return unittest.TestSuite(suites)

class MemberTestCase(TestCase):

    fixtureName = 'MemberTestCase'

    def setUp(self):
        super(MemberTestCase, self).setUp()
        self.member = None
        self.person  = self.registry.people['levin']
        self.project = self.registry.projects['warandpeace']
        if self.person in self.project.members:
            member = self.project.members[self.person]
            member.delete()
            member.purge()
        self.failUnless(self.person)
        self.failUnless(self.project)
        self.command = self.buildCommand()

    def tearDown(self):
        if self.command and self.command.member:
            self.command.member.delete()
            self.command.member.purge()
        elif self.member:
            self.member.delete()
            self.member.purge()


class TestMemberCreate(MemberTestCase):
    "TestCase for the MemberCreate command."

    fixtureName = 'TestMemberCreate'

    def buildCommand(self):
        return MemberCreate(
            person=self.person,
            project=self.project,
        )
        
    def testExecute(self):
        self.command.execute()
        self.failUnless(self.command.member, "No member on command.")
        self.member = self.command.member
        self.failUnless(self.member.person, "No person on member.")
        self.failUnless(self.member.project, "No project on member.")
        self.failUnless(self.project in self.person.memberships)
        self.failUnless(self.person in self.project.members)
            
    def testErrorMemberAlreadyExists(self):
        self.command.execute()
        # Suspended isUnique=True.
        #self.failUnlessRaises(KforgeCommandError, self.command.execute)
        
    def testErrorNoPerson(self):
        self.command = MemberCreate(
            project=self.project,
        )   
        self.failUnlessRaises(KforgeCommandError, self.command.execute)
                
    def testErrorNoProject(self):
        self.command = MemberCreate(
            person=self.person,
        )   
        self.failUnlessRaises(KforgeCommandError, self.command.execute)


#class TestMemberDelete(MemberTestCase):
#    "TestCase for the MemberDelete command."
#
#    fixtureName = 'TestMemberDelete'
#    
#    def setUp(self):
#        super(TestMemberDelete, self).setUp()
#        self.command.execute()
#
#    def tearDown(self):
#        self.command = None
#        try:
#            if self.member:
#                self.member.delete()
#                self.member.purge()
#        finally:
#            try:
#                self.person.delete()
#                self.person.purge()
#            finally:
#                self.project.delete()
#                self.project.purge()
#
#    def testExecute(self):
#        self.failUnless(self.person in self.project.members)
#        self.command.execute()
#        self.failIf(self.person in self.project.members)
#
#    def testNoMember(self):
#        self.command.execute()
#        self.failUnlessRaises(KforgeCommandError, self.command.execute)
#
