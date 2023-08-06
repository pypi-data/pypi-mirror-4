import unittest
from kforge.test import RequiresPlugins
from kforge.django.apps.kui.views.test.base import ViewTestCase
from kforge.django.apps.kui.views.service import ServiceListView
from kforge.django.apps.kui.views.service import ServiceCreateView
from kforge.django.apps.kui.views.service import ServiceReadView
from kforge.django.apps.kui.views.service import ServiceUpdateView
from kforge.django.apps.kui.views.service import ServiceDeleteView
from kforge.django.apps.kui.views.service import ServiceView
from dm.util.datastructure import MultiValueDict

# Todo: Indicate whether apache restarted since service was created
# so that the user knows whether a new service will respond.

# Todo: Redirect delay for service update and delete.

def suite():
    suites = [
        unittest.makeSuite(TestServiceListView),
        unittest.makeSuite(TestServiceListViewNatasha),
        unittest.makeSuite(TestServiceCreateView),
        unittest.makeSuite(TestServiceCreateViewNatasha),
        unittest.makeSuite(TestServiceCreateViewNatashaPOST),
        unittest.makeSuite(TestServiceCreateViewNatashaPOSTErrorInUse),
        unittest.makeSuite(TestServiceCreateViewNatashaPOSTErrorRequired),
        unittest.makeSuite(TestServiceCreateViewNatashaPOSTErrorInvalid),
        unittest.makeSuite(TestServiceCreateViewNatashaPOSTSvn),
        unittest.makeSuite(TestServiceCreateViewNatashaPOSTTrac),
        unittest.makeSuite(TestServiceReadView),
        unittest.makeSuite(TestServiceReadViewNatasha),
        unittest.makeSuite(TestServiceUpdateView),
        unittest.makeSuite(TestServiceUpdateViewNatasha),
        unittest.makeSuite(TestServiceUpdateViewNatashaPOST),
        unittest.makeSuite(TestServiceUpdateViewNatashaPOSTTrac),
        unittest.makeSuite(TestServiceUpdateViewNatashaPOSTTracSvn),
        unittest.makeSuite(TestServiceUpdateViewNatashaPOSTTracHg),
        #unittest.makeSuite(TestServiceUpdateViewNatashaPOSTErrorInUse),
        #unittest.makeSuite(TestServiceUpdateViewNatashaPOSTErrorRequired),
        #unittest.makeSuite(TestServiceUpdateViewNatashaPOSTErrorInvalid),
        unittest.makeSuite(TestServiceDeleteView),
        unittest.makeSuite(TestServiceDeleteViewNatasha),
        unittest.makeSuite(TestServiceDeleteViewNatashaPOST),
    ]
    return unittest.TestSuite(suites)


class ServiceTestCase(RequiresPlugins, ViewTestCase):

    projectName = 'warandpeace'

    def createViewKwds(self):
        viewKwds = super(ServiceTestCase, self).createViewKwds()
        viewKwds['domainObjectKey'] = self.projectName
        if hasattr(self, 'serviceName'):
            viewKwds['hasManyKey'] = self.serviceName
        return viewKwds

# Todo: Test for when service create view has service type passed in, check create form with correct extn fields is returned normally. So "Select service type" form, then "Create <service type> service" with extn fields, then "Edit <service name> service" with extn fields.
# Todo: Method to get plugin model extn fields from service with service type.


class TestServiceListView(ServiceTestCase):

    viewClass = ServiceListView

    def test_canCreate(self):
        object = None
        self.failIf(self.view.canCreateService())

    def test_canRead(self):
        object = None
        self.failUnless(self.view.canReadService())

    def test_canUpdate(self):
        object = None
        self.failIf(self.view.canUpdateService())

    def test_canDelete(self):
        object = None
        self.failIf(self.view.canDeleteService())


class TestServiceListViewNatasha(ServiceTestCase):

    viewerName = 'natasha'
    viewClass = ServiceListView

    def test_canCreate(self):
        object = None
        self.failUnless(self.view.canCreateService())

    def test_canRead(self):
        object = None
        self.failUnless(self.view.canReadService())

    def test_canUpdate(self):
        object = None
        self.failUnless(self.view.canUpdateService())

    def test_canDelete(self):
        object = None
        self.failUnless(self.view.canDeleteService())


