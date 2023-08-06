import unittest
from kforge.handlers.modpythontest import ModPythonHandlerTestCase
from kforge.handlers.modpythontest import MockModPythonRequest
from kforge.handlers.projecthost import PythonAccessHandler
from kforge.handlers.projecthost import PythonAuthenHandler
from kforge.handlers.apachecodes import *
from kforge.dictionarywords import *
import kforge.url



def suite():
    suites = [
#        unittest.makeSuite(TestPythonAccessHandler),
#        unittest.makeSuite(TestPythonAccessHandler_WithCookie),
#        unittest.makeSuite(TestPythonAuthenHandler),
    ]
    return unittest.TestSuite(suites)


class MockPythonAccessRequest(MockModPythonRequest):

    def __init__(self):
        super(MockPythonAccessRequest, self).__init__()
        self.subprocess_env.add('HTTP_USER_AGENT', 'Mozilla')
    

class TestPythonAccessHandler(ModPythonHandlerTestCase):

    requestClass = MockPythonAccessRequest
    handlerClass = PythonAccessHandler
    url_scheme = kforge.url.UrlScheme()

    def test_isCookieClient(self):
        self.handler.authorise()
        self.failUnless(self.handler.isCookieClient())

    def test_authorise_OK(self):
        self.failUnlessEqual(
            self.handler.authorise(),
            HTTP_FORBIDDEN
        )
        self.failIf(self.handler.isAccessAllowed)
        self.failIf(self.handler.session)

    def test_authorise_DENY(self):
        self.request.method = 'POST'
        self.failUnlessEqual(
            self.handler.authorise(),
            HTTP_FORBIDDEN
        )
        self.failIf(self.handler.isAccessAllowed)
        self.failUnlessEqual(
            self.request.status,
            HTTP_MOVED_TEMPORARILY
        )
        self.failUnless(self.request.err_headers_out.has_key('Location'))
        # visitor is member
        uri = self.url_scheme.url_for('projects.service', project='annakarenina',
                service='example')
        self.request.uri = uri
        self.request.method = 'GET'
        self.failUnlessEqual(
            self.handler.authorise(),
            HTTP_FORBIDDEN
        )
        self.failUnlessEqual(
            self.request.status,
            HTTP_MOVED_TEMPORARILY
        )
        self.request.method = 'POST'
        self.failUnlessEqual(
            self.handler.authorise(),
            HTTP_FORBIDDEN
        )
        self.failUnlessEqual(
            self.request.status,
            HTTP_MOVED_TEMPORARILY
        )
        
    def test_authorise_DEFER(self):
        self.request.method = 'POST'
        self.request.subprocess_env['HTTP_USER_AGENT'] = 'SVN'
        self.failUnlessEqual(
            self.handler.authorise(),
            HTTP_UNAUTHORIZED
        )


class MockPythonAccessRequest_WithCookie(MockPythonAccessRequest):

    def __init__(self):
        super(MockPythonAccessRequest_WithCookie, self).__init__()
        self.addSessionCookie()

    def addSessionCookie(self):
        import dm.view.base
        view = dm.view.base.ControlledAccessView(None)
        person = view.registry.people['natasha']  # admin for warandpeace
        session = person.sessions.create()
        cookieString = view.makeCookieStringFromSessionKey(session.key)
        cookieName = view.dictionary[AUTH_COOKIE_NAME]
        self.headers_in.add('Cookie', "%s=%s" % (cookieName, cookieString))

        # so we can delete the session after the test
        self.sessionFixture = session


class TestPythonAccessHandler_WithCookie(ModPythonHandlerTestCase):

    requestClass = MockPythonAccessRequest_WithCookie
    handlerClass = PythonAccessHandler
    url_scheme = kforge.url.UrlScheme()

    def tearDown(self):
        self.request.sessionFixture.delete()
        super(TestPythonAccessHandler_WithCookie, self).tearDown()

    def test_authorise_OK(self):
        self.failUnlessEqual(
            self.handler.authorise(),
            HTTP_FORBIDDEN
        )
        self.failUnlessEqual(
            self.handler.isAccessAllowed,
            False
        )
        self.failUnless(self.handler.session)
        
    def test_authorise_REDIRECT(self):
        self.request.method = 'POST'
        # natasha not member
        uri = self.url_scheme.url_for('projects.service', project='annakarenina',
                service='example')
        self.request.uri = uri
        
        self.failUnlessEqual(
            self.handler.authorise(),
            HTTP_FORBIDDEN
        )
        self.failUnlessEqual(
            self.handler.isAccessAllowed,
            False
        )
        self.failUnless(self.handler.session)
        self.failUnlessEqual(
            self.request.status,
            HTTP_MOVED_TEMPORARILY
        )
        

class MockPythonAuthenRequest(MockModPythonRequest):

    def __init__(self):
        super(MockPythonAuthenRequest, self).__init__()
        self.subprocess_env = {'HTTP_USER_AGENT': 'SVN'}
        self.user = 'admin'
        self.basicAuthPass = 'pass'

    def get_basic_auth_pw(self):
        return self.basicAuthPass


class TestPythonAuthenHandler(ModPythonHandlerTestCase):

    requestClass = MockPythonAuthenRequest
    handlerClass = PythonAuthenHandler

    def test_isCookieClient(self):
        self.handler.authorise()
        self.failIf(self.handler.isCookieClient())

    def test_authorise_OK(self):
        self.failUnlessEqual(self.handler.authorise(), OK)
        self.request.method = 'POST'
        self.failUnlessEqual(self.handler.authorise(), OK)

    def test_authorise_DENY_visitor(self):
        self.request.method = 'POST'
        self.request.user = ''
        self.failUnlessEqual(
            self.handler.authorise(),
            HTTP_UNAUTHORIZED
        )
        
    def test_authorise_DENY_Mozilla(self):
        self.request.method = 'POST'
        self.request.subprocess_env['HTTP_USER_AGENT'] = 'Mozilla'
        self.failUnlessEqual(
            self.handler.authorise(),
            HTTP_FORBIDDEN
        )


