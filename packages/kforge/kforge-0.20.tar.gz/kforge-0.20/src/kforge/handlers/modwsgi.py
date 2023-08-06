import kforge.soleInstance

from kforge.handlers.base import *
from kforge.handlers.apachecodes import *
import re
from kforge.handlers.tracticket import TracTicketFromHeaders

class ModWsgiHandler(BaseHandler):

    def authoriseRequest(self):
        raise Exception, "Method not implemented on %s" % self.__class__

    def getDefaultResponseCode(self):
        return HTTP_INTERNAL_SERVER_ERROR
       
    def getRequestMethod(self):
        return self.getRequestEnvironVar('REQUEST_METHOD')

    def getRefererUri(self):
        return self.getRequestEnvironVar('HTTP_REFERER')

    def getRequestUri(self):
        return self.getRequestEnvironVar('REQUEST_URI')

    def getRequestUserAgent(self):
        return self.getRequestEnvironVar('HTTP_USER_AGENT')

    def getRequestEnvironVar(self, name):
        return self.environ.get(name, '')


class WsgiCheckPasswordHandler(ModWsgiHandler):

    def __call__(self, environ, user, password):
        self.environ = environ
        self.requestuser = user
        self.requestpassword = password
        return self.authorise()

    def authoriseRequest(self):
        if not self.validateRequestUri():
            return False
        self.initAuthuserFromBasicPrompt()
        if self.isAccessAuthorised():
            self.environ['REMOTE_USER'] = self.authuser
            return True
        else:
            return False

    def getRequestCredentials(self):
        return (self.requestuser, self.requestpassword)

    def hasCookies(self):
        return False


class WsgiMiddleware(object):

    def __init__(self, application):
        self.wsgiApplication = application
        import kforge.soleInstance
        self.application = kforge.soleInstance.application

    def __call__(self, environ, start_response):
        self.environ = environ
        if not self.wsgiApplication:
            return [""]
        status, headers, body = self.callWsgiApplication(environ)
        status, headers, body = self.adjustResponse(status, headers, body)
        # Start WSGI response, and return body as list of chunks.
        start_response(status, headers)
        return [body]

    def callWsgiApplication(self, environ):
        import StringIO, sys
        stdout = sys.stdout
        myout = StringIO.StringIO()
        sys.stdout = myout 
        body = []
        status_headers = [None, None]
        # Define a new WSGI start_response method.
        def start_response(status, headers, *args, **kwds):
            status_headers[:] = [status, headers]
            return body.append
        app_iter = self.wsgiApplication(environ, start_response)
        try:
            for item in app_iter:
                body.append(item)
            body.append(myout.getvalue())
        finally:
            if hasattr(app_iter, 'close'):
                app_iter.close()
            sys.stdout = stdout
            myout.close()
        return status_headers[0], status_headers[1], ''.join(body)

    def adjustResponse(self, status, headers, body):
        if "<body>" in body:
            body = self.adjustBody(body)
            # Reset content length header (otherwise client sees truncated page).
            newHeaders = []
            for header in headers:
                if header[0] == 'Content-Length':
                    newHeader = (header[0], str(len(body)))
                    newHeaders.append(newHeader)
                else:
                    newHeaders.append(header)
            headers = newHeaders
        return status, headers, body

    def adjustBody(self, body):
        return body


class TracTickets(WsgiMiddleware):

    def adjustResponse(self, *args, **kwds):
        s, h, b = super(TracTickets, self).adjustResponse(*args, **kwds)
        if 'trac' in self.application.registry.plugins:
            TracTicketFromHeaders(h).execute()
        return s, h, b


class KforgeNavigationBar(WsgiMiddleware):

    barCss = """
div.kforgenav {
position: relative;
top: 0;
bottom: 0;
height: 20px;
z-index: 1000;
width: 100%;
}

.kforgenav ul {
padding: 0;
margin: 0;
list-style: none;
line-height: 1;
cursor: pointer;
height: auto;
}

.kforgenav li {
padding: 0;
margin: 0;
list-style: none;
float: left;
position: relative;
text-align: left;
}

.kforgenav a {
display: block;
padding: 4px 15px 3px;
text-decoration: none;
font-size: 11px;
color: #000;
border: 0;
background: #fff;
}
"""

    def adjustBody(self, body):
        requiredFragments = {
            'gitweb': '<meta name=\"generator\" content=\"gitweb',
            'trac': 'By <a href="http://www.edgewall.org/">Edgewall Software</a>',
            'viewvc': '<meta name=\"generator\" content=\"ViewVC',
        }
        for fragment in requiredFragments.values(): 
            if fragment in body:
                return self.insertNavigationBar(body)
        return body

    def insertNavigationBar(self, body):
        # Prepare the CSS.
        barCss = """<style type="text/css">%s</style>""" % self.barCss
        # Insert the CSS at the end of the HEAD section.
        body = re.sub('</head>', '%s\g<0>' % barCss, body)
        # Prepare the HTML.
        requestUri = self.environ['REQUEST_URI']
        uriPrefix = self.application.dictionary[URI_PREFIX]
        if uriPrefix and requestUri.startswith(uriPrefix):
            requestUri = requestUri.replace(uriPrefix, '', 1)
        requestParts = requestUri.strip('/').split('/')
        requestParts = requestParts[0:2]
        projectName = requestParts[0]
        siteUri = uriPrefix + '/'
        profileUri = uriPrefix + '/people/home/'
        projectsUri = uriPrefix + '/projects/'
        projectUri = uriPrefix + '/projects/%s/' % projectName
        servicesUri = projectUri + 'services/' 
        membersUri = projectUri + 'members/'
        links = [
            (siteUri, self.application.dictionary[SYSTEM_SERVICE_NAME]),
            (profileUri, "Profile"),
            (projectsUri, "Projects"),
            (projectUri, self.application.registry.projects[projectName].title.encode('ascii', 'xmlcharrefreplace')),
            (servicesUri, "Services"),
            (membersUri, "Members"),
        ]
        barHtml = '<div class="kforgenav">'
        barHtml += "<ul>"
        for (url, label) in links:
            barHtml += '<li><a href="%s">%s</a></li>' % (url, label)
        barHtml += '</ul></div>'
        # Insert the HTML at the start of the BODY section.
        body = re.sub('<body[^>]*>', '\g<0>%s' % barHtml, body)
        return body


