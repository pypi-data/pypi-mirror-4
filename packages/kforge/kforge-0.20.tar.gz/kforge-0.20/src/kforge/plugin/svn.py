"""KForge Subversion Plugin

Enabling this plugin allows KForge project administrators to create Subversion version control system services.

Creating services with this plugin requires:

  * Subversion. The 'svnadmin' command is used to create repositories.

Providing access to this plugin's services requires:

  * Apache. The mod_python, mod_dav, mod_dav_fs, and mod_dav_svn Apache modules are used to provide access to Subversion through Apache. For example, on Debian the libapache2-mod-python and libapache2-svn packages must be installed and enabled.

You do not need to add anything to the KForge config file.

You can enable, disable, and show status in the usual way.

  $ kforge-admin plugin enable svn
  $ kforge-admin plugin show svn
  $ kforge-admin plugin disable svn
"""
import kforge.plugin.base
import kforge.utils.backup
from kforge.dictionarywords import *
from kforge.plugin.ssh import SSH_USER_NAME
from kforge.plugin.ssh import SSH_HOST_NAME
from kforge.plugin.base import dictionary, setWord
import os
import commands
import shutil

SVN_ADMIN_SCRIPT = ExecutableFileSetting('svn.admin_script', umask=0o22)
SVN_WSGI_SCRIPT_PATH = WsgiScriptSetting('svn.wsgi_script')
SVN_WSGI_PROCESS_GROUP = StringSetting('svn.wsgi_process_group')
SVN_CGI_SCRIPT_PATH = CgiScriptSetting('svn.cgi_script')
SVN_VIEWVC_IS_ENABLED = StringSetting('svn.enable_viewvc')
SVN_VIEWVC_LIB_PATH = DirSetting('svn.viewvc_lib')
SVN_VIEWVC_MEDIA_PATH = DirSetting('svn.viewvc_media_dir')
SVN_VIEWVC_TEMPLATE_PATH = DirSetting('svn.viewvc_template_dir')
defaultWsgiScript = os.path.join(dictionary[FILESYSTEM_PATH], 'wsgi', 'svn.wsgi')
defaultCgiScript = os.path.join(dictionary[FILESYSTEM_PATH], 'cgi', 'svn.cgi')
setWord(SVN_ADMIN_SCRIPT, '/usr/bin/svnadmin')
setWord(SVN_WSGI_SCRIPT_PATH, defaultWsgiScript)
setWord(SVN_WSGI_PROCESS_GROUP, dictionary[WSGI_PROCESS_GROUP])
setWord(SVN_CGI_SCRIPT_PATH, defaultCgiScript)
setWord(SVN_VIEWVC_IS_ENABLED, '')
setWord(SVN_VIEWVC_LIB_PATH, '/usr/lib/viewvc/lib')
setWord(SVN_VIEWVC_MEDIA_PATH, '/usr/share/viewvc/docroot')
setWord(SVN_VIEWVC_TEMPLATE_PATH, '/etc/viewvc/templates')


