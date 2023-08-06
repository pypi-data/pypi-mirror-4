import os
import unittest
from kforge.testunit import TestCase
from kforge.handlers.modwsgi import WsgiCheckPasswordHandler
from kforge.handlers.modwsgi import WsgiAccessControlHandler
from kforge.dictionarywords import *
from django.http import HttpRequest
import kforge.url
import base64

# Assumed that these statements are true for the domain model.
#   - admin can do everything
#   - natasha is admin of war and peace
#   - natasha is friend of annakarenina
#   - visitor is friend of war and peace
#   - visitor is not member of annakarenina

# Todo: Assert above preconditions are satisfied before running suite.


def suite():
    suites = [
        # Four cases for basic client on access controller.
        unittest.makeSuite(TestWsgiCheckPasswordHandlerBasicClientGetOk),
        unittest.makeSuite(TestWsgiCheckPasswordHandlerBasicClientGetDeny),
        unittest.makeSuite(TestWsgiCheckPasswordHandlerBasicClientPostOk),
        unittest.makeSuite(TestWsgiCheckPasswordHandlerBasicClientPostDeny),
        # Four cases for basic client on access control handler.
        unittest.makeSuite(TestWsgiAccessControlBasicClientGetOk),
        unittest.makeSuite(TestWsgiAccessControlBasicClientGetDeny),
        unittest.makeSuite(TestWsgiAccessControlBasicClientPostOk),
        unittest.makeSuite(TestWsgiAccessControlBasicClientPostDeny),
        # Four cases for authenticated cookie client on access control handler.
        unittest.makeSuite(TestWsgiAccessControlCookieClientWithCookieGetOk),
        unittest.makeSuite(TestWsgiAccessControlCookieClientWithCookieGetDeny),
        unittest.makeSuite(TestWsgiAccessControlCookieClientWithCookiePostOk),
        unittest.makeSuite(TestWsgiAccessControlCookieClientWithCookiePostDeny),
        # Four cases for unauthenticated cookie client on access control handler.
        #unittest.makeSuite(TestWsgiAccessControlCookieClientAnonymousGetOk),
        #unittest.makeSuite(TestWsgiAccessControlCookieClientAnonymousGetDeny),
        #unittest.makeSuite(TestWsgiAccessControlCookieClientAnonymousPostOk),
        #unittest.makeSuite(TestWsgiAccessControlCookieClientAnonymousPostDeny),
    ]
    return unittest.TestSuite(suites)


class MockWsgiEnviron(dict):

    def __init__(self, method='GET', project='annakarenina', service='example'):
        uri = kforge.url.UrlScheme().url_for('projects.service', project=project, service=service)
        self.update({
            'KFORGE_SETTINGS'       : os.environ['KFORGE_SETTINGS'],
            'DJANGO_SETTINGS_MODULE': os.environ['DJANGO_SETTINGS_MODULE'],
            'REQUEST_METHOD': method,
            'REQUEST_URI': uri,
        })


class WsgiHandlerTestCase(TestCase):

    # To be overridden in sub-class test cases.
    requestUser = ''
    requestMethod = 'GET'
    requestProject = 'annakarenina'
    requestService = 'example'
    environClass = None
    handlerClass = None

    requireCookieClient = False
    requireHandlerSession = None
    requireResponse = None
    requireAccess = False
    requireRequestUser = ''
    requireAuthuserName = 'visitor'

    passwords = {
        '': '',
        'visitor': '',
        'admin': 'pass',
        'natasha': 'pass',
    }

    def setUp(self):
        self.environ = self.createEnviron()
        self.handler = self.createHandler()
        self.failUnless(self.handler)

    def createEnviron(self):
        raise Exception, "Method not implemented on %s" % self

    def createHandler(self):
        raise Exception, "Method not implemented on %s" % self

    def testCallHandler(self):
        self.callHandler()
        self.checkAuthorisation()

    def callHandler(self):
        raise Exception, "Method not implemented on %s" % self

    def checkAuthorisation(self):
        self.checkHandlerResponse()
        self.checkClientDetection()
        self.checkHandlerSession()
        self.checkAccessStatus()
        self.checkAuthuserName()
        self.checkRequestUser()

    def checkHandlerResponse(self):
        self.failIf(self.requireResponse == None)
        self.failUnlessEqual(self.requireResponse, self.handlerResponse)

    def checkClientDetection(self):
        canCookie = self.handler.isCookieClient()
        self.failUnlessEqual(canCookie, self.requireCookieClient)

    def checkHandlerSession(self):
        if self.requireHandlerSession:
            self.failUnless(self.handler.session)

    def checkAccessStatus(self):
        self.failUnlessEqual(self.requireAccess, self.handler.accessStatus)

    def checkAuthuserName(self):
        if self.requireAuthuserName:
            self.failUnlessEqual(self.requireAuthuserName, self.handler.authuser.name)
        else:
            self.failIf(self.handler.authuser)

    def checkRequestUser(self):
        self.failUnlessEqual(self.requireRequestUser, self.handler.getRequestCredentials()[0])

    def tearDown(self):
        if self.environ and hasattr(self.environ, 'sessionFixture'):
            self.environ.sessionFixture.delete()
        self.environ = None
        self.handler = None


