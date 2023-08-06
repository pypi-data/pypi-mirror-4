import unittest
from kforge.test.customer.plugin.base import PluginTestCase
import os
from time import sleep

def suite():
    suites = [
        unittest.makeSuite(TestTrac),
        unittest.makeSuite(TestTracConfigEdit),
        unittest.makeSuite(TestTracTickets),
        unittest.makeSuite(TestTracTicketSearch),
        unittest.makeSuite(TestTracWithSvn),
        unittest.makeSuite(TestTracWithMercurial),
        unittest.makeSuite(TestTracWithGit),
        unittest.makeSuite(TestTracSetPreferences),
        unittest.makeSuite(TestTracAuthenticatedProjectVisitor),
        unittest.makeSuite(TestTracAuthenticatedProjectDeveloper),
        unittest.makeSuite(TestTracAuthenticatedProjectAdministrator),
    ]
    return unittest.TestSuite(suites)


class TracTestCase(PluginTestCase):

    requiredPlugins = ['trac']

    def createTracService(self):
        self.createService('trac', 'trac', wait=True)

    def getTracPath(self, serviceName='trac'):
        return self.getServicePath(serviceName)
 
    def getNewTracTicketUrl(self, serviceName='trac'):
        return self.getServicePath(serviceName) +'newticket'

    def getTracTicketSearchUrl(self, serviceName='trac'):
        return self.getPersonPath(serviceName) +'search'

    def getTracTimelineUrl(self, serviceName='trac'):
        return self.getServicePath(serviceName) +'timeline'

    def getTracPermissionAdminPath(self, serviceName='trac'):
        return self.getServicePath(serviceName) +'admin/general/perm'

    def getTracAdminPath(self, serviceName='trac'):
        return self.getServicePath(serviceName) +'admin'

    def tearDown(self):
        services = self.registry.projects[self.kuiProjectName].services
        if 'trac' in services:
            del(services['trac'])
        if 'svn' in services:
            del(services['svn'])
        super(TracTestCase, self).tearDown()

    def getFormIndex(self, page, formId):
        formIndex = None
        for (index, form) in enumerate(page.getDOM().getByName('form')):
            if form.hasattr('id'):
                value = form.getattr('id')
                if value == formId:
                    return index
        raise Exception, "Can't find '%s' form in page: %s" % (formId, page.body)



class TestTrac(TracTestCase):

    def testHttpClient(self):
        # Check Trac service is not found.
        urlService = self.getServicePath('trac')
        self.getAssertCode(urlService, 404)

        # Create Trac service.
        self.createTracService()

        # Check 'Welcome' message.
        self.getAssertContent(urlService, 'Welcome to Trac')

        # Check unauthorized access.
        self.logoutPerson()
        self.getAssertCode(urlService, 401)

        # Check basic authentication access.
        self.setBasicAuthPerson()
        self.getAssertContent(urlService, 'Welcome to Trac')
        self.clearBasicAuth()

        # Check cookie-based authentication access, again.
        self.loginPerson()
        self.getAssertContent(urlService, 'Welcome to Trac')


class TestTracConfigEdit(TracTestCase):

    def testHttpClient(self):
        # Create Trac service.
        self.createTracService()
        # Get trac service edit form.
        tracEditUrl = self.getProjectServiceEditPath('trac')
        page = self.getAssertCode(tracEditUrl, code=200)
        formdata = page.extractForm([('form', 0)])
        # Check for form looks okay.
        self.failUnless('repositories' in formdata)
        # Check there is a config file field.
        self.failUnless('configfile' in formdata)
        config = formdata['configfile']
        self.failUnless('render_unsafe_content = false' in config, config)
        self.failIf('render_unsafe_content = true' in config, config)
        # Change the config file field.
        config = config.replace('render_unsafe_content = false', 'render_unsafe_content = true')
        self.failUnless('render_unsafe_content = true' in config, config)
        formdata['configfile'] = config
        # Submit the form.
        page.postForm(0, self.post, formdata)
        # Get trac service edit form.
        page = self.getAssertCode(tracEditUrl, code=200)
        formdata = page.extractForm([('form', 0)])
        # Check field value is the edited value.
        config = formdata['configfile']
        self.failIf('render_unsafe_content = false' in config, config)
        self.failUnless('render_unsafe_content = true' in config, config)
        # Check the new configuration is effective.