class Plugin(kforge.plugin.base.ServicePlugin):
    "Subversion plugin."

    settings = [SVN_ADMIN_SCRIPT, SVN_WSGI_SCRIPT_PATH,
        SVN_WSGI_PROCESS_GROUP, SVN_CGI_SCRIPT_PATH, SVN_VIEWVC_IS_ENABLED,
        SVN_VIEWVC_LIB_PATH, SVN_VIEWVC_MEDIA_PATH, SVN_VIEWVC_TEMPLATE_PATH]
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        self.utils = SvnUtils(umask=self.dictionary.getUmask())
   
    def checkDependencies(self):
        errors = []
        svnadminPath = self.dictionary[SVN_ADMIN_SCRIPT]
        cmd = 'which %s' % svnadminPath
        (status, output) = commands.getstatusoutput(cmd) 
        if status:
            errors.append("Couldn't find Subversion admin script '%s' on path." % svnadminPath)
        if self.dictionary[SVN_VIEWVC_IS_ENABLED]:
            if not os.path.isdir(self.dictionary[SVN_VIEWVC_LIB_PATH]):
                errors.append("Couldn't find ViewVC library: %s" % self.dictionary[SVN_VIEWVC_LIB_PATH])
            if not os.path.isdir(self.dictionary[SVN_VIEWVC_TEMPLATE_PATH]):
                errors.append("Couldn't find ViewVC templates: %s" % self.dictionary[SVN_VIEWVC_TEMPLATE_PATH])
            if not os.path.isdir(self.dictionary[SVN_VIEWVC_MEDIA_PATH]):
                errors.append("Couldn't find ViewVC static media: %s" % self.dictionary[SVN_VIEWVC_MEDIA_PATH])
        return errors

    def showDepends(self):
        svnadminPath = self.dictionary[SVN_ADMIN_SCRIPT]
        cmd = 'which %s' % svnadminPath
        (statusWhichSvnadmin, outputWhichSvnadmin) = commands.getstatusoutput(cmd) 

        depends = [
            "Subversion admin: %s" % (statusWhichSvnadmin and "Not found!" or ("Found OK. %s" % outputWhichSvnadmin)),
        ]
        if self.dictionary[SVN_VIEWVC_IS_ENABLED]:
            hasViewvcLibrary= os.path.isdir(self.dictionary[SVN_VIEWVC_LIB_PATH])
            hasViewvcTemplate = os.path.isdir(self.dictionary[SVN_VIEWVC_TEMPLATE_PATH])
            hasViewvcMedia = os.path.isdir(self.dictionary[SVN_VIEWVC_MEDIA_PATH])
            depends.extend([
                "ViewVC library: %s" % (hasViewvcLibrary and ("Found OK. %s" % self.dictionary[SVN_VIEWVC_LIB_PATH]) or "Not found!"),
                "ViewVC template: %s" % (hasViewvcTemplate and ("Found OK. %s" % self.dictionary[SVN_VIEWVC_TEMPLATE_PATH]) or "Not found!"),
                "ViewVC media: %s" % (hasViewvcMedia and ("Found OK. %s" % self.dictionary[SVN_VIEWVC_MEDIA_PATH]) or "Not found!"),
            ])
        depends.extend([
            "Apache dav module: %s" % "Please check this module is enabled.",
            "Apache dav_fs module: %s" % "Please check this module is enabled.",
            "Apache dav_svn module: %s" % "Please check this module is enabled.",
        ])
        return depends
    showDepends = classmethod(showDepends)
 
    def onServiceCreate(self, service):
        if self.isOurs(service):
            servicePath = self.paths.getServicePath(service)
            msg = 'SvnPlugin: Creating new Subversion repository for %s: %s' % (
                service, servicePath
            )
            self.logger.info(msg)
            self.paths.assertServiceFolder(service)
            self.utils.createRepository(servicePath)
            self.buildAndReloadApacheConfig()

    def getApacheConfig(self, service, configVars):
        apacheConfigTmpl = '\n'
        configVars['serviceName'] = service.name
        configVars['projectName'] = service.project.name
        if self.dictionary[SVN_VIEWVC_IS_ENABLED]:
            configVars['viewvcWsgiScriptPath'] = self.dictionary[SVN_WSGI_SCRIPT_PATH]
            configVars['viewvcCgiScriptPath'] = self.dictionary[SVN_GGI_SCRIPT_PATH]
            viewvcServicePath =  "%(uriPrefix)s/%(projectName)s/viewvc/%(serviceName)s" % configVars
            configVars['viewvcServicePath'] = viewvcServicePath
            configVars['svnWsgiProcessGroup'] = self.dictionary[SVN_WSGI_PROCESS_GROUP]
            configVars['viewvcMediaFolder'] = self.dictionary[SVN_VIEWVC_MEDIA_PATH]
            # Want to do: <LocationMatch ^%(urlPath)s(!?viewvc)> but mod_dav_svn gets the paths wrong.
            apacheConfigTmpl += """
AliasMatch ^%(uriPrefix)s/%(projectName)s/viewvc\/\*docroot\*((?!%(serviceName)s).*) %(viewvcMediaFolder)s$1

<IfModule mod_wsgi.c>
WSGIScriptAlias %(uriPrefix)s/%(projectName)s/viewvc %(viewvcWsgiScriptPath)s
WSGIApplicationGroup %%{GLOBAL}
WSGIProcessGroup %(svnWsgiProcessGroup)s
</IfModule>

<IfModule !mod_wsgi.c>
<IfModule mod_python.c>
ScriptAlias %(viewvcServicePath)s %(viewCgiScriptpath)s
</IfModule>
</IfModule>

<IfModule mod_rewrite.c>
RewriteEngine on
RewriteCond %%{HTTP_USER_AGENT}  Lynx               [OR]
RewriteCond %%{HTTP_USER_AGENT}  Mozilla            [OR]
RewriteCond %%{HTTP_USER_AGENT}  Links              [OR]
RewriteCond %%{HTTP_USER_AGENT}  w3m
RewriteRule ^%(urlPath)s$       %(viewvcServicePath)s/  [R,L]
</IfModule>

<IfModule mod_wsgi.c>
<Location %(viewvcServicePath)s>
SetEnv KFORGE_SVN_REPO_PATH %(fileSystemPath)s
SetEnv KFORGE_SVN_SERVICE_NAME %(serviceName)s
WSGIPassAuthorization On
</Location>
</IfModule>

<IfModule !mod_wsgi.c>
<IfModule mod_python.c>
<Location %(viewvcServicePath)s>
SetEnv KFORGE_SVN_REPO_PATH %(fileSystemPath)s
SetEnv KFORGE_SVN_SERVICE_NAME %(serviceName)s
%(modPythonAccessControl)s
</Location>
</IfModule>
</IfModule>
"""
            apacheConfigTmpl += viewvcConfigTmpl
        # Add configuration for DAV Svn.
        apacheConfigTmpl += """
<IfModule mod_dav.c>
<IfModule mod_dav_svn.c>
<IfModule mod_wsgi.c>
<Location %(urlPath)s>
DAV svn 
SVNPath %(fileSystemPath)s
# Prefer mod_python access control (avoids unnecessary prompt).
<IfModule mod_python.c>
# Don't cache the model in mod_python since Web UI is running in mod_wsgi.
PYTHONOPTION AVOID_ENABLING_MODEL_CACHE True
%(modPythonAccessControl)s
</IfModule>
<IfModule !mod_python.c>
%(modWsgiAccessControl)s
</IfModule>
</Location>
</IfModule>
<IfModule !mod_wsgi.c>
<IfModule mod_python.c>
<Location %(urlPath)s>
DAV svn 
SVNPath %(fileSystemPath)s
%(modPythonAccessControl)s
</Location>
</IfModule>
</IfModule>
</IfModule>
</IfModule>
"""
        return apacheConfigTmpl % configVars

    def buildWsgiFile(self):
        path = self.dictionary[SVN_WSGI_SCRIPT_PATH]
        content = self.createWsgiScriptContent()
        purpose = 'Subversion WSGI script'
        self.filesystem.writeFileIfChanged(path, content, purpose)

    def createWsgiScriptBody(self, pythonPathActivation):
        viewvcLibPath = self.dictionary[SVN_VIEWVC_LIB_PATH]
        viewvcTemplatePath = self.dictionary[SVN_VIEWVC_TEMPLATE_PATH]
        wsgiScriptBody = """
# KForge auto-generated Svn (ViewVC) WSGI File.

import os
import sys

import sys, os

LIBRARY_DIR = r'""" + viewvcLibPath + """'
CONF_PATHNAME = None

sys.path.insert(0, LIBRARY_DIR)

import sapi
import viewvc


""" + pythonPathActivation + """

os.environ['KFORGE_SETTINGS'] = '""" + self.dictionary[SYSTEM_CONFIG_PATH] + """'

from kforge.handlers.modwsgi import WsgiAccessControlHandler

def dispatch_viewvc_request(environ, start_response):
    server = sapi.WsgiServer(environ, start_response)
    cfg = viewvc.load_config(CONF_PATHNAME, server)
    cfg.options.template_dir = r'"""+viewvcTemplatePath+"""'
    repositoryPath = environ.pop('KFORGE_SVN_REPO_PATH')
    serviceName = environ.pop('KFORGE_SVN_SERVICE_NAME')
    cfg.general.svn_roots = {serviceName: repositoryPath}
    cfg.options.svn_roots = {serviceName: repositoryPath}
    cfg.options.allowed_views.append('co')

    #cfg.conf_path = ' ' # Stops the viewvc's "hack_..." method failing. :-)
    cfg.options.hide_cvs_root = 1
    viewvc.main(server, cfg)
    return []

def application(environ, start_response):
    access_control = WsgiAccessControlHandler(dispatch_viewvc_request)
    return access_control(environ, start_response)
"""
        return wsgiScriptBody

    def buildCgiFile(self):
        path = self.dictionary[SVN_CGI_SCRIPT_PATH]
        content = self.createCgiScriptContent()
        purpose = 'Subversion CGI script'
        self.filesystem.writeCgiFile(path, content, purpose)

    def createCgiScriptContent(self):
        # Todo: Fixup so it uses virtualenv or PYTHONPATH, if they exist.
        viewvcLibPath = self.dictionary[SVN_VIEWVC_LIB_PATH]
        viewvcTemplatePath = self.dictionary[SVN_VIEWVC_TEMPLATE_PATH]
        pythonBinPath = "/usr/bin/env python"
        if self.dictionary[VIRTUALENVBIN_PATH]:
            pythonBinPath = os.path.join(self.dictionary[VIRTUALENVBIN_PATH], 'python')
        cgiScriptContent = '''#!'''+pythonBinPath+'''

LIBRARY_DIR = r"'''+viewvcLibPath+'''"

#########################################################################
#
# Adjust sys.path to include our library directory
#

import sys
import os

if LIBRARY_DIR:
    sys.path.insert(0, LIBRARY_DIR)


repositoryPath = os.environ.pop('KFORGE_SVN_REPO_PATH')
serviceName = os.environ.pop('KFORGE_SVN_SERVICE_NAME')

import sapi
import viewvc

server = sapi.CgiServer()
cfg = viewvc.load_config(None, server)
cfg.options.template_dir = r"'''+viewvcTemplatePath+'''"
cfg.general.svn_roots = {serviceName: repositoryPath}
cfg.options.svn_roots = {serviceName: repositoryPath}
cfg.options.hide_cvs_root = 1
viewvc.main(server, cfg)

'''
        return cgiScriptContent

    def getUserHelp(self, service, serviceLocation):
        values = {'httpUrl' : serviceLocation}
        if 'ssh' in self.registry.plugins:
            sshUrl = 'svn+ssh://%(sshUser)s@%(sshHost)s/%(project)s/%(service)s'
            sshUrl %= {
                'sshUser': self.dictionary[SSH_USER_NAME],
                'sshHost': self.dictionary[SSH_HOST_NAME],
                'project': service.project.name,
                'service': service.name
            }
            values['sshUrl'] = sshUrl
        helpMessage = '''
<p>This service provides a single Subversion repository. To find out more about <a href="http://subversion.tigris.org/">Subversion</a> see the <a href="http://svnbook.red-bean.com/">Subversion book</a>.</p>
<p>You can access the material in the repository the following ways (provided you have sufficient permission):</p>
<ul>
    <li>Browse the repository with your favorite Web browser.</li>
    <li>Access the repository with a suitable Subversion client via HTTP.</li>'''
        if 'ssh' in self.registry.plugins:
            helpMessage +='''
    <li>Access the repository with a suitable Subversion client via SSH.</li>'''
        helpMessage += '''
</ul>

<p>For more information on the command line client see the Subversion book (chapter 3). Alternatively there is <a href="http://tortoisesvn.tigris.org/">Tortoise SVN</a>, a GUI client that integrates with Windows explorer. It has a <a href="http://tortoisesvn.net/doc_release">detailed manual</a> with chapter 5 covering 'daily use' -- checking out, committing etc.</p>

<h4>HTTP Access</h4>
<p>The repository is available via HTTP here:
<b><pre>%(httpUrl)s

</pre></b></p>
<p>If you are using the command line client, you would do:
<pre>$ svn checkout %(httpUrl)s --username username

</pre></p>

'''
        if 'ssh' in self.registry.plugins:
            helpMessage +='''
<h4>SSH Access</h4>
<p>The repository is available via SSH here:
<b><pre>%(sshUrl)s

</pre></b></p>
<p>Firstly, register your SSH public key with your account.</p>
<p>If you are using the command line client, you would do:
<pre>$ svn checkout %(sshUrl)s

</pre>
</p>

'''
        msg = helpMessage % values
        return msg


    def backup(self, service, backupPathBuilder):
        backupPath = backupPathBuilder.getServicePath(service)
        backupItem = kforge.utils.backup.BackupItemSvn(
            backupPath, '', service.getDirPath()
        )
        backupItem.doBackup()


