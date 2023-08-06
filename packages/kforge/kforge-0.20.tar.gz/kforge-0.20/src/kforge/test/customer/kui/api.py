from kforge.test import RequiresPlugins
from kforge.test.customer.kui.base import KuiTestCase
import unittest
from dmclient.apiclient import ApiClient
from kforge.dictionarywords import *
from time import sleep

def suite():
    suites = [
        unittest.makeSuite(TestProc),
        unittest.makeSuite(TestProjectAndServices),
        unittest.makeSuite(TestMemory),
        # See http://kforge.appropriatesoftware.net/kforge/trac/ticket/98
        #unittest.makeSuite(TestTickets),
    ]
    return unittest.TestSuite(suites)


class TestApi(RequiresPlugins, KuiTestCase):

    requiredPlugins = ['svn', 'trac']

    def setUp(self):
        super(TestApi, self).setUp()
        self.baseUrl = 'http://%s/api' % self.dictionary[SITE_HOST]
        self.registerPerson()
        self.loginPerson()
        headerName = self.dictionary[API_KEY_HEADER_NAME]
        apiKey = self.registry.people['admin'].getApiKey().key
        self.api = ApiClient(baseUrl=self.baseUrl, isVerbose=False,
            apiKeyHeaderName=headerName, apiKey=apiKey)


class TestProc(TestApi):

    def test(self):
        procData = self.getProc()
        self.failUnless(hasattr(procData, 'vsize'), procData)
        self.failUnless(self.getVsize())


class TestProjectAndServices(TestApi):

    def test(self):
        resources = self.api.resources
        projects = resources.projects
        project = projects.create(name=self.kuiProjectName, title=self.kuiProjectTitle, description=self.kuiProjectDescription)
        self.failIf(project.services)
        trac = project.services.create(name='trac', plugin='/plugins/trac')
        svn = project.services.create(name='svn', plugin='/plugins/svn')
        self.failUnless(project.services)
        self.failUnless(project.services)
        trac.repositories.append(svn)
        trac.save()
        project.members.create(person='/people/%s' % self.kuiPersonName, role='/roles/Administrator')
        self.getAssertContent('/%s/trac/browser' % self.kuiProjectName, 'svn', code=200)
        self.getAssertCode('/%s/trac/browser/svn' % self.kuiProjectName, code=200)


class TestMemory(TestApi):

    def test(self):
        resources = self.api.resources
        projects = resources.projects
        samples = []
        for i in range(20):
            self.createMemoryDump()
            samples.append(self.getVsize())
            sleep(0.1)
        first = samples[0:10]
        second = samples[10:20]
        max_first = max(first)
        mean_second = sum(second) / float(len(second))
        self.failUnless(max_first >= mean_second, (max_first, mean_second, first, second))


class TestTickets(TestApi):

    def test(self):
        # Setup project.
        resources = self.api.resources
        projects = resources.projects
        project = projects.create(name=self.kuiProjectName, title=self.kuiProjectTitle, description=self.kuiProjectDescription)
        person = resources.people[self.kuiPersonName]
        project.members.create(person=person, role='/roles/Administrator')
        service = project.services.create(name='trac', plugin='/plugins/trac')
        #self.failIf(person.tickets)
        self.failIf(service.tickets)
        return # Creating tickets via the API isn't supported at the moment.
        # Create a ticket.
        ticket = service.tickets.create(owner=self.kuiPersonName, summary='apitest1')
        self.failUnlessEqual(ticket.url, 'http://kforge.dev.localhost/api/tickets/%s' % (ticket.id))
        self.failUnlessEqual(ticket.service.url, 'http://kforge.dev.localhost/api/projects/%s/services/trac' % (self.kuiProjectName))
        self.failUnlessEqual(ticket.owner, self.kuiPersonName)
        #self.failUnlessEqual(ticket.status, 'new')
        self.failUnlessEqual(ticket.summary, 'apitest1')
        #self.failUnless(person.tickets)
        self.failUnless(service.tickets)
        # Todo: Check the ticket is created in Trac.
        # Update the ticket.
        ticket.summary = 'apitest2'
        ticket.save()
        # Todo: Check the ticket is updated in Trac.
        # Delete the ticket.
        ticket.delete()
        #self.failUnless(person.tickets)
        self.failIf(service.tickets)
        # Todo: Check the ticket is closed in Trac.

