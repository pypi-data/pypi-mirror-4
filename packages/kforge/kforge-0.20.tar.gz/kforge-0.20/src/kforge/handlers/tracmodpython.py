from trac.web.modpython_frontend import *
from kforge.handlers.modpython import ModPythonHandler

class TracModPythonHandler(ModPythonHandler):

    def __init__(self, request, options):
        super(TracModPythonHandler, self).__init__(request)
        self.options = options

    def run(self, application):
        gateway = ModPythonGateway(self.request, self.options)
        gateway.run(application)
        self.initHandler()
        from kforge.handlers.tracticket import TracTicketFromHeaders
        status, headers = gateway.headers_sent
        TracTicketFromHeaders(headers).execute()

# The rest of this file uses a modified version of the handler function in
# from trac/web/modpython_frontend.py, so that we can use an extended version
# of Trac's ModPythonGateway, without which it isn't possible to read the response
# headers, which are needed to spot when a ticket has been created or updated, and
# to get its ID.

_first = True
_first_lock = threading.Lock()

def handler(req):
    global _first
    try:
        _first_lock.acquire()
        if _first:
            _first = False
            options = req.get_options()
            egg_cache = options.get('PYTHON_EGG_CACHE')
            if not egg_cache and options.get('TracEnv'):
                egg_cache = os.path.join(options.get('TracEnv'), '.egg-cache')
            if not egg_cache and options.get('TracEnvParentDir'):
                egg_cache = os.path.join(options.get('TracEnvParentDir'), '.egg-cache')
            if not egg_cache and req.subprocess_env.get('PYTHON_EGG_CACHE'):
                egg_cache = req.subprocess_env.get('PYTHON_EGG_CACHE')
            if egg_cache:
                pkg_resources.set_extraction_path(egg_cache)
            reload(sys.modules['trac.web'])
    finally:
        _first_lock.release()
    pkg_resources.require('Trac==%s' % VERSION)
    gateway = TracModPythonHandler(req, req.get_options())
    from trac.web.main import dispatch_request
    gateway.run(dispatch_request)
    return apache.OK