class TracTicketsTestCase(TracTestCase):

    def createNewTicket(self, summary):
        # Create new ticket.
        newticketUrl = self.getNewTracTicketUrl()
        page = self.getAssertCode(newticketUrl, code=200)
        formData = {
            'field_owner': self.kuiPersonName,
            'field_summary': summary,
        }
        page = page.postForm(1, self.postAssertCode, formData, 303)
        return page


class TestTracTickets(TracTicketsTestCase):

    def testHttpClient(self):
        # Create Trac service.
        self.createTracService()

        # Check the ticket isn't created.
        project = self.registry.projects[self.kuiProjectName]
        service = project.services['trac']
        tickets = service.getExtnObject().tickets

        # Check there are no tickets for the service.
        self.failUnlessEqual(len(tickets), 0)

        # Create new ticket.
        summary = 'Testing Trac tickets'
        page = self.createNewTicket(summary=summary)

        # Check the ticket is created.
        self.failUnless('Location' in page.headers)
        ticketUrl = page.headers['Location']
        self.getAssertContent(ticketUrl, summary, code=200)

        # Check the service has the ticket.
        # NB Tests the TracTickets WSGI middleware.
        self.failUnlessEqual(len(tickets), 1, tickets)
        self.failUnlessEqual(list(tickets)[0].summary, summary, tickets)

        # Update the ticket summary.
        newSummary = 'Trac ticket testing is continuing...'
        self.getAssertNotContent(ticketUrl, newSummary, code=200)

        formData = {
            'field_summary': newSummary,
        }
        # NB page.postForm doesn't work with mod_python for some reason.
        #formIndex = self.getFormIndex(page, 'propertyform')
        #page.postForm(formIndex, self.postAssertCode, formData, 303)
        self.extractFormAndPost(ticketUrl, 'propertyform', formData)

        # Check the summary has changed.
        self.getAssertContent(ticketUrl, newSummary, code=200)
        
        # Check the service still has the ticket.
        # NB Tests the TracTickets WSGI middleware.
        self.failUnlessEqual(len(tickets), 1, tickets)
        self.failUnlessEqual(list(tickets)[0].summary, newSummary, tickets)

        # Close the ticket.
        oldSummary = summary
        newSummary = 'Trac ticket testing is continuing elsewhere...'
        formData = {
            'field_summary': newSummary,
            'action': 'resolve',
            'action_resolve_resolve_resolution': 'fixed',
        }
        # NB page.postForm doesn't work with mod_python for some reason.
        #formIndex = self.getFormIndex(page, 'propertyform')
        #page = self.getAssertContent(ticketUrl, oldSummary, code=200)
        #page.postForm(formIndex, self.postAssertCode, formData, 303)
        self.extractFormAndPost(ticketUrl, 'propertyform', formData)
        
        # Check the summary has changed.
        self.getAssertContent(ticketUrl, newSummary, code=200)
        
        # Check the service no longer has the ticket.
        # NB Tests the TracTickets WSGI middleware.
        self.failUnlessEqual(len(tickets), 0)
        # Check the ticket is deleted.
        self.failUnlessEqual(len(tickets.deleted), 1)
        self.failUnlessEqual(list(tickets.deleted)[0].status, 'closed')

        # Reopen the ticket.
        oldSummary = newSummary
        newSummary = 'Trac ticket testing is continuing here...'
        self.getAssertNotContent(ticketUrl, newSummary, code=200)
        formData = {
            'field_summary': newSummary,
            'action': 'reopen',
        }
        # NB page.postForm doesn't work with mod_python for some reason.
        #formIndex = self.getFormIndex(page, 'propertyform')
        #page = self.getAssertContent(ticketUrl, oldSummary, code=200)
        #page = page.postForm(formIndex, self.postAssertCode, formData, 303)
        self.extractFormAndPost(ticketUrl, 'propertyform', formData)
        
        # Check the service has the ticket again.
        # NB Tests the TracTickets WSGI middleware.
        self.failUnlessEqual(len(tickets), 1, tickets)
        self.failUnlessEqual(list(tickets)[0].summary, newSummary, tickets)

    def extractFormAndPost(self, url, formName, formParams, codes=[303]):
        page = self.get(url)
        formIndex = self.getFormIndex(page, formName)
        formData = page.extractForm([('form', formIndex)])
        formData.update(formParams)
        page = self.postAssertCode(url, formData, codes)
        return page