class TestServiceCreateView(ServiceTestCase):

    viewClass = ServiceCreateView
    requiredRedirect = '%s/login/' % ViewTestCase.URI_PREFIX 
    requiredResponseClassName = 'HttpResponseRedirect'


class TestServiceCreateViewNatasha(ServiceTestCase):

    viewerName = 'natasha'
    viewClass = ServiceCreateView
    requiredRedirect = ''
    requiredResponseClassName = 'HttpResponse'


class TestServiceCreateViewNatashaPOSTErrorInUse(ServiceTestCase):

    viewerName = 'natasha'
    viewClass = ServiceCreateView
    POST = MultiValueDict({'name': ['example'], 'plugin': ['/plugins/example']})
    requiredFormErrors = "The name 'example' is already being used."
    requiredResponseClassName = 'HttpResponseBadRequest'
    requiredRedirect = ''


class TestServiceCreateViewNatashaPOSTErrorRequired(ServiceTestCase):

    viewerName = 'natasha'
    viewClass = ServiceCreateView
    POST = MultiValueDict({'name': [''], 'plugin': ['/plugins/example']})
    requiredFormErrors = ['Name is required.']
    requiredResponseClassName = 'HttpResponseBadRequest'
    requiredRedirect = ''


class TestServiceCreateViewNatashaPOSTErrorInvalid(ServiceTestCase):

    viewerName = 'natasha'
    viewClass = ServiceCreateView
    POST = MultiValueDict({'name': ['/'], 'plugin': ['/plugins/example']})
    requiredFormErrors = ['Enter a valid name.']
    requiredResponseClassName = 'HttpResponseBadRequest'
    requiredRedirect = ''

class TestServiceCreateViewNatashaPOSTErrorInUse(ServiceTestCase):

    viewerName = 'natasha'
    viewClass = ServiceCreateView
    POST = MultiValueDict({'name': ['example'], 'plugin': ['/plugins/example']})
    requiredFormErrors = "The name 'example' is already being used."
    requiredResponseClassName = 'HttpResponseBadRequest'
    requiredRedirect = ''

class TestServiceCreateViewNatashaPOST(ServiceTestCase):

    viewerName = 'natasha'
    viewClass = ServiceCreateView
    POST = MultiValueDict({'name': ['example2'], 'plugin': ['/plugins/example']})
    requiredRedirect = '/projects/warandpeace/services/example2/'
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredFormErrors = False

    def tearDown(self):
        if 'example2' in self.registry.projects[self.projectName].services:
            service = self.registry.projects[self.projectName].services['example2']
            service.delete()
            service.purge()
        super(TestServiceCreateViewNatashaPOST, self).tearDown()


class TestServiceCreateViewNatashaPOSTSvn(ServiceTestCase):

    viewerName = 'natasha'
    viewClass = ServiceCreateView
    POST = MultiValueDict({'name': ['svn'], 'plugin': ['/plugins/svn']})
    requiredRedirect = '/projects/warandpeace/services/svn/'
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredFormErrors = False
    requiredPlugins = ['svn']

    def tearDown(self):
        if 'svn' in self.registry.projects[self.projectName].services:
            service = self.registry.projects[self.projectName].services['svn']
            service.delete()
            service.purge()
        super(TestServiceCreateViewNatashaPOSTSvn, self).tearDown()


class TestServiceCreateViewNatashaPOSTTrac(ServiceTestCase):

    viewerName = 'natasha'
    viewClass = ServiceCreateView
    POST = MultiValueDict({'name': ['trac'], 'plugin': ['/plugins/trac']})
    requiredRedirect = '/projects/warandpeace/services/trac/'
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredFormErrors = False
    requiredPlugins = ['trac']

    def tearDown(self):
        if 'trac' in self.registry.projects[self.projectName].services:
            service = self.registry.projects[self.projectName].services['trac']
            service.delete()
            service.purge()
        super(TestServiceCreateViewNatashaPOSTTrac, self).tearDown()

    def test_getResponse(self):
        super(TestServiceCreateViewNatashaPOSTTrac, self).test_getResponse()
        service = self.registry.projects[self.projectName].services['trac']
        tracProject = service.getExtnObject()
        self.failUnless(tracProject.isEnvironmentInitialised, repr(tracProject))


