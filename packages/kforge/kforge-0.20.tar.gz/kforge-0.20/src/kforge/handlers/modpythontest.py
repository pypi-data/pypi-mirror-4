import os
import unittest
from kforge.testunit import TestCase
from kforge.handlers.modpython import ModPythonHandler
from kforge.handlers.modpython import PythonAccessHandler
from kforge.handlers.modpython import PythonAuthenHandler
from kforge.handlers.apachecodes import *
from kforge.dictionarywords import *
from django.http import HttpRequest
import kforge.url

# Assumed that these statements are true for the domain model.
#   - admin can do everything
#   - natasha is admin of war and peace
#   - natasha is friend of annakarenina
#   - visitor is friend of war and peace
#   - visitor is not member of annakarenina

# Todo: Assert above preconditions are satisfied before running suite.


def suite():
    suites = [
        # Four cases for anonymous cookie client on access handler.
        unittest.makeSuite(TestModPythonHandler),
        unittest.makeSuite(TestAccessHandlerCookieClientAnonymousGetOk),
        unittest.makeSuite(TestAccessHandlerCookieClientAnonymousGetDeny),
        # Todo: Write test for anonymous write from cookie client (PostOk).
        unittest.makeSuite(TestAccessHandlerCookieClientAnonymousPostDeny),
        # Four cases for authenticated cookie client on access handler.
        unittest.makeSuite(TestAccessHandlerCookieClientWithCookieGetOk),
        unittest.makeSuite(TestAccessHandlerCookieClientWithCookieGetDeny),
        unittest.makeSuite(TestAccessHandlerCookieClientWithCookiePostOk),
        unittest.makeSuite(TestAccessHandlerCookieClientWithCookiePostDeny),
        # Four cases for basic client on access handler.
        unittest.makeSuite(TestAccessHandlerBasicClientGetOk),
        unittest.makeSuite(TestAccessHandlerBasicClientGetDefer),
        # Todo: Write test for anonymous write from basic client (PostOk).
        unittest.makeSuite(TestAccessHandlerBasicClientPostDefer),
        # Four cases for basic client on authen handler.
        unittest.makeSuite(TestAuthenHandlerBasicClientGetOk),
        unittest.makeSuite(TestAuthenHandlerBasicClientGetDeny),
        unittest.makeSuite(TestAuthenHandlerBasicClientPostOk),
        unittest.makeSuite(TestAuthenHandlerBasicClientPostDeny),
        # One case for cookie client on authen handler (shouldn't get there).
        unittest.makeSuite(TestAuthenHandlerCookieClientDeny),
    ]
    return unittest.TestSuite(suites)


class MockTableRecord(dict):

    def add(self, key, value):
        self[key] = value


class MockPythonRequest(HttpRequest):

    def __init__(self, user='', method='GET', project='annakarenina', 
            service='example'):
        self.uri = kforge.url.UrlScheme().url_for(
            'projects.service', project=project, service=service)
        self.method = method
        self.headers_in = MockTableRecord()
        self.headers_out = MockTableRecord()
        self.err_headers_out = MockTableRecord()
        self.subprocess_env = MockTableRecord()
        self.options = {
            'KFORGE_SETTINGS'       : os.environ['KFORGE_SETTINGS'],
            'DJANGO_SETTINGS_MODULE': os.environ['DJANGO_SETTINGS_MODULE'],
        }
        self.user = ''
        self.setUser(user)
        self.bodyContent = ''

    def setUser(self, user):
        pass

    def get_options(self):
        return self.options

    def add_common_vars(self):
        pass

    def write(self, bodyContent):
        self.bodyContent += bodyContent


class BasicClientRequest(MockPythonRequest):

    passwords = {
        '': '',
        'visitor': '',
        'admin': 'pass',
        'natasha': 'pass',
    }
    def __init__(self, *args, **kwds):
        super(BasicClientRequest, self).__init__(*args, **kwds)
        self.subprocess_env = {'HTTP_USER_AGENT': 'SVN'}

    def setUser(self, user):
        self.user = user

    def get_basic_auth_pw(self):
        return self.passwords[self.user]


