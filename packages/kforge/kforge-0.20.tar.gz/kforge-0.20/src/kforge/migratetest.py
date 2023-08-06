import unittest
from kforge.testunit import TestCase
from kforge.dictionarywords import *

def suite():
    suites = [
        unittest.makeSuite(MigrationTest),
    ]
    return unittest.TestSuite(suites)

class MigrationTest(TestCase):

    def test_registry(self):
        # Check system version in the model equals system version in the code.
        systemVersion = self.registry.systems[1].version
        self.failUnlessEqual(systemVersion, self.dictionary[SYSTEM_VERSION])

        # Check everybody can delete their memberships.
        for person in self.registry.people:
            for membership in person.memberships:
                ac = self.accessController
                canAccess = ac.isAccessAuthorised(
                    person=person,
                    actionName='Delete',
                    protectedObject=membership,
                )
                if person.name == 'visitor':
                    msg = "Person '%s' can leave project '%s'." % (
                        person.name, membership.project.name)
                    self.failIf(canAccess, msg)
                else:
                    msg = "Person '%s' can't leave project '%s'." % (
                        person.name, membership.project.name)
                    self.failUnless(canAccess, msg)
            
        # Check everybody still has an email address.
        adminRole = self.registry.roles['Administrator']
        admins = self.registry.people.findDomainObjects(role=adminRole)
        self.failUnless(len(admins))
        for person in admins:
            self.failUnless(person.getEmailAddress())                 

        # Check everybody can read and delete their registered email addresses.
        for person in self.registry.people:
            if person.name == 'visitor':
                continue
            for emailAddress in person.emailAddresses:
                ac = self.accessController
                canAccess = ac.isAccessAuthorised(
                    person=person,
                    actionName='Read',
                    protectedObject=emailAddress,
                )
                msg = "Person '%s' can't read email address '%s'." % (
                    person.name, emailAddress)
                self.failUnless(canAccess, msg)
                canAccess = ac.isAccessAuthorised(
                    person=person,
                    actionName='Delete',
                    protectedObject=emailAddress,
                )
                msg = "Person '%s' can't delete email address '%s'." % (
                    person.name, emailAddress)
                self.failUnless(canAccess, msg)

