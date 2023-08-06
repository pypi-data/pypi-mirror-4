import unittest
from kforge.django.apps.kui.views.api import ApiView
from dm.view.apitest import ApiViewTestCase # Test case for single request.
from dm.view.testunit import ApiTestCase  # Test case for CRUD requests on a register.
from kforge.django.apps.kui.views.api import KForgeApiView
from dm.dictionarywords import SYSTEM_VERSION

def suite():
    suites = [
        # Single request test cases.
        unittest.makeSuite(TestApiGetOk),
        unittest.makeSuite(TestApiGetLicensesOk),
        unittest.makeSuite(TestApiGetRolesOk),
        # CRUD requests test cases.
        unittest.makeSuite(TestProject),
    ]
    return unittest.TestSuite(suites)


class TestApiGetOk(ApiViewTestCase):
    requestPath = '/api'
    requiredResponseClassName = 'HttpResponse'
    requiredResponseStatus = 200
    requiredResponseData = [
        u'http://kforge.dev.localhost/api/licenses',
        u'http://kforge.dev.localhost/api/people',
        u'http://kforge.dev.localhost/api/projects',
        u'http://kforge.dev.localhost/api/roles',
        u'http://kforge.dev.localhost/api/systems',
    ]


class TestApiGetLicensesOk(ApiViewTestCase):
    requestPath = '/api/licenses'
    requiredResponseClassName = 'HttpResponse'
    requiredResponseStatus = 200
    requiredResponseData = [
        "http://kforge.dev.localhost/api/licenses/3",
        "http://kforge.dev.localhost/api/licenses/5",
        "http://kforge.dev.localhost/api/licenses/4",
        "http://kforge.dev.localhost/api/licenses/2",
        "http://kforge.dev.localhost/api/licenses/1",
    ]


class TestApiGetRolesOk(ApiViewTestCase):
    requestPath = '/api/roles'
    requiredResponseClassName = 'HttpResponse'
    requiredResponseStatus = 200
    requiredResponseData = [
        "http://kforge.dev.localhost/api/roles/Administrator",
        "http://kforge.dev.localhost/api/roles/Developer",
        "http://kforge.dev.localhost/api/roles/Friend",
        "http://kforge.dev.localhost/api/roles/Visitor",
    ]


class KForgeApiTestCase(ApiTestCase):

    viewClass = KForgeApiView
    apiKeyHeaderName = 'HTTP_X_KFORGE_API_KEY'


class TestProject(KForgeApiTestCase):

    registerName = 'projects'
    newEntity = {'name': 'xxxx', 'title': 'My Project', 'description': 'A project by me.', 'licenses': ['http://kforge.dev.localhost/api/licenses/1']}
    entityKey = 'xxxx'
    notFoundKey = 'zzzz'
    changedEntity = {'name': 'xxxx', 'title': 'Your Project', 'description': 'A project by you.', 'licenses': ['http://kforge.dev.localhost/api/licenses/1']}

    def tearDown(self):
        key = self.newEntity['name']
        if key in self.registry.projects:
            del(self.registry.projects[key])
        key = self.changedEntity['name']
        if key in self.registry.projects:
            del(self.registry.projects[key])
        super(TestProject, self).tearDown()