class SvnUtils(object):
    
    def __init__(self, parentPath='', umask=0o077):
        """
        @parentPath: string representing parent path to use when creating
                     repositories. If not defined then defaults to empty string
                     (so repositories must be specified with their path)
        """
        # NB: Only used in svntest.py.
        # Todo: Either move test path switching to dictionary manipulations, or create subclass in test unit and test that.
        self.parentPath = parentPath  
        self.umask = umask
   
    def createRepository(self, path):
        """
        Creates repository with correct permissions.
        @path: a path to use for repository creation. If absolute it is used on 
               its own and if relative it is joined to parentPath defined at
               creation of class.
        """
        path = self.getRepositoryPath(path)
        type = 'fsfs'
        cmd = 'svnadmin create %s --fs-type %s' % (path, type)
        status, output = commands.getstatusoutput(cmd)
        if status:
            raise Exception('Subversion command error: %s: %s' % (cmd, output))
        # Make the rep-cache.db file group writable since svnadmin doesn't.
        repCachePath = '%s/db/rep-cache.db' % (path)
        if os.path.exists(repCachePath):
            os.chmod(repCachePath, 0660 & ~ self.umask)

    def deleteRepository(self, path):
        """
        Destroys Subversion repository file system.
        @path: see definition of path for createRepository
        """
        fullPath = self.getRepositoryPath(path)
        if os.path.exists(fullPath):
            shutil.rmtree(fullPath)

    # NB: Only used when parentPath != '' in test.
    # Todo: Remove this function, it's distracting. :-)
    def getRepositoryPath(self, name):
        "Returns file system path from repository name."
        path = os.path.join(self.parentPath, name)
        return path
    