class TestTracTicketSearch(TracTicketsTestCase):

    def testHttpClient(self):
        # Create Trac service.
        return
        self.createTracService()

        # Check there are no tickets.
        project = self.registry.projects[self.kuiProjectName]
        service = project.services['trac']
        tickets = service.getExtnObject().tickets
        self.failUnlessEqual(len(tickets), 0)

        # Create new tickets.
        for i in range(0, 16):
            page = self.createNewTicket(summary='Testing Trac ticket%s...' % i)

        # Check there are fifteen tickets.
        tickets = service.getExtnObject().tickets
        self.failUnlessEqual(len(tickets), 16)

        # Search for tickets.
        formData = {'userQuery':'zzzzz'}
        self.failUnlessSearch(formData, count=0);
        formData = {'userQuery':'ticket'}
        self.failUnlessSearch(formData, count=16);
        formData = {'userQuery':'ticket15'}
        self.failUnlessSearch(formData, count=1);
        formData = {'userQuery':'ticket14'}
        self.failUnlessSearch(formData, count=1);

    def failUnlessSearch(self, formData, count=None):
        page = self.searchTickets(formData)
        requiredText = ' %s ticket%s.' % (count, count != 1 and 's' or '')
        self.failUnless(requiredText in page.body, "'%s' not in page: %s" % (requiredText, page.body))

    def searchTickets(self, formData={}):
        page = self.getAssertCode(self.urlPersonTicketSearch, code=200)
        page = page.postForm(0, self.postAssertCode, formData, 200)
        return page



class RepositoryTestCase(TracTestCase):

    requiredPlugins = ['trac', 'svn', 'mercurial', 'git']

    def testHttpClient(self):
        self.createTracService()

        # Check we cannot see the browser view.
        urlService = self.getServicePath('trac')
        urlBrowser = urlService+'browser'
        self.getAssertCode(urlBrowser, code=404)

        # Add repository.
        self.addRepository()

        # Create a changeset.
        commitMsg = "Testing '%s' repository with Trac timeline" % self.repositoryName
        self.addChangesetToRepository(commitMsg)

        # Check we can see the browser view.
        self.getAssertCode(urlBrowser, code=200)

        # Check repository is showing in code browser.
        self.getAssertContent(urlBrowser, self.repositoryName)

        # Check commit message is showing in timeline.
        urlTimeline = urlService + 'timeline'
        self.getAssertContent(urlTimeline, commitMsg, code=200)

        # Note well, Trac prefers URLs without trailing slashes. :-)
        urlTimeline = urlService + 'timeline/'
        self.getAssertCode(urlTimeline, 301)

    def addRepository(self):
        # Create repository service.
        self.createService(self.repositoryName, self.repositoryName)
        # Set repository.
        editUrl = self.getProjectServiceEditPath('trac')
        page = self.getAssertCode(editUrl, code=200)
        params = page.extractForm([('form', 0)])
        svnUri = self.registry.projects[self.kuiProjectName].services[self.repositoryName].getUri()
        params['repositories'] = [svnUri]
        self.postAssertCode(editUrl, params)

    def addChangesetToRepository(self, commitMsg):
        raise Exception, "No 'checkout/clone/add/commit/push' method for VCS '%s'." % self.repositoryName

class TestTracWithSvn(RepositoryTestCase):

    repositoryName = 'svn'

    def addChangesetToRepository(self, commitMsg):
        self.svnCheckoutAddCommit(self.repositoryName, commitMsg)


class TestTracWithMercurial(RepositoryTestCase):

    repositoryName = 'mercurial'

    def addChangesetToRepository(self, commitMsg):
        self.mercurialCloneAddCommitPush(self.repositoryName, commitMsg)


class TestTracWithGit(RepositoryTestCase):

    repositoryName = 'git'

    def addChangesetToRepository(self, commitMsg):
        self.gitCloneAddCommitPush(self.repositoryName, commitMsg)


class PreferencesTestCase(TracTestCase):

    requiredPlugins = ['trac', 'svn']
    tracCacheDelay = 5  # Necessary but not sure why.

    def setupTracServiceWithRepository(self, serviceName='trac', repositoryName='svn'):
        # Setup trac service with svn repository.
        self.createService('trac', serviceName)
        if repositoryName not in self.registry.projects[self.kuiProjectName].services:
            self.createService('svn', repositoryName)
        svnUri = self.getProjectServiceUri(repositoryName)
        tracEditUrl = self.getProjectServiceEditPath(serviceName)
        page = self.getAssertCode(tracEditUrl, code=200)
        params = page.extractForm([('form', 0)])
        params['repositories'] = [svnUri]
        self.postAssertCode(tracEditUrl, params) 


