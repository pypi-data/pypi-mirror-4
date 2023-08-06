import unittest

import kforge.testunit
from kforge.command.emailjoinrequest import EmailJoinRequest
from kforge.command.emailjoinrequest import EmailJoinApprove
from kforge.command.emailjoinrequest import EmailJoinReject
from kforge.exceptions import *
from kforge.dictionarywords import *

def suite():
    suites = [
        unittest.makeSuite(TestEmailJoinRequest),
        unittest.makeSuite(TestEmailJoinApprove),
        unittest.makeSuite(TestEmailJoinReject),
    ]
    return unittest.TestSuite(suites)


class MockEmailJoinRequest(EmailJoinRequest):

    def dispatchEmailMessage(self, msgFrom, msgTo, msgSubject, msgBody):
        self.dispatchedMessage = {}
        self.dispatchedMessage['from'] = msgFrom
        self.dispatchedMessage['to'] = msgTo
        self.dispatchedMessage['subject'] = msgSubject
        self.dispatchedMessage['body'] = msgBody
        self.isDispatchedOK = True


class TestEmailJoinRequest(kforge.testunit.TestCase):

    def setUp(self):
        self.person = self.registry.people['levin']
        self.project = self.registry.projects['warandpeace']
        self.cmd = MockEmailJoinRequest(self.project, self.person)

    def tearDown(self):
        pass

    def testExecute(self):
        self.cmd.execute()
        data = self.cmd.dispatchedMessage
        self.failUnless(data['from'], data)
        self.failUnless(data['to'], data)
        self.failUnless(data['subject'], data)
        self.failUnless(data['body'], data)
        #url = 'http://%s%s/person/home/' % (self.dictionary[SITE_HOST], self.dictionary[URI_PREFIX])
        acceptUrl = 'http://%s%s/projects/%s/members/%s/approve/' % (self.dictionary[SITE_HOST], self.dictionary[URI_PREFIX], self.project.name, self.person.name)
        rejectUrl = 'http://%s%s/projects/%s/members/%s/reject/' % (self.dictionary[SITE_HOST], self.dictionary[URI_PREFIX], self.project.name, self.person.name)
        self.failUnless(acceptUrl in data['body'], (acceptUrl, data['body']))
        self.failUnless(rejectUrl in data['body'], (rejectUrl, data['body']))


class MockEmailJoinApprove(EmailJoinApprove):

    def dispatchEmailMessage(self, msgFrom, msgTo, msgSubject, msgBody):
        self.dispatchedMessage = {}
        self.dispatchedMessage['from'] = msgFrom
        self.dispatchedMessage['to'] = msgTo
        self.dispatchedMessage['subject'] = msgSubject
        self.dispatchedMessage['body'] = msgBody
        self.isDispatchedOK = True


class TestEmailJoinApprove(kforge.testunit.TestCase):

    def setUp(self):
        self.person = self.registry.people['levin']
        self.project = self.registry.projects['annakarenina']
        self.cmd = MockEmailJoinApprove(self.project, self.person)

    def tearDown(self):
        pass

    def testExecute(self):
        self.cmd.execute()
        data = self.cmd.dispatchedMessage
        self.failUnless(data['from'], data)
        self.failUnless(data['to'], data)
        self.failUnless(data['subject'], data)
        self.failUnless(data['body'], data)


class MockEmailJoinReject(EmailJoinReject):

    def dispatchEmailMessage(self, msgFrom, msgTo, msgSubject, msgBody):
        self.dispatchedMessage = {}
        self.dispatchedMessage['from'] = msgFrom
        self.dispatchedMessage['to'] = msgTo
        self.dispatchedMessage['subject'] = msgSubject
        self.dispatchedMessage['body'] = msgBody
        self.isDispatchedOK = True


class TestEmailJoinReject(kforge.testunit.TestCase):

    def setUp(self):
        self.person = self.registry.people['levin']
        self.project = self.registry.projects['warandpeace']
        self.cmd = MockEmailJoinReject(self.project, self.person)

    def tearDown(self):
        pass

    def testExecute(self):
        self.cmd.execute()
        data = self.cmd.dispatchedMessage
        self.failUnless(data['from'], data)
        self.failUnless(data['to'], data)
        self.failUnless(data['subject'], data)
        self.failUnless(data['body'], data)