class WsgiAccessControlHandler(ModWsgiHandler):

    redirectUri = None
    statusMessages = {
        200: "200 OK",
        302: "302 Found",
        401: "401 Unauthorized",
        500: "500 Internal Server Error",
    }

    def __init__(self, application=None):
        if application:
            self.wsgiApplication = TracTickets(KforgeNavigationBar(application))
        else:
            self.wsgiApplication = None
        self.session = None

    def __call__(self, environ, start_response):
        self.environ = environ
        authStatus = self.authorise()
        headers = [
            ("Content-type", "text/html; charset=iso-8859-1"),
        ]
        body = [""]
        if authStatus == HTTP_OK:
            if self.wsgiApplication:
                body = self.wsgiApplication(environ, start_response)
            else:
                body = ["Access was authorised, but there is no protected application."]
                start_response(self.createWsgiStatus(authStatus), headers)
        elif self.isCookieClient():
            if self.redirectUri:
                headers.append(("Location", self.redirectUri))
            start_response(self.createWsgiStatus(authStatus), headers)
        elif authStatus == HTTP_UNAUTHORIZED:
            realm = self.application.dictionary[HTTP_AUTH_REALM]
            realm = realm.encode('utf8')
            headers.append(('WWW-Authenticate', 'Basic realm="%s Restricted Area"' % realm))
            start_response(self.createWsgiStatus(authStatus), headers)
        return body

    def createWsgiStatus(self, code):
        return self.statusMessages[code] if code in self.statusMessages else str(code)

    def authoriseRequest(self):
        if self.isCookieClient():
            if not self.validateRequestUri():
                # Apache configuration should mean we never get here.
                self.setRedirect()
                return HTTP_MOVED_TEMPORARILY
            elif self.isLoginUri():
                self.setRedirect('login')
                return HTTP_MOVED_TEMPORARILY
            elif self.isLogoutUri():
                self.setRedirect('logout')
                return HTTP_MOVED_TEMPORARILY
            self.initAuthuserFromCookie()
            if self.isAccessAuthorised():
                if self.session:
                    self.setRequestUser(self.authuser.name)
                return HTTP_OK
            else:
                self.setRedirect()
                return HTTP_MOVED_TEMPORARILY
        else:
            if not self.validateRequestUri():
                return HTTP_NOT_FOUND
            self.initAuthuserFromDictionary()
            if self.isAccessAuthorised():
                return HTTP_OK
            else:
                if 'HTTP_AUTHORIZATION' in self.environ:
                    self.initAuthuserFromBasicPrompt()
                    if self.isAccessAuthorised():
                        self.setRequestUser(self.authuser.name)
                        return HTTP_OK
                    else:
                        return HTTP_UNAUTHORIZED
                else:
                    return HTTP_UNAUTHORIZED

    def getRequestCredentials(self):
        if 'HTTP_AUTHORIZATION' in self.environ:
            authorization = self.environ['HTTP_AUTHORIZATION']
            (authmeth, auth) = authorization.split(' ', 1)
            if authmeth.lower() != 'basic':
                msg = "Needs basic auth (not '%s')." % authmeth
                raise Exception, msg
            auth = auth.strip().decode('base64')
            username, password = auth.split(':', 1)
            return username, password
        elif self.session:
            return self.session.person.name, None

    def setRequestRedirect(self, uri):
        self.redirectUri = uri

    def setRequestUser(self, userName):
        if type(userName) == unicode:
            userName = userName.encode('utf-8')
        if type(userName) != str:
            userName = str(userName)
        self.environ['REMOTE_USER'] = userName
        
    def hasCookies(self):
        return self.environ.has_key('HTTP_COOKIE')

    def getCookies(self):
        return self.environ['HTTP_COOKIE']


class GitWsgiAccessControlHandler(WsgiAccessControlHandler):

    def getActionName(self):
        uri = self.normalizeUriPath(self.getRequestUri())
        if 'receive-pack' not in uri and 'upload-pack' in uri:
            # Client is doing clone or pull.
            actionName = 'Read'
        elif 'receive-pack' in uri and 'upload-pack' not in uri:
            # Client is doing push.
            actionName = 'Update'
        else:
            if self.getServiceFromUri(uri):
                actionName = super(GitWsgiAccessControlHandler, self).getActionName()
            else:
                raise Exception, "Can't identify action name from request URI: %s" % uri
        return actionName