class CookieClientAnonymous(MockPythonRequest):

    def __init__(self, *args, **kwds):
        super(CookieClientAnonymous, self).__init__(*args, **kwds)
        self.subprocess_env.add('HTTP_USER_AGENT', 'Mozilla')

    def setUser(self, user):
        self.user = ''
        self.addSessionCookie(user)

    def addSessionCookie(self, user):
        pass


class CookieClientWithCookie(CookieClientAnonymous):

    def __init__(self, *args, **kwds):
        super(CookieClientWithCookie, self).__init__(*args, **kwds)

    def addSessionCookie(self, user):
        import dm.view.base
        view = dm.view.base.ControlledAccessView(None)
        person = view.registry.people[user]
        session = person.sessions.create()
        cookieString = view.makeCookieStringFromSessionKey(session.key)
        cookieName = view.dictionary[AUTH_COOKIE_NAME]
        self.headers_in.add('Cookie', "%s=%s" % (cookieName, cookieString))
        # so we can delete the session after the test
        self.sessionFixture = session


class HandlerTestCase(TestCase):

    # To be overridden in sub-class test cases.
    requestUser = ''
    requestMethod = 'GET'
    requestProject = 'annakarenina'
    requestService = 'example'
    requestClass = None
    handlerClass = None

    requireCookieClient = False
    requireHandlerSession = None
    requireCode = None
    requireAccess = False
    requireRequestStatus = None
    requireAuthuserName = 'visitor'
    requireRequestUser = ''

    def setUp(self):
        self.request = self.requestClass(user=self.requestUser,
            method=self.requestMethod, project=self.requestProject,
            service=self.requestService)
        self.handler = self.handlerClass(self.request)
        self.failUnless(self.handler)

    def test_authorise(self):
        self.authorisationCode = self.handler.authorise()
        self.checkAuthorisation()

    def checkAuthorisation(self):
        self.checkAuthorisationCode()
        self.checkClientDetection()
        self.checkHandlerSession()
        self.checkAccessStatus()
        self.checkRequestStatus()
        self.checkAuthuserName()
        self.checkRequestUser()

    def checkAuthorisationCode(self):
        self.failIf(self.requireCode == None)
        self.failUnlessEqual(self.requireCode, self.authorisationCode)

    def checkClientDetection(self):
        canCookie = self.handler.isCookieClient()
        self.failUnlessEqual(canCookie, self.requireCookieClient)

    def checkHandlerSession(self):
        if self.requireHandlerSession == None:
            return
        if self.requireHandlerSession:
            self.failUnless(self.handler.session)
        else:
            self.failIf(self.handler.session)

    def checkAccessStatus(self):
        self.failUnlessEqual(self.requireAccess, self.handler.accessStatus)

    def checkRequestStatus(self):
        if self.requireRequestStatus == None:
            return
        self.failUnlessEqual(self.requireRequestStatus,
            self.handler.request.status)
        if self.requireRequestStatus == HTTP_MOVED_TEMPORARILY:
            self.failUnless(self.request.err_headers_out.has_key('Location'))

    def checkAuthuserName(self):
        if self.requireAuthuserName:
            self.failUnlessEqual(self.requireAuthuserName, self.handler.authuser.name)
        else:
            self.failIf(self.handler.authuser)

    def checkRequestUser(self):
        self.failUnlessEqual(self.requireRequestUser, self.request.user)

    def tearDown(self):
        if self.request and hasattr(self.request, 'sessionFixture'):
            self.request.sessionFixture.delete()
        self.request = None
        self.handler = None


class TestModPythonHandler(HandlerTestCase):

    requestUser = ''
    requestMethod = 'GET'
    requestProject = 'annakarenina'
    requestService = 'example'
    handlerClass = None
    requestClass = None

    handlerClass = ModPythonHandler
    requestClass = MockPythonRequest
    requireCode = DEFER_OR_DENY
    requireAccess = False
    requireRequestStatus = None
    requireAuthuserName = ''
    requireRequestUser = ''

    def test_normalizeUriPath(self):
        self.handler.authorise()
        self.failUnlessEqual(
            self.handler.normalizeUriPath('/path/'),
            '/path',
        )

    def test_validateUri(self):
        self.handler.authorise()
        self.failUnless(self.handler.validateUri('/path/to/something/'))
        self.failUnless(self.handler.validateUri('/path'))
        self.failIf(self.handler.validateUri('/'))