class TestServiceReadView(ServiceTestCase):

    viewClass = ServiceReadView
    serviceName = 'example'


class TestServiceReadViewNatasha(ServiceTestCase):

    viewerName = 'natasha'
    viewClass = ServiceReadView
    serviceName = 'example'


class TestServiceUpdateView(ServiceTestCase):

    viewClass = ServiceUpdateView
    serviceName = 'example'
    requiredRedirect = '%s/login/' % ViewTestCase.URI_PREFIX
    requiredResponseClassName = 'HttpResponseRedirect'


class TestServiceUpdateViewNatasha(ServiceTestCase):

    viewerName = 'natasha'
    serviceName = 'example'
    viewClass = ServiceUpdateView
    requiredRedirect = ''
    requiredResponseClassName = 'HttpResponse'


class TestServiceUpdateViewNatashaPOST(TestServiceUpdateViewNatasha):

    POST = MultiValueDict({'submit': 'submit changes'})
    requiredRedirect = '/projects/warandpeace/services/example/'
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredFormErrors = False


class TestServiceUpdateViewNatashaPOSTTrac(TestServiceUpdateViewNatashaPOST):
    # Check update trac service, without setting repository.

    serviceName = 'trac'
    requiredRedirect = '/projects/warandpeace/services/trac/'
    requiredPlugins = ['trac']

    def initPost(self):
        tracService = self.createTracService()
        tracProject = self.getTracProject()
        self.failUnless(tracProject.isEnvironmentInitialised)
        self.failUnless(tracProject.isOperational())
        configfileText = tracProject.asDictValues()['configfile']
        self.POST = MultiValueDict({})
        self.POST['configfile'] = configfileText

    def tearDown(self):
        self.destroyTracService()
        super(TestServiceUpdateViewNatashaPOSTTrac, self).tearDown()

    def createTracService(self):
        tracPlugin = self.registry.plugins['trac']
        project = self.registry.projects[self.projectName]
        return project.services.create('trac', plugin=tracPlugin)

    def getTracProject(self):
        project = self.registry.projects[self.projectName]
        if 'trac' not in project.services:
            raise Exception, "No service named 'trac' in project services: %s" % project.services.keys()
        service = project.services['trac']
        return service.getExtnObject()

    def destroyTracService(self):
        project = self.registry.projects[self.projectName]
        if 'trac' in project.services:
            service = project.services['trac']
            service.delete()
            service.purge()
    
    def test_getResponse(self):
        super(TestServiceUpdateViewNatashaPOSTTrac, self).test_getResponse()
        tracProject = self.getTracProject()
        self.failUnless(tracProject.isEnvironmentInitialised)
        self.failUnless(tracProject.isOperational())
        configfileText = tracProject.asDictValues()['configfile']
        self.failUnless(configfileText)
        repositories = tracProject.asDictValues()['repositories']
        self.checkRepositories(repositories)

    def checkRepositories(self, repositories):
        self.failIf(repositories)


class TestServiceUpdateViewNatashaPOSTTracSvn(TestServiceUpdateViewNatashaPOSTTrac):
    # Check update trac service, with setting repository (svn).

    requiredPlugins = ['trac', 'svn']

    def initPost(self):
        super(TestServiceUpdateViewNatashaPOSTTracSvn, self).initPost()
        project = self.registry.projects[self.projectName]
        svnPlugin = self.registry.plugins['svn']
        svnService = project.services.create('svn', plugin=svnPlugin)
        self.failUnless(svnService.getUri())
        self.POST['repositories'] = [svnService.getUri()]

    def tearDown(self):
        self.destroySvnService()
        super(TestServiceUpdateViewNatashaPOSTTracSvn, self).tearDown()

    def destroySvnService(self):
        project = self.registry.projects[self.projectName]
        if 'svn' in project.services:
            service = project.services['svn']
            service.delete()
            service.purge()
    
    def checkRepositories(self, repositories):
        self.failUnless(repositories)


