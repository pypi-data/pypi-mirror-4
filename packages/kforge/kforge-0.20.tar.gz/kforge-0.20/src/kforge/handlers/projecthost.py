from kforge.handlers.modpython import PythonAccessHandler
from kforge.handlers.modpython import PythonAuthenHandler
from kforge.handlers.apachecodes import *

# Todo: Refactor these long doc strings, now the method has been established.

class ProjectAccessHandler(PythonAccessHandler):
    """
    Responsible for authentication and access control based upon session
    cookies, and for redirecting to the KForge login page or deferring control
    to the authen handler if access is not allowed, for clients which do 
    support cookies (such as Mozilla, Lynx, etc.).
    
    Note Well: To statisfy Apache's 'Satisfy any' condition, thereby stopping
    further handling of the mod_python request (so that e.g. a basic auth
    dialog prompt is not raised in a user's browser for allowed visitor access
    to controlled application services) mod_python access handlers, such as
    this one, must return OK (integer value of 0) from the authorise() method.
    Returning HTTP_OK (200) does not have the same effect, and further
    access control handlers may be triggered wrongly.

    To stop handlers and make sure no other handler is called, return DONE (-2)
    and write at least one character to the request ("request.write()").


    Redirect from an Authen Handler
    -------------------------------

    If a handler returns DONE, so that no further handlers will be called,
    then the HTTP response code can be set by setting the 'status'
    attribute on the request object received by the handler.

        self.request.status = HTTP_FORBIDDEN
        self.request.write('\n')
        return DONE

    For example, to redirect and be the last handler in a 'Satisfy any'
    condition, set the Location in the error headers, set the status to
    code HTTP_MOVED_TEMPORARILY, and then return OK:

        self.request.err_headers_out.add('Location', redirectUri)
        self.request.status = HTTP_MOVED_TEMPORARILY
        self.request.write('\n')
        return DONE

    This can be used in an Apache AccessHandler to avoid the 'Basic' prompt:

        Satisfy any
        Require valid-user
        PythonAccessHandler myhandlers::accesshandler  # method to redirect
        PythonAuthenHandler myhandlers::authenhandler
        AuthType Basic
        AuthName "%s Restricted Area"

    """

    pass


class ProjectAuthenHandler(PythonAuthenHandler):
    """
    Responsible for authentication of and access control based upon
    credentials supplied through the 'Basic' password prompt for clients
    which don't support cookies (such as DAV, SVN, etc.).
    
    """

    pass

def accesshandler(request):
    handler = ProjectAccessHandler(request)
    return handler.authorise()
        
def authenhandler(request):
    handler = ProjectAuthenHandler(request)
    return handler.authorise()
 