class TestTracSetPreferences(PreferencesTestCase):

    def testHttpClient(self):
        # Setup trac service with svn repository.
        self.setupTracServiceWithRepository()
        # Check for person's registered details.
        urlService = self.getServicePath('trac')
        urlPreferences = urlService + 'prefs'
        self.getAssertContent(urlPreferences, 'This page lets you customize your personal settings for this site.')
        #self.getAssertContent(urlPreferences, self.kuiPersonFullname)
        #self.getAssertContent(urlPreferences, self.kuiPersonEmail)
        # Update the person's registered details.
        params = {}
        params['submission'] = '1'
        params['password'] = ''
        params['passwordconfirmation'] = ''
        fullnameCorrection = 'newCorrectFullname'
        params['fullname'] = fullnameCorrection
        emailCorrection = 'correct.email%s@appropriatesoftware.net' % self.randomInteger
        params['email'] = emailCorrection
        self.postAssertCode(self.urlPersonUpdate, params)
        # Check for updated details.
        self.getAssertNotContent(urlPreferences, self.kuiPersonFullname)
        self.getAssertNotContent(urlPreferences, self.kuiPersonEmail)
        self.getAssertContent(urlPreferences, emailCorrection)
        self.getAssertContent(urlPreferences, fullnameCorrection)

        # Add a new member to the project.
        newName = 'admin'
        newPass = 'pass'
        newPerson = self.registry.people[newName]
        newFullname = str(newPerson.fullname)
        newEmail = str(newPerson.email)
        params = {'person': '/people/%s' % newName, 'role': '/roles/Friend'}
        self.postAssertCode(self.urlProjectMemberCreate, params, code=302)
        self.logoutPerson()
        # Check for new member details.
        self.loginPerson(newName, newPass)
        self.getAssertContent(urlPreferences, newFullname)
        self.getAssertContent(urlPreferences, newEmail)
        self.logoutPerson()
        # Add a new Trac service to the project.
        self.loginPerson()
        self.setupTracServiceWithRepository('trac2')
        # Check for updated details.
        urlService = self.getServicePath('trac2')
        urlPreferences = urlService + 'prefs'
        self.getAssertContent(urlPreferences, emailCorrection)
        self.getAssertContent(urlPreferences, fullnameCorrection)
        self.logoutPerson()
        # Check for new member details.
        self.loginPerson(newName, newPass)
        self.getAssertContent(urlPreferences, newFullname)
        self.getAssertContent(urlPreferences, newEmail)
        self.logoutPerson()


class TestTracAuthenticatedProjectVisitor(PreferencesTestCase):

    # This test case exists because Trac sets up permissions for authenticated
    # users to create and modify tickets and wiki pages (which is bad). KForge
    # will remove these permissions so that only members have such access.
    def testHttpClient(self):
        # Setup trac service with svn repository.
        self.setupTracServiceWithRepository()
        urlService = self.getServicePath('trac')
        self.getAssertContent(urlService, '>New Ticket</a>', code=200)
        # Add visitor as a friend.
        self.getAssertNotContent(self.urlProjectMembers, 'visitor')
        postdata = {'person': '/people/visitor', 'role': '/roles/Friend'}
        self.postAssertCode(self.urlProjectMemberCreate, postdata, code=302)
        self.getAssertContent(self.urlProjectMembers, 'visitor')
        # Check levin cannot create tickets.
        self.logoutPerson()
        self.loginPerson('levin', 'levin')
        self.getAssertNotContent(urlService, '>New Ticket</a>', code=200)
        # Check levin cannot do admin stuff.
        self.getAssertNotContent(urlService, '>Admin</a>', code=200)