class TestServiceUpdateViewNatashaPOSTTracHg(TestServiceUpdateViewNatashaPOSTTrac):
    # Check update trac service, with setting repository (hg).

    requiredPlugins = ['trac', 'mercurial']

    def initPost(self):
        super(TestServiceUpdateViewNatashaPOSTTracHg, self).initPost()
        project = self.registry.projects[self.projectName]
        hgPlugin = self.registry.plugins['mercurial']
        hgService = project.services.create('hg', plugin=hgPlugin)
        self.failUnless(hgService.getUri())
        self.POST['repositories'] = [hgService.getUri()]

    def tearDown(self):
        self.destroyHgService()
        super(TestServiceUpdateViewNatashaPOSTTracHg, self).tearDown()

    def destroyHgService(self):
        project = self.registry.projects[self.projectName]
        if 'hg' in project.services:
            service = project.services['hg']
            service.delete()
            service.purge()
    
    def checkRepositories(self, repositories):
        self.failUnless(repositories)


#class TestServiceUpdateViewNatashaPOSTErrorInUse(TestServiceUpdateViewNatashaPOST):
#
#    POST = MultiValueDict({'name': ['example']})
#    requiredRedirect = ''
#    requiredResponseClassName = 'HttpResponseBadRequest'
#    requiredFormErrors = "The name 'example' is already being used."
#    
#
#class TestServiceUpdateViewNatashaPOSTErrorRequired(TestServiceUpdateViewNatashaPOST):
#
#    POST = MultiValueDict({'name': ['']})
#    requiredRedirect = ''
#    requiredResponseClassName = 'HttpResponseBadRequest'
#    requiredFormErrors = ['Name is required.']
#    
#
#class TestServiceUpdateViewNatashaPOSTErrorInvalid(TestServiceUpdateViewNatashaPOST):
#
#    POST = MultiValueDict({'name': [' ']})
#    requiredRedirect = ''
#    requiredResponseClassName = 'HttpResponseBadRequest'
#    requiredFormErrors = ['Enter a valid name.']
    

class TestServiceDeleteView(ServiceTestCase):

    viewClass = ServiceDeleteView
    serviceName = 'example'
    requiredRedirect = '%s/login/' % ViewTestCase.URI_PREFIX
    requiredResponseClassName = 'HttpResponseRedirect'


class TestServiceDeleteViewNatasha(ServiceTestCase):

    viewerName = 'natasha'
    serviceName = 'example'
    viewClass = ServiceDeleteView
    requiredRedirect = ''
    requiredResponseClassName = 'HttpResponse'


class TestServiceDeleteViewNatashaPOST(ServiceTestCase):

    viewerName = 'natasha'
    serviceName = 'example2'
    viewClass = ServiceDeleteView
    POST = MultiValueDict({'Submit': ['submit']})
    requiredRedirect = '/projects/warandpeace/'
    #if ServiceCreateView.isReloadingModWsgi():
    #    requiredResponseClassName = 'HttpResponse'
    #else:
    #    requiredResponseClassName = 'HttpResponseRedirect'
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredFormErrors = False

    def setUp(self):
        if 'example2' not in self.registry.projects[self.projectName].services:
            plugin = self.registry.plugins['example']
            self.domainObject = self.registry.projects[self.projectName].services.create('example2', plugin=plugin)
        super(TestServiceDeleteViewNatashaPOST, self).setUp()

    def tearDown(self):
        super(TestServiceDeleteViewNatashaPOST, self).tearDown()
        if 'example2' in self.registry.projects[self.projectName].services:
            service = self.registry.projects[self.projectName].services['example2']
            service.delete()
            service.purge()
            self.fail("Project still has a service called 'example2'.")
            