class TestAccessHandlerCookieClientAnonymousGetOk(HandlerTestCase):

    requestUser = ''
    requestMethod = 'GET'
    requestProject = 'warandpeace'
    requestService = 'example'
    requestClass = CookieClientAnonymous
    handlerClass = PythonAccessHandler

    requireCookieClient = True
    requireHandlerSession = False
    requireCode = STOP_AND_APPROVE
    requireAccess = True
    requireRequestStatus = None
    requireAuthuserName = 'visitor'
    requireRequestUser = ''


class TestAccessHandlerCookieClientAnonymousGetDeny(HandlerTestCase):

    requestUser = ''
    requestMethod = 'GET'
    requestProject = 'annakarenina'
    requestService = 'example'
    requestClass = CookieClientAnonymous
    handlerClass = PythonAccessHandler

    requireCookieClient = True
    requireHandlerSession = False
    requireCode = DONE
    requireAccess = False
    requireRequestStatus = HTTP_MOVED_TEMPORARILY
    requireAuthuserName = 'visitor'
    requireRequestUser = ''
    

class TestAccessHandlerCookieClientAnonymousPostDeny(HandlerTestCase):

    requestUser = ''
    requestMethod = 'POST'
    requestProject = 'annakarenina'
    requestService = 'example'
    requestClass = CookieClientAnonymous
    handlerClass = PythonAccessHandler

    requireCookieClient = True
    requireHandlerSession = False
    requireCode = DONE
    requireAccess = False
    requireRequestStatus = HTTP_MOVED_TEMPORARILY
    requireAuthuserName = 'visitor'
    requireRequestUser = ''


class TestAccessHandlerCookieClientWithCookieGetOk(HandlerTestCase):

    requestUser = 'natasha'
    requestMethod = 'GET'
    requestProject = 'warandpeace'
    requestService = 'example'
    requestClass = CookieClientWithCookie
    handlerClass = PythonAccessHandler

    requireCookieClient = True
    requireHandlerSession = True
    requireCode = STOP_AND_APPROVE
    requireAccess = True
    requireRequestStatus = None
    requireAuthuserName = 'natasha'
    requireRequestUser = 'natasha'
    
        
class TestAccessHandlerCookieClientWithCookieGetDeny(HandlerTestCase):

    requestUser = 'natasha'
    requestMethod = 'GET'
    requestProject = 'annakarenina'
    requestService = 'example'
    requestClass = CookieClientWithCookie
    handlerClass = PythonAccessHandler

    requireCookieClient = True
    requireHandlerSession = True
    requireCode = DONE
    requireAccess = False
    requireRequestStatus = HTTP_MOVED_TEMPORARILY
    requireAuthuserName = 'natasha'
    requireRequestUser = ''
    
        
class TestAccessHandlerCookieClientWithCookiePostOk(HandlerTestCase):

    requestUser = 'natasha'
    requestMethod = 'POST'
    requestProject = 'warandpeace'
    requestService = 'example'
    requestClass = CookieClientWithCookie
    handlerClass = PythonAccessHandler

    requireCookieClient = True
    requireHandlerSession = True
    requireCode = STOP_AND_APPROVE
    requireAccess = True
    requireRequestStatus = None
    requireAuthuserName = 'natasha'
    requireRequestUser = 'natasha'
    
        
class TestAccessHandlerCookieClientWithCookiePostDeny(HandlerTestCase):

    requestUser = 'visitor'
    requestMethod = 'POST'
    requestProject = 'warandpeace'
    requestService = 'example'
    requestClass = CookieClientWithCookie
    handlerClass = PythonAccessHandler

    requireCookieClient = True
    requireHandlerSession = True
    requireCode = DONE
    requireAccess = False
    requireRequestStatus = HTTP_MOVED_TEMPORARILY
    requireAuthuserName = 'visitor'
    requireRequestUser = ''
    
        