class TestTracAuthenticatedProjectDeveloper(PreferencesTestCase):

    def testHttpClient(self):
        urlService = self.getTracPath()
        urlServiceAdmin = self.getTracAdminPath()
        urlServiceAdminPerm = self.getTracPermissionAdminPath()
        urlServiceNewTicket = self.getNewTracTicketUrl()
        # Setup trac service with svn repository.
        self.setupTracServiceWithRepository()
        # Add levin as a developer.
        self.addLevinProjectRole('Developer')
        # Switch login to levin.
        self.logoutPerson()
        self.loginPerson('levin', 'levin')
        # Check new ticket page is OK.
        self.getAssertCode(urlServiceNewTicket, code=200)
        # Check admin page is Not Found.
        self.getAssertCode(urlServiceAdminPerm, code=404)
        self.getAssertNotContent(urlService, '>Admin</a>', code=200)
        # Change levin to Friend.
        self.changeLevinProjectRole('Friend')
        # Check new ticket page is Forbidden.
        self.getAssertCode(urlServiceNewTicket, code=403)
        # Check admin page is Not Found.
        self.getAssertCode(urlServiceAdminPerm, code=404)
        self.getAssertNotContent(urlService, '>Admin</a>', code=200)
        # Change levin to Developer.
        self.changeLevinProjectRole('Developer')
        # Check new ticket page is OK.
        self.getAssertCode(urlServiceNewTicket, code=200)
        # Check admin page is Not Found.
        self.getAssertCode(urlServiceAdminPerm, code=404)
        # Change levin to Visitor.
        self.changeLevinProjectRole('Visitor')
        # Check new ticket page redirects.
        self.getAssertCode(urlServiceNewTicket, code=302)
        # Check admin page redirects.
        self.getAssertCode(urlServiceAdminPerm, code=302)
        # Change levin to Developer.
        self.changeLevinProjectRole('Developer')
        # Check new ticket page is OK.
        self.getAssertCode(urlServiceNewTicket, code=200)
        # Check admin page is Not Found.
        self.getAssertCode(urlServiceAdminPerm, code=404)
        # Remove levin.
        self.removeLevinProjectRole()
        # Check new ticket page redirects.
        self.getAssertCode(urlServiceNewTicket, code=302)
        # Check admin page redirects.
        self.getAssertCode(urlServiceAdminPerm, code=302)

    def addLevinProjectRole(self, roleName):
        r = self.registry
        r.people['levin'].memberships.create(
            project=r.projects[self.kuiProjectName],
            role=r.roles[roleName],
        )
        sleep(self.tracCacheDelay)

    def removeLevinProjectRole(self):
        r = self.registry
        m = r.people['levin'].memberships[r.projects[self.kuiProjectName]]
        m.delete()
        sleep(self.tracCacheDelay)

    def changeLevinProjectRole(self, roleName):
        r = self.registry
        m = r.people['levin'].memberships[r.projects[self.kuiProjectName]]
        m.role = r.roles[roleName]
        m.save()
        sleep(self.tracCacheDelay)


class TestTracAuthenticatedProjectAdministrator(PreferencesTestCase):

    def testHttpClient(self):
        urlService = self.getTracPath()
        urlServiceAdmin = self.getTracAdminPath()
        urlServiceAdminPerm = self.getTracPermissionAdminPath()
        urlServiceNewTicket = self.getNewTracTicketUrl()
        # Setup trac service with svn repository.
        self.setupTracServiceWithRepository()
        # Check admin page is OK.
        self.getAssertCode(urlServiceAdminPerm, code=200)
        # Change to Developer.
        self.changePersonProjectRole('Developer')
        # Check admin page is Not Found.
        sleep(self.tracCacheDelay)
        self.getAssertCode(urlServiceAdminPerm, code=404)
        self.getAssertNotContent(urlService, '>Admin</a>', code=200)
        # Change to Administrator.
        self.changePersonProjectRole('Administrator')
        # Check admin page is OK.
        sleep(self.tracCacheDelay)
        self.getAssertCode(urlServiceAdminPerm, code=200)
        self.getAssertContent(urlService, '>Admin</a>', code=200)
        # Change to Friend.
        self.changePersonProjectRole('Friend')
        # Check admin page is Not Found.
        sleep(self.tracCacheDelay)
        self.getAssertCode(urlServiceAdminPerm, code=404)
        self.getAssertNotContent(urlService, '>Admin</a>', code=200)
        # Change to Administrator.
        self.changePersonProjectRole('Administrator')
        # Check admin page is OK.
        sleep(self.tracCacheDelay)
        self.getAssertCode(urlServiceAdminPerm, code=200)
        self.getAssertContent(urlService, '>Admin</a>', code=200)

