from kforge.handlers.base import *
from kforge.handlers.apachecodes import *

class ModPythonHandler(BaseHandler):
    """
    Responsible for authentication and access control based upon session
    cookies, and for redirecting to the KForge login page or deferring control
    to the authen handler if access is not allowed, for clients which do 
    support cookies (such as Mozilla, Lynx, etc.).

    """

    def __init__(self, request):
        self.request = request
        self.authuser = None
        self.application = None

    def initRequestVars(self):
        self.request.add_common_vars()

    def getRequestEnvironVar(self, name):
        return self.request.get_options().get(name, '')

    def authoriseRequest(self):
        return DEFER_OR_DENY

    def getDefaultResponseCode(self):
        return DONE

    def getRequestUri(self):
        return self.request.uri

    def getRefererUri(self):
        referer = ''
        if self.request.headers_in.has_key('referer'):
            referer = self.request.headers_in['referer']
        return referer

    def getRequestMethod(self):
        return self.request.method

    def getRequestCredentials(self):
        username = self.request.user
        password = self.request.get_basic_auth_pw()
        return (username, password)

    def setRequestUser(self, userName):
        if type(userName) == unicode:
            userName = userName.encode('utf-8')
        if type(userName) != str:
            userName = str(userName)
        self.request.user = userName
        
    def setRequestRedirect(self, uri):
        self.request.err_headers_out.add('Location', uri)
        self.request.status = HTTP_MOVED_TEMPORARILY
        self.request.write("\n")

    def getRequestUserAgent(self):
        return self.request.subprocess_env.get('HTTP_USER_AGENT', '')

    def hasCookies(self):    
        return self.request.headers_in.has_key('Cookie')

    def getCookies(self):    
        return self.request.headers_in['Cookie']


class PythonAccessHandler(ModPythonHandler):
    """
    Responsible for authentication of and access control based upon
    credentials supplied through the 'Basic' password prompt for clients
    which don't support cookies (such as DAV, SVN, etc.).
    
    """

    def __init__(self, *args, **kwds):
        super(PythonAccessHandler, self).__init__(*args, **kwds)
        self.session = None

    def authoriseRequest(self):
        if self.isCookieClient():
            if not self.validateRequestUri():
                self.setRedirect()
                return DONE
            elif self.isLoginUri():
                self.setRedirect('login')
                return DONE
            elif self.isLogoutUri():
                self.setRedirect('logout')
                return DONE
            self.initAuthuserFromCookie()
            if self.isAccessAuthorised():
                if self.session:
                    # Set request.user only under above conditions.
                    self.setRequestUser(self.authuser.name)
                return STOP_AND_APPROVE
            else:
                self.setRedirect()
                return DONE
        else:
            if not self.validateRequestUri():
                return DONE
            self.initAuthuserFromDictionary()
            if self.isAccessAuthorised():
                return STOP_AND_APPROVE
            else:
                return DEFER_OR_DENY


class PythonAuthenHandler(ModPythonHandler):

    def authoriseRequest(self):
        if not self.validateRequestUri():
            return STOP_AND_DENY
        if self.isCookieClient():
            self.logDebug("Cookie clients shouldn't get here.")
            return STOP_AND_DENY
        self.initAuthuserFromBasicPrompt()
        if self.isAccessAuthorised():
            return STOP_AND_APPROVE
        else:
            return DEFER_OR_DENY

