import os
from kforge.dictionarywords import *
from kforge.command import PersonRead
from kforge.url import UrlScheme
from kforge.exceptions import KforgeRegistryKeyError
import Cookie
import traceback
#import urllib2

class GetServiceFromUri(object):

    def __init__(self, uri):
        self.uri = uri
        import kforge.soleInstance
        self.application = kforge.soleInstance.application

    def execute(self):
        (projectName, serviceName) = UrlScheme().decodeServicePath(self.uri)
        try:
            project = self.application.registry.projects[projectName]
        except KforgeRegistryKeyError:
            return None
        try:
            service = project.services[serviceName]
        except KforgeRegistryKeyError:
            return None
        return service


class BaseHandler(object):

    cookieClientIdentifiers = ['Mozilla', 'Links', 'Lynx', 'w3m'] 

    def isCookieClient(self):
        "True if client supports cookies and redirection."
        # Check for cookie header in request.
        if self.hasCookies():
            return True
        # Otherwise look at user agent header in request.
        userAgent = self.getRequestUserAgent()
        isCookieClient = False
        for identifier in self.cookieClientIdentifiers:
            if identifier in userAgent:
                isCookieClient = True
                break
        if self.application.debug:
            if isCookieClient:
                self.logDebug('Cookie client making request.')
            else:
                self.logDebug('Basic client making request.')
            self.logDebug('User-Agent: %s' % userAgent)
        return isCookieClient

    def authorise(self):
        try:
            self.initHandler()
            message = 'Handling access control check: %s %s' % (
                self.getRequestMethod(),
                self.getRequestUri(),
            )
            self.logInfo(message)
            status = self.authoriseRequest()
        except Exception, inst:
            msg = "Failed to complete authorise() method: %s\n" % repr(inst)
            msg += traceback.format_exc()
            try:
                self.logError(msg)
            except:
                raise Exception, "Couldn't log error message: %s" % msg
            if self.isCookieClient():
                # Todo: Redirect with an error message to 'sorry' page.
                self.setRequestRedirect('/')
            status = self.getDefaultResponseCode()
        self.logInfo('Returning with status code: %s' % status)
        return status

    def authoriseRequest(self):
        raise Exception, "Method not implemented on %s" % self.__class__

    def isAccessAuthorised(self):
        self.accessStatus = False
        uri = self.normalizeUriPath(self.getRequestUri())
        service = self.getServiceFromUri(uri)
        if service:
            self.logDebug('Service for path: %s' % service)
            actionName = self.getActionName()
            self.accessStatus = self.application.accessController.isAccessAuthorised(
                person=self.authuser,
                actionName=actionName,
                protectedObject=service.plugin,
                project=service.project,
            )
        else:
            self.logDebug('No service for path: %s' % uri)
        return self.accessStatus

    def initHandler(self):
        self.accessStatus = False
        self.initEnviron()
        self.initApplication()
        self.initRequestVars()

    def initEnviron(self):
        # Set environ from configured request options (SetEnv doesn't work).
        for name in ['KFORGE_SETTINGS', 'DJANGO_SETTINGS_MODULE', 'AVOID_ENABLING_MODEL_CACHE']:
            if name not in os.environ:
                os.environ[name] = self.getRequestEnvironVar(name)

    def initApplication(self):
        import kforge.soleInstance
        self.application = kforge.soleInstance.application

    def initRequestVars(self):
        pass

    def validateRequestUri(self):
        return self.validateUri(self.getRequestUri())

    def validateUri(self, uri):
        "True if location has at least one directories."
        uri = self.normalizeUriPath(uri)
        if len(uri.split('/')) >= 2:
            self.logDebug('Valid request path: %s' % uri)
            return True
        else:
            self.logInfo('Invalid request path: %s' % uri)
            return False
   
    def getRequestUri(self):
        raise Exception, "Method not implemented on %s" % self.__class__

    def getRefererUri(self):
        raise Exception, "Method not implemented on %s" % self.__class__

    def getRequestMethod(self):
        raise Exception, "Method not implemented on %s" % self.__class__

    def getRequestCredentials(self):
        raise Exception, "Method not implemented on %s" % self.__class__

    def getRequestEnvironVar(self, name):
        raise Exception, "Method not implemented on %s" % self.__class__

    def setRequestRedirect(self, name):
        raise Exception, "Method not implemented on %s" % self.__class__

    def getDefaultResponseCode(self):
        raise Exception, "Method not implemented on %s" % self.__class__

    def getRequestUserAgent(self):
        raise Exception, "Method not implemented on %s" % self.__class__

    def isLoginUri(self):
        urlPath = self.normalizeUriPath(self.getRequestUri())
        # Todo: Improve this condition, so it doesn't match eg. template file called login.html in a repository.
        return 'login' in urlPath.split('/')[-1]

    def isLogoutUri(self):
        urlPath = self.normalizeUriPath(self.getRequestUri())
        # Todo: Improve this condition, so it doesn't match eg. template file called logout.html in a repository.
        return 'logout' in urlPath.split('/')[-1]

    def normalizeUriPath(self, uri):
        "Removes trailing slash."
        if uri[-1] == '/':
            uri = uri[:-1]
        # Hack to cope with mod_dav or mod_dav_svn getting PATH_INFO from 
        # LocationMatch in a twist.
        uri = uri.replace('/viewvc/', '/', 1)
        return uri

    def getServiceFromUri(self, uri):
        return GetServiceFromUri(uri).execute()

    def getActionName(self):
        readList = ['GET', 'PROPFIND', 'OPTIONS', 'REPORT']
        if self.getRequestMethod() in readList:
            return 'Read'
        else:
            return 'Update'

    def initAuthuserFromCookie(self):
        self.authuser = None
        authCookieValue = self.getAuthCookieValue()
        if authCookieValue:
            if self.application.debug:
                self.logDebug('Cookie: %s' % authCookieValue)
            import dm.view.base
            view = dm.view.base.ControlledAccessView(None)
            view.setSessionFromCookieString(authCookieValue)
            if view.session:
                self.session = view.session
                self.authuser = self.session.person
            else:
                self.initAuthuserFromDictionary()
        else:
            if self.application.debug:
                self.logDebug('No session cookie in request.')
            self.initAuthuserFromDictionary()
        
    def getAuthCookieValue(self):
        authCookieName = self.application.dictionary[AUTH_COOKIE_NAME]
        return self.getCookieValue(authCookieName)

    def getCookieValue(self, cookieName):
        "Retrieves named cookie."
        if self.hasCookies():
            cookies = Cookie.SimpleCookie()
            cookies.load(self.getCookies())
            if cookies.has_key(cookieName):
                return cookies[cookieName].value
        return ''
       
    def hasCookies(self):
        raise Exception, "Method not implemented on %s" % self

    def getCookies(self):
        raise Exception, "Method not implemented on %s" % self

    def initAuthuserFromBasicPrompt(self):
        personName, password = self.getRequestCredentials()
        if self.application.debug:
            msg = "Authenticating basic auth credentials for '%s'." % personName
            self.logDebug(msg)
        # Todo: Sort this urlpermission confusion out.
        import kforge.apache.urlpermission as accessController
        self.authuser = accessController.isAuthenticated(personName, password)
        if self.authuser:
            msg = "Authenticated basic auth credentials for '%s'." % self.authuser
            self.logDebug(msg)
        else:
            self.initAuthuserFromDictionary()
            msg = "Could not authenticate basic auth credentials for '%s'. Assuming default auth user '%s'." % (personName, self.authuser)
            self.logDebug(msg)

    def initAuthuserFromDictionary(self):
        read = PersonRead(self.application.dictionary[VISITOR_NAME])
        read.execute()
        self.authuser = read.person

    def setRedirect(self, locationName=None):
        try:
            import kforge.url
            urlScheme = kforge.url.UrlScheme()
            if not locationName:
                if self.session:
                    locationName = 'access_denied'
                else:
                    locationName = 'login'
            pageUri = urlScheme.url_for(locationName) 
            if pageUri[-1] != '/':
                pageUri += '/'
            redirectUri = pageUri
            requestUri = self.getRequestUri()
            # Todo: Find out which paths need this trailing slash and fix them.
            #if requestUri[-1] != '/':
            #    requestUri += '/'
            refererUri = self.getRefererUri()
            if refererUri and '/login' in requestUri:
                # Plan on returning to referer [sic] if requested a login page.
                returnUri = refererUri
            else:
                # Otherwise plan on returning to the currently requested page.
                returnUri = requestUri
            # Don't return to a login page.
            returnUri = returnUri.replace('/login', '')
            # Don't pass any POST data forward.
            redirectUri += "?returnPath=%s" % returnUri
            self.logInfo('Redirecting to %s.' % redirectUri)
            self.setRequestRedirect(redirectUri)
        except Exception, inst:
            msg = "Couldn't set redirect: %s" % repr(inst)
            self.logError(msg)
            raise

    def logInfo(self, message):
        self.application.logger.info(self.prefixLogMessage(message))

    def logDebug(self, message):
        self.application.logger.debug(self.prefixLogMessage(message))

    def logError(self, message):
        self.application.logger.error(self.prefixLogMessage(message))

    def prefixLogMessage(self, message):
        return "%s: %s" % (self.__class__.__name__, message)