class TestAccessHandlerBasicClientGetOk(HandlerTestCase):

    requestUser = ''
    requestMethod = 'GET'
    requestProject = 'warandpeace'
    requestService = 'example'
    requestClass = BasicClientRequest
    handlerClass = PythonAccessHandler

    requireCookieClient = False
    requireHandlerSession = False
    requireCode = STOP_AND_APPROVE
    requireAccess = True
    requireRequestStatus = None
    requireAuthuserName = 'visitor'
    requireRequestUser = ''
       

class TestAccessHandlerBasicClientGetDefer(HandlerTestCase):

    requestUser = ''
    requestMethod = 'GET'
    requestProject = 'annakarenina'
    requestService = 'example'
    requestClass = BasicClientRequest
    handlerClass = PythonAccessHandler

    requireCookieClient = False
    requireHandlerSession = False
    requireCode = DEFER_OR_DENY
    requireAccess = False
    requireRequestStatus = None
    requireAuthuserName = 'visitor'
    requireRequestUser = ''
       

class TestAccessHandlerBasicClientPostDefer(HandlerTestCase):

    requestUser = ''
    requestMethod = 'POST'
    requestProject = 'annakarenina'
    requestService = 'example'
    requestClass = BasicClientRequest
    handlerClass = PythonAccessHandler

    requireCookieClient = False
    requireHandlerSession = False
    requireCode = DEFER_OR_DENY
    requireAccess = False
    requireRequestStatus = None
    requireAuthuserName = 'visitor'
    requireRequestUser = ''
       

class TestAuthenHandlerBasicClientGetOk(HandlerTestCase):

    requestUser = 'admin'
    requestMethod = 'GET'
    requestProject = 'annakarenina'
    requestService = 'example'
    requestClass = BasicClientRequest
    handlerClass = PythonAuthenHandler

    requireCookieClient = False
    requireHandlerSession = None
    requireCode = STOP_AND_APPROVE
    requireAccess = True
    requireRequestStatus = None
    requireAuthuserName = 'admin'
    requireRequestUser = 'admin'


class TestAuthenHandlerBasicClientGetDeny(HandlerTestCase):

    requestUser = ''
    requestMethod = 'GET'
    requestProject = 'annakarenina'
    requestService = 'example'
    requestClass = BasicClientRequest
    handlerClass = PythonAuthenHandler

    requireCookieClient = False
    requireHandlerSession = None
    requireCode = DEFER_OR_DENY
    requireAccess = False
    requireRequestStatus = None
    requireAuthuserName = 'visitor'
    requireRequestUser = ''


class TestAuthenHandlerBasicClientPostOk(HandlerTestCase):

    requestUser = 'admin'
    requestMethod = 'POST'
    requestProject = 'annakarenina'
    requestService = 'example'
    requestClass = BasicClientRequest
    handlerClass = PythonAuthenHandler

    requireCookieClient = False
    requireHandlerSession = None
    requireCode = STOP_AND_APPROVE
    requireAccess = True
    requireRequestStatus = None
    requireAuthuserName = 'admin'
    requireRequestUser = 'admin'


class TestAuthenHandlerBasicClientPostDeny(HandlerTestCase):

    requestUser = ''
    requestMethod = 'POST'
    requestProject = 'annakarenina'
    requestService = 'example'
    requestClass = BasicClientRequest
    handlerClass = PythonAuthenHandler

    requireCookieClient = False
    requireHandlerSession = None
    requireCode = DEFER_OR_DENY
    requireAccess = False
    requireRequestStatus = None
    requireAuthuserName = 'visitor'
    requireRequestUser = ''


class TestAuthenHandlerCookieClientDeny(HandlerTestCase):

    requestUser = 'admin'
    requestMethod = 'GET'
    requestProject = 'annakarenina'
    requestService = 'example'
    requestClass = CookieClientWithCookie
    handlerClass = PythonAuthenHandler

    requireCookieClient = True
    requireHandlerSession = None
    requireCode = STOP_AND_DENY
    requireAccess = False
    requireRequestStatus = None
    requireAuthuserName = ''
    requireRequestUser = ''