class CheckPasswordEnviron(MockWsgiEnviron):

    def __init__(self, *args, **kwds):
        super(CheckPasswordEnviron, self).__init__(*args, **kwds)
        self.update({'HTTP_USER_AGENT': 'SVN'})


class WsgiCheckPasswordHandlerTestCase(WsgiHandlerTestCase):

    environClass = CheckPasswordEnviron
    handlerClass = WsgiCheckPasswordHandler

    def createEnviron(self):
        return self.environClass(
            method=self.requestMethod, 
            project=self.requestProject,
            service=self.requestService
        )

    def createHandler(self):
        return self.handlerClass()

    def callHandler(self):
        user = self.requestUser
        password = self.passwords[self.requestUser]
        self.handlerResponse = self.handler.__call__(self.environ, user, password)

 
class TestWsgiCheckPasswordHandlerBasicClientGetOk(WsgiCheckPasswordHandlerTestCase):

    requestUser = 'admin'
    requestProject = 'annakarenina'
    requestService = 'example'

    requireResponse = True
    requireAccess = True
    requireRequestUser = 'admin'
    requireAuthuserName = 'admin'


class TestWsgiCheckPasswordHandlerBasicClientGetDeny(WsgiCheckPasswordHandlerTestCase):

    requestProject = 'annakarenina'
    requestService = 'example'

    requireResponse = False
    requireAccess = False
    requireAuthuserName = 'visitor'


class TestWsgiCheckPasswordHandlerBasicClientPostOk(WsgiCheckPasswordHandlerTestCase):

    requestUser = 'admin'
    requestMethod = 'POST'
    requestProject = 'annakarenina'
    requestService = 'example'

    requireResponse = True
    requireAccess = True
    requireRequestUser = 'admin'
    requireAuthuserName = 'admin'


class TestWsgiCheckPasswordHandlerBasicClientPostDeny(WsgiCheckPasswordHandlerTestCase):

    requestMethod = 'POST'
    requestProject = 'annakarenina'
    requestService = 'example'

    requireResponse = False
    requireAccess = False
    requireAuthuserName = 'visitor'


class AccessControlWsgiEnviron(MockWsgiEnviron):

    def __init__(self, *args, **kwds):
        super(AccessControlWsgiEnviron, self).__init__(*args, **kwds)


class WsgiAccessControlHandlerTestCase(WsgiHandlerTestCase):

    handlerClass = WsgiAccessControlHandler
    requireResponse = None
    requireStatus = None
    requireHeaders = None

    def createEnviron(self):
        return self.environClass(
            method=self.requestMethod, 
            project=self.requestProject,
            service=self.requestService,
            user=self.requestUser,
            password=self.passwords[self.requestUser]
        )

    def createHandler(self):
        return self.handlerClass()

    def callHandler(self):
        self.handlerResponse = self.handler(self.environ, self.startResponse)

    def startResponse(self, *args, **kwds):
        self.startResponseArgs = args
        self.startResponseKwds = kwds

    def checkHandlerResponse(self):
        super(WsgiAccessControlHandlerTestCase, self).checkHandlerResponse()
        self.failUnlessEqual(self.startResponseArgs[0], self.requireStatus)
        self.failUnlessEqual(self.startResponseArgs[1], self.requireHeaders)


class AccessControlBasicClientWsgiEnviron(AccessControlWsgiEnviron):

    def __init__(self, *args, **kwds):
        user = kwds.pop('user')
        password = kwds.pop('password')
        super(AccessControlBasicClientWsgiEnviron, self).__init__(*args, **kwds)
        self.update({'HTTP_USER_AGENT': 'SVN'})
        base64string = base64.encodestring('%s:%s' % (user, password))[:-1]
        basicAuthorization =  "Basic %s" % base64string
        self.update({'HTTP_AUTHORIZATION': basicAuthorization})


class WsgiAccessControlBasicClientTestCase(WsgiAccessControlHandlerTestCase):

    environClass = AccessControlBasicClientWsgiEnviron


class TestWsgiAccessControlBasicClientGetOk(WsgiAccessControlBasicClientTestCase):

    requestUser = 'admin'
    requestProject = 'annakarenina'
    requestService = 'example'

    requireStatus = "200 OK"
    requireResponse = ["Access was authorised, but there is no protected application."]
    requireHeaders = [('Content-type', 'text/html; charset=iso-8859-1')]
    requireAccess = True
    requireAuthuserName = 'admin'
    requireRequestUser = 'admin'


