from dm.apache.config import ApacheConfigBuilder
from kforge.exceptions import MissingPluginSystem
from kforge.ioc import *
import dm.environment
import kforge.accesscontrol
import dm.environment
import kforge.url
import commands
from kforge.dictionarywords import *

# Todo: Rename simply as ApacheConfig (since that is what it encapsulates).

class ApacheConfigBuilder(ApacheConfigBuilder):
    
    registry = RequiredFeature('DomainRegistry')
    fsPathBuilder = RequiredFeature('FileSystem')
    
    def __init__(self):
        super(ApacheConfigBuilder, self).__init__()
        self.url_scheme = kforge.url.UrlScheme()
    
    def createConfigContent(self):
        # Replace super's method, since we need to add the services in the middle
        # of the two WUI sections. Perhaps refactor so super's method supports
        # extension config or something.
        modWsgiWebuiConfig = self.createModWsgiWebuiConfig()
        modPythonWebuiConfig = self.createModPythonWebuiConfig()
        mediaConfig = self.createMediaConfig()
        servicesConfig = self.createServicesConfig()
        configContents = {
            'modWsgiWebuiConfig': modWsgiWebuiConfig,
            'modPythonWebuiConfig': modPythonWebuiConfig,
            'mediaConfig': mediaConfig,
            'servicesConfig': servicesConfig,
        }
        apacheConfigTmpl = """
####################################################
#
### Auto-generated KForge Apache configuration.
#
####################################################

<IfModule !mod_wsgi.c>
<IfModule mod_python.c>
%(modPythonWebuiConfig)s
</IfModule>
</IfModule>
%(mediaConfig)s
%(servicesConfig)s
<IfModule mod_wsgi.c>
%(modWsgiWebuiConfig)s
</IfModule>

####################################################
#
### END Auto-generated KForge Apache configuration.
#
####################################################
"""
        return apacheConfigTmpl % configContents

    def buildWsgiFile(self):
        super(ApacheConfigBuilder, self).buildWsgiFile()
        for plugin in self.registry.plugins:
            plugin.buildWsgiFile()
   
    def buildCgiFile(self):
        super(ApacheConfigBuilder, self).buildCgiFile()
        for plugin in self.registry.plugins:
            plugin.buildCgiFile()

    def buildLocksDir(self):
        super(ApacheConfigBuilder, self).buildLocksDir()
        for plugin in self.registry.plugins:
            plugin.buildLocksDir()
   
    def getWsgiHandlerModule(self):
        return 'kforge.handlers.kui.wsgi'

    def getModPythonHandlerModuleVirtualenv(self):
        systemName = self.dictionary[SYSTEM_NAME]
        moduleName = '%s.handlers.kui.modpython' % systemName
        return moduleName

    def getWebuiPathPatterns(self):
        paths = '^%s$' % self.url_scheme.url_for('home')
        extraPaths = [
            self.url_scheme.url_for('feed'),
            self.url_scheme.url_for('api'),
            self.url_scheme.url_for('recover'),
            self.url_scheme.url_for('about'),
            self.url_scheme.url_for('access_denied'),
            self.url_scheme.url_for('login'),
            self.url_scheme.url_for('logout'),
            self.url_scheme.url_for('admin'),
            self.url_scheme.url_for('people'),
            self.url_scheme.url_for('projects'),
        ]
        for path in extraPaths:
            paths += '|^%s($|/.*)' % path
        return paths

    def createServicesConfig(self):
        urlBuilder = kforge.url.UrlScheme()
        apacheConfig = self.getEnvironmentVariables()
        apacheConfig += self.getPluginsCommonConfig()
        apacheConfig += """

####################################################
#
### Configuration for project services.
#
"""
        for project in self.registry.projects:
            serviceNames = project.services.keys()
            # Reverse sort names (so shorter names don't mask longer names).
            serviceNames.sort()
            serviceNames.reverse()
            for name in serviceNames:
                service = project.services[name]
                apacheConfig += self.getServiceSection(urlBuilder, service)
        apacheConfig += """
### END Configuration for project services. ########
"""
        return apacheConfig
        
    def getEnvironmentVariables(self):
        configVars = self.getConfigVars()
        apacheConfigTmpl = """

####################################################
#
### Site environment variables.
#

<IfModule !mod_wsgi.c>
<IfModule mod_python.c>
SetEnv RUNNING_IN_MOD_PYTHON True
SetEnv DJANGO_SETTINGS_MODULE kforge.django.settings.main
SetEnv %(CONFIG_ENV_VAR_NAME)s %(SYSTEM_CONFIG_PATH)s
SetEnv PYTHONPATH %(PYTHON_PATH)s
</IfModule>
</IfModule>

### END Site environment variables. ################

        """
        return apacheConfigTmpl % configVars
    
    def getPluginsCommonConfig(self):
        apacheConfig = """

####################################################
#
### Configuration for plugins (common).
#
        """
        for plugin in self.registry.plugins:
            apacheConfig += plugin.getApacheConfigCommon()
        apacheConfig += """

### END Configuration for plugins (common). ########
        """

        return apacheConfig
    
    def getServiceSection(self, urlBuilder, service):
        "Generates Apache config fragment for service."
        uriPrefix = self.dictionary[URI_PREFIX]
        serviceUrl = urlBuilder.getServicePath(service)
        serviceUrlNoPrefix = serviceUrl.replace(uriPrefix, '', 1)
        configVars = {}
        configVars['serviceName'] = service.name
        configVars['projectName'] = service.project.name
        configVars['uriPrefix'] = uriPrefix
        configVars['urlPath'] = serviceUrl
        configVars['urlPathNoPrefix'] = serviceUrlNoPrefix
        configVars['fileSystemPath'] = self.fsPathBuilder.getServicePath(service)
        configVars['modPythonAccessControl'] = self.getModPythonAccessControl()
        configVars['modWsgiAccessControl'] = self.getModWsgiAccessControl()
        pluginSystem = service.plugin.getSystem()
        apacheConfig = """

### Configuration for service: %(projectName)s %(serviceName)s
""" % configVars
        apacheConfig += pluginSystem.getApacheConfig(service, configVars)
        return apacheConfig
    
    def getModWsgiAccessControl(self):
        apacheConfigTmpl = """
AuthType basic
AuthName "%(HTTP_AUTH_REALM)s Restricted Area"
AuthBasicProvider wsgi
WSGIAuthUserScript %(WSGI_SCRIPT_PATH)s
Require valid-user"""
        return apacheConfigTmpl % self.getConfigVars()

    def getModPythonAccessControl(self):
        configVars = self.getConfigVars().copy()
        if self.dictionary[VIRTUALENVBIN_PATH]:
            accessHandlerName = 'kforgevirtualenvhandlers::accesshandler'
            authenHandlerName = 'kforgevirtualenvhandlers::authenhandler'
        else:
            accessHandlerName = 'kforge.handlers.projecthost::accesshandler'
            authenHandlerName = 'kforge.handlers.projecthost::authenhandler'
        configVars['accessHandlerName'] = accessHandlerName
        configVars['authenHandlerName'] = authenHandlerName
        # Using PYTHONOPTION as SetEnv does not seem to work in here.
        # Apache module 'mod_auth_basic.c' only available in apache >= 2.1.
        # See also comments in kforge.handlers.projecthost.
        apacheConfigTmpl = """
PYTHONOPTION DJANGO_SETTINGS_MODULE kforge.django.settings.main
PYTHONOPTION %(CONFIG_ENV_VAR_NAME)s %(SYSTEM_CONFIG_PATH)s
PythonPath "'%(PYTHON_PATH)s'.split(':') + sys.path"
PythonDebug %(PYTHON_DEBUG)s
Satisfy any
PythonAccessHandler %(accessHandlerName)s
PythonAuthenHandler %(authenHandlerName)s
AuthType basic
AuthName "%(HTTP_AUTH_REALM)s Restricted Area"
Require valid-user
<IfModule mod_auth_basic.c>
AuthBasicAuthoritative Off
AuthUserFile /dev/null
</IfModule>
""" 
        return apacheConfigTmpl % configVars

    def createWsgiScriptContent(self):
        content = super(ApacheConfigBuilder, self).createWsgiScriptContent()
        content += """
def check_password(environ, user, password):
    from kforge.handlers.modwsgi import WsgiCheckPasswordHandler
    application = WsgiCheckPasswordHandler()
    return application(environ, user, password)
""" 
        return content

