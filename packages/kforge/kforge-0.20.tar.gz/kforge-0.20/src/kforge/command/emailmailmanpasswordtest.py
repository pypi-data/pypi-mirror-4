import unittest

import kforge.testunit
from kforge.command.emailmailmanpassword import EmailMailmanPassword
from kforge.exceptions import *
from kforge.dictionarywords import *

def suite():
    suites = [
        unittest.makeSuite(TestEmailMailmanPassword),
    ]
    return unittest.TestSuite(suites)


class MockEmailMailmanPassword(EmailMailmanPassword):

    def dispatchEmailMessage(self, msgFrom, msgTo, msgSubject, msgBody):
        self.dispatchedMessage = {}
        self.dispatchedMessage['from'] = msgFrom
        self.dispatchedMessage['to'] = msgTo
        self.dispatchedMessage['subject'] = msgSubject
        self.dispatchedMessage['body'] = msgBody
        self.isDispatchedOK = True


class TestEmailMailmanPassword(kforge.testunit.TestCase):

    def setUp(self):
        self.password = 'not-a-password'
        self.project = self.registry.projects['annakarenina']
        self.listName = 'not-a-list'
        self.cmd = MockEmailMailmanPassword(password=self.password, project=self.project, listName=self.listName)

    def testExecute(self):
        self.cmd.execute()
        data = self.cmd.dispatchedMessage
        self.failUnless(data['from'], data)
        self.failUnless(data['to'], data)
        self.failUnless(data['subject'], data)
        self.failUnless(data['body'], data)
        self.failUnless(self.password in data['body'], data['body'])
        self.failUnless(self.listName in data['body'], data['body'])