class TestWsgiAccessControlBasicClientGetDeny(WsgiAccessControlBasicClientTestCase):

    requestProject = 'annakarenina'
    requestService = 'example'

    requireStatus = "401 Unauthorized"
    requireResponse = [""]
    requireHeaders = [('Content-type', 'text/html; charset=iso-8859-1'), ('WWW-Authenticate', 'Basic realm="%s Restricted Area"' % WsgiHandlerTestCase.dictionary[HTTP_AUTH_REALM])]
    requireAccess = False
    requireAuthuserName = 'visitor'


class TestWsgiAccessControlBasicClientPostOk(WsgiAccessControlBasicClientTestCase):

    requestUser = 'admin'
    requestMethod = 'POST'
    requestProject = 'annakarenina'
    requestService = 'example'

    requireStatus = "200 OK"
    requireResponse = ["Access was authorised, but there is no protected application."]
    requireHeaders = [('Content-type', 'text/html; charset=iso-8859-1')]
    requireAccess = True
    requireRequestUser = 'admin'
    requireAuthuserName = 'admin'


class TestWsgiAccessControlBasicClientPostDeny(WsgiAccessControlBasicClientTestCase):

    requestMethod = 'POST'
    requestProject = 'annakarenina'
    requestService = 'example'

    requireStatus = "401 Unauthorized"
    requireResponse = [""]
    requireHeaders = [('Content-type', 'text/html; charset=iso-8859-1'), ('WWW-Authenticate', 'Basic realm="%s Restricted Area"' % WsgiHandlerTestCase.dictionary[HTTP_AUTH_REALM])]
    requireAccess = False
    requireAuthuserName = 'visitor'


class AccessControlCookieClientWsgiEnviron(AccessControlWsgiEnviron):

    def __init__(self, *args, **kwds):
        user = kwds.pop('user')
        kwds.pop('password')
        super(AccessControlCookieClientWsgiEnviron, self).__init__(*args, **kwds)
        self.update({'HTTP_USER_AGENT': 'Mozilla'})

        # Add session cookie.
        import dm.view.base
        view = dm.view.base.ControlledAccessView(None)
        person = view.registry.people[user]
        session = person.sessions.create()
        cookieString = view.makeCookieStringFromSessionKey(session.key)
        cookieName = view.dictionary[AUTH_COOKIE_NAME]
        # HTTP_COOKIE here rather than Cookie because WSGI environ will be used directly.
        self.update({'HTTP_COOKIE': "%s=%s" % (cookieName, cookieString)})
        # so we can delete the session after the test
        self.sessionFixture = session


class WsgiAccessControlCookieClientWithCookieTestCase(WsgiAccessControlHandlerTestCase):

    environClass = AccessControlCookieClientWsgiEnviron
    requireCookieClient = True

    def tearDown(self):
        if self.environ and hasattr(self.environ, 'sessionFixture'):
            self.environ.sessionFixture.delete()
        self.environ = None
        self.handler = None


class TestWsgiAccessControlCookieClientWithCookieGetOk(WsgiAccessControlCookieClientWithCookieTestCase):

    requestUser = 'admin'
    requestProject = 'annakarenina'
    requestService = 'example'

    requireStatus = "200 OK"
    requireResponse = ["Access was authorised, but there is no protected application."]
    requireHeaders = [('Content-type', 'text/html; charset=iso-8859-1')]
    requireAccess = True
    requireAuthuserName = 'admin'
    requireRequestUser = 'admin'


class TestWsgiAccessControlCookieClientWithCookieGetDeny(WsgiAccessControlCookieClientWithCookieTestCase):

    requestUser = 'natasha'
    requestProject = 'annakarenina'
    requestService = 'example'

    requireStatus = "302 Found"
    requireResponse = [""]
    requireHeaders = [('Content-type', 'text/html; charset=iso-8859-1'), ('Location', '/accessDenied/?returnPath=/annakarenina/example')]
    requireAccess = False
    requireRequestUser = 'natasha'
    requireAuthuserName = 'natasha'


class TestWsgiAccessControlCookieClientWithCookiePostOk(WsgiAccessControlCookieClientWithCookieTestCase):

    requestUser = 'admin'
    requestMethod = 'POST'
    requestProject = 'annakarenina'
    requestService = 'example'

    requireStatus = "200 OK"
    requireResponse = ["Access was authorised, but there is no protected application."]
    requireHeaders = [('Content-type', 'text/html; charset=iso-8859-1')]
    requireAccess = True
    requireRequestUser = 'admin'
    requireAuthuserName = 'admin'


class TestWsgiAccessControlCookieClientWithCookiePostDeny(WsgiAccessControlCookieClientWithCookieTestCase):

    requestUser = 'natasha'
    requestMethod = 'POST'
    requestProject = 'annakarenina'
    requestService = 'example'

    requireStatus = "302 Found"
    requireHeaders = [('Content-type', 'text/html; charset=iso-8859-1'), ('Location', '/accessDenied/?returnPath=/annakarenina/example')]
    requireResponse = [""]
    requireAccess = False
    requireRequestUser = 'natasha'
    requireAuthuserName = 'natasha'

