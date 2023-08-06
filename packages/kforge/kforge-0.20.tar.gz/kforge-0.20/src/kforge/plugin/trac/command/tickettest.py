import unittest
from kforge.plugin.trac.command.basetest import TracCommandTestCase
from kforge.plugin.trac.command.ticket import CreateTracTicket
from kforge.plugin.trac.command.ticket import ReadTracTicket
from kforge.plugin.trac.command.ticket import UpdateTracTicket
from kforge.plugin.trac.command.ticket import DeleteTracTicket
from kforge.plugin.trac.command.ticket import ListTracTickets
from kforge.plugin.trac.command.ticket import ListTracTicketIds
from kforge.plugin.trac.exceptions import TracTicketNotFound
import os

def suite():
    suites = [
        unittest.makeSuite(TestCreateTracTicket),
        unittest.makeSuite(TestReadTracTicket),
        unittest.makeSuite(TestUpdateTracTicket),
        unittest.makeSuite(TestDeleteTracTicket),
        unittest.makeSuite(TestListTracTickets),
        unittest.makeSuite(TestListTracTicketIds),
    ]
    return unittest.TestSuite(suites)


class TestCreateTracTicket(TracCommandTestCase):

    def test(self):
        cmd = CreateTracTicket(self.tracProject, {
            'priority': 'major',
            'summary': 'Test ticket',
            'type': 'defect',
            'owner': '', 
            'reporter': 'natasha',
            'cc': ''
        })
        ticketId = cmd.execute()
        self.failUnlessEqual(ticketId, 1)
        ticketId = cmd.execute()
        self.failUnlessEqual(ticketId, 2)
        ticketId = cmd.execute()
        self.failUnlessEqual(ticketId, 3)


class TestReadTracTicket(TracCommandTestCase):

    def setUp(self):
        super(TestReadTracTicket, self).setUp()
        cmd = CreateTracTicket(self.tracProject, {
            'priority': 'major',
            'summary': 'Test ticket',
            'type': 'defect',
            'owner': '', 
            'reporter': 'natasha',
            'cc': ''
        })
        self.tracTicketId = cmd.execute()

    def test(self):
        cmd = ReadTracTicket(self.tracProject, self.tracTicketId)
        ticketData = cmd.execute()
        self.failUnlessEqual(ticketData['priority'], 'major')
        self.failUnlessEqual(ticketData['summary'], 'Test ticket')
        self.failUnlessEqual(ticketData['type'], 'defect')
        self.failUnlessEqual(ticketData['owner'], '')
        self.failUnlessEqual(ticketData['reporter'], 'natasha')
        self.failUnlessEqual(ticketData['cc'], '')
        # Check TracTicketNotFound error.
        cmd = ReadTracTicket(self.tracProject, None)
        self.failUnlessRaises(TracTicketNotFound, cmd.execute)
        cmd = ReadTracTicket(self.tracProject, 99)
        self.failUnlessRaises(TracTicketNotFound, cmd.execute)


class TestUpdateTracTicket(TracCommandTestCase):

    def setUp(self):
        super(TestUpdateTracTicket, self).setUp()
        cmd = CreateTracTicket(self.tracProject, {
            'priority': 'major',
            'summary': 'Test ticket',
            'type': 'defect',
            'owner': '', 
            'reporter': 'natasha',
            'cc': ''
        })
        self.tracTicketId = cmd.execute()

    def test(self):
        cmd = UpdateTracTicket(self.tracProject, self.tracTicketId, {
            'priority': 'minor',
            'summary': 'Test ticket update',
            'type': 'enhancement',
            'owner': 'natasha', 
            'reporter': 'levin',
            'cc': 'admin'
        })
        cmd.execute()
        cmd = ReadTracTicket(self.tracProject, self.tracTicketId)
        ticketData = cmd.execute()
        self.failUnlessEqual(ticketData['priority'], 'minor')
        self.failUnlessEqual(ticketData['summary'], 'Test ticket update')
        self.failUnlessEqual(ticketData['type'], 'enhancement')
        self.failUnlessEqual(ticketData['owner'], 'natasha')
        self.failUnlessEqual(ticketData['reporter'], 'levin')
        self.failUnlessEqual(ticketData['cc'], 'admin')


class TestDeleteTracTicket(TracCommandTestCase):

    def setUp(self):
        super(TestDeleteTracTicket, self).setUp()
        cmd = CreateTracTicket(self.tracProject, {
            'priority': 'major',
            'summary': 'Test ticket',
            'type': 'defect',
            'owner': '', 
            'reporter': 'natasha',
            'cc': ''
        })
        self.tracTicketId = cmd.execute()

    def test(self):
        readCmd = ReadTracTicket(self.tracProject, self.tracTicketId)
        readCmd.execute()
        DeleteTracTicket(self.tracProject, self.tracTicketId).execute()
        self.failUnlessRaises(TracTicketNotFound, readCmd.execute)


class TestListTracTickets(TracCommandTestCase):

    def setUp(self):
        super(TestListTracTickets, self).setUp()
        cmd = CreateTracTicket(self.tracProject, {
            'priority': 'major',
            'summary': 'Test ticket',
            'type': 'defect',
            'owner': '', 
            'reporter': 'natasha',
            'cc': ''
        })
        ticketId = cmd.execute()

    def test(self):
        cmd = ListTracTickets(self.tracProject)
        tickets = cmd.execute()
        self.failUnlessEqual(len(tickets), 1)
        ticket = tickets[0]
        self.failUnlessEqual(ticket['id'], 1)
        self.failUnlessEqual(ticket['summary'], 'Test ticket')


class TestListTracTicketIds(TracCommandTestCase):

    def setUp(self):
        super(TestListTracTicketIds, self).setUp()
        cmd = CreateTracTicket(self.tracProject, {
            'priority': 'major',
            'summary': 'Test ticket',
            'type': 'defect',
            'owner': '', 
            'reporter': 'natasha',
            'cc': ''
        })
        ticketId = cmd.execute()

    def test(self):
        cmd = ListTracTicketIds(self.tracProject)
        ticketIds = cmd.execute()
        self.failUnless(len(ticketIds), 1)
        self.failUnless(ticketIds[0], 1)



