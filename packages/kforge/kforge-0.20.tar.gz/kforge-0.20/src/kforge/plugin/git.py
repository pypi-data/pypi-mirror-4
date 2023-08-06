"""KForge Git plugin.

Enabling this plugin allows KForge project administrators to create Git
services.

Creating services with this plugin requires:

  * Git. The 'git' command is used to create repositories (supplied by the 'git-core' package on Debian).

Providing access to this plugin's services requires:

  * Apache. The mod_python or mod_wsgi Apache modules are used to provide access to Git through Apache. For example, on Debian the libapache2-mod-python or libapache2-mod-wsgi must be installed and enabled.

Using Git repositories with Trac projects (optional) requires:

  * Trac's Git plugin. For example, on Debian the trac-git package can be installed.

There are various configuration options (see KForge configuration file). For
example, if the directory for "static" git files is not located at
'/usr/share/gitweb/static' then you may need to change this path to be
'/usr/share/gitweb' instead. This is one difference between Ubuntu and Debian.

You can enable, disable, and show status in the usual way.

  $ kforge-admin plugin enable git
  $ kforge-admin plugin show git
  $ kforge-admin plugin disable git
"""
# Todo: Fix the helpMessage so it's https when necessary.
from kforge.dictionarywords import *
import kforge.plugin.base
from kforge.plugin.ssh import SSH_USER_NAME
from kforge.plugin.ssh import SSH_HOST_NAME
import os
import commands

# Dictionary words.
from kforge.plugin.base import dictionary, setWord
GIT_ADMIN_SCRIPT = ExecutableFileSetting('git.admin_script', umask=0o22)
GIT_HTTP_BACKEND_SCRIPT = ExecutableFileSetting('git.http_backend_script', umask=0o22)
GIT_GITWEB_SCRIPT = ExecutableFileSetting('git.gitweb_script', umask=0o22)
GIT_GITWEB_STATIC = DirSetting('git.gitweb_static')
GIT_WSGI_SCRIPT_PATH = WsgiScriptSetting('git.wsgi_file')
GIT_WSGI_PROCESS_GROUP = 'git.wsgi_process_group'
defaultAdminScript = '/usr/bin/git'
defaultHttpBackendScript = '/usr/lib/git-core/git-http-backend'
defaultGitwebScript = '/usr/lib/cgi-bin/gitweb.cgi'
defaultGitwebStatic = '/usr/share/gitweb/static'
defaultWsgiScript = os.path.join(dictionary[FILESYSTEM_PATH], 'wsgi', 'git.wsgi')
defaultWsgiProcessGroup = dictionary[WSGI_PROCESS_GROUP]
setWord(GIT_ADMIN_SCRIPT, defaultAdminScript)
setWord(GIT_HTTP_BACKEND_SCRIPT, defaultHttpBackendScript)
setWord(GIT_GITWEB_SCRIPT, defaultGitwebScript)
setWord(GIT_GITWEB_STATIC, defaultGitwebStatic)
setWord(GIT_WSGI_SCRIPT_PATH, defaultWsgiScript)
setWord(GIT_WSGI_PROCESS_GROUP, defaultWsgiProcessGroup)


class Plugin(kforge.plugin.base.ServicePlugin):

    settings = [GIT_ADMIN_SCRIPT, GIT_HTTP_BACKEND_SCRIPT, GIT_GITWEB_SCRIPT, GIT_GITWEB_STATIC, GIT_WSGI_SCRIPT_PATH, GIT_WSGI_PROCESS_GROUP]
    
    def onServiceCreate(self, service):
        if self.isOurs(service):
            servicePath = self.paths.getServicePath(service)
            msg = 'GitPlugin: Creating new Git repository for %s: %s' % (
                service, servicePath
            )
            self.logger.info(msg)
            self.paths.assertServiceFolder(service)
            self.createRepository(servicePath, self.dictionary[GIT_ADMIN_SCRIPT])
            self.createGitwebConfig(servicePath, service.project.name, service.name)
            self.buildAndReloadApacheConfig()

    def createRepository(self, path, gitCmd='git'):
        if not os.path.exists(path):
            os.makedirs(path)
        # Create bare repository.
        cmd = 'cd %s; %s --bare init; git update-server-info; if [ -e hooks/post-commit ]; then chmod +x hooks/post-commit; fi' % (path, gitCmd)
        msg = 'GitPlugin: Initializing bare repository: %s' % cmd
        self.logger.info(msg)
        status, output = commands.getstatusoutput(cmd)
        if status:
            raise Exception('git create error on %s: %s' % (cmd, output))
        # Adjust the description file.
        cmd = 'echo "Git repository" > %s/description' % path
        msg = 'GitPlugin: Changing project description: %s' % cmd
        self.logger.info(msg)
        status, output = commands.getstatusoutput(cmd)
        if status:
            raise Exception('error changing git description file %s: %s' % (cmd, output))

    def createGitwebConfig(self, servicePath, projectName, serviceName):
        msg = 'GitPlugin: Configuring new repository for Gitweb.'
        self.logger.info(msg)
        cmd = 'mkdir %(servicePath)s/gitwebprojectroot' % {'servicePath': servicePath}
        status, output = commands.getstatusoutput(cmd)
        if status:
            raise Exception('Unable to create Gitweb project root: %s: %s' % (cmd, output))
        cmd = 'ln -s %(servicePath)s %(servicePath)s/gitwebprojectroot/%(serviceName)s' % {'servicePath': servicePath, 'serviceName': serviceName}
        status, output = commands.getstatusoutput(cmd)
        if status:
            raise Exception('Unable to symlink repository for gitweb: %s: %s' % (cmd, output))
        listFileContent = '%s Administrator\n' % serviceName
        listFilePath = os.path.join(servicePath, 'gitweb.list')
        listFile = open(listFilePath, 'w')
        listFile.write(listFileContent)
        listFile.close()
        configFileContent = '''# Gitweb configuration (generated by KForge).
$projectroot = "%(servicePath)s/gitwebprojectroot";
$projects_list = "%(servicePath)s/gitweb.list";
$git_temp = "/tmp";
#$home_link = $my_uri || "/";
$home_link_str = "%(projectName)s";
#$home_text = "indextext.html";
@stylesheets = ("/gitweb_static/gitweb.css");
$javascript = "/gitweb_static/gitweb.js";
$logo = "/gitweb_static/git-logo.png";
$favicon = "/gitweb_static/git-favicon.png";
#@diff_opts = ("-M");
@diff_opts = ();
''' % {'servicePath': servicePath, 'projectName': projectName}
        configFilePath = os.path.join(servicePath, 'gitweb.conf')
        configFile = open(configFilePath, 'w')
        configFile.write(configFileContent)
        configFile.close()

    def getApacheConfigCommon(self):
        kwds = {
            'staticPath': self.dictionary[GIT_GITWEB_STATIC],
        }
        return """
Alias /gitweb_static %(staticPath)s
""" % kwds

    def getApacheConfig(self, service, configVars):
        # Todo: Change all service URLs to have trailing slash (so config knows where they end
        # and they aren't at risk of shorter patterns matching longer names - current order is critical).
        # Todo: Support static file configuration, see "Accelerated static Apache 2.x" on this
        # page: http://www.kernel.org/pub/software/scm/git/docs/git-http-backend.html
        # - will need dictionary word, default value in dictionary, 
        configVars['servicePath'] = self.paths.getServicePath(service)
        configVars['backendPath'] = self.dictionary[GIT_HTTP_BACKEND_SCRIPT]
        configVars['gitwebPath'] = self.dictionary[GIT_GITWEB_SCRIPT]
        configVars['wsgiScriptPath'] = self.dictionary[GIT_WSGI_SCRIPT_PATH]
        configVars['wsgiProcessGroup'] = self.dictionary[GIT_WSGI_PROCESS_GROUP]
        apacheConfigTmpl = """
<IfModule mod_wsgi.c>
WSGIScriptAlias %(urlPath)s %(wsgiScriptPath)s
WSGIApplicationGroup %%{GLOBAL}
WSGIProcessGroup %(wsgiProcessGroup)s
<Location %(urlPath)s>
SetEnv GIT_PROJECT_ROOT %(servicePath)s
SetEnv GIT_HTTP_EXPORT_ALL
SetEnv GITWEB_CONFIG %(servicePath)s/gitweb.conf
WSGIPassAuthorization On
</Location>
</IfModule>
<IfModule !mod_wsgi.c>
<IfModule mod_python.c>
<Location %(urlPath)s>
SetEnv GIT_PROJECT_ROOT %(servicePath)s
SetEnv GIT_HTTP_EXPORT_ALL
SetEnv GITWEB_CONFIG %(servicePath)s/gitweb.conf
%(modPythonAccessControl)s
</Location>
ScriptAliasMatch "(?x)^%(urlPath)s(.*/(HEAD|info/refs|objects/(info/[^/]+|[0-9a-f]{2}/[0-9a-f]{38}|pack/pack-[0-9a-f]{40}\.(pack|idx))|git-(upload|receive)-pack))$" %(backendPath)s/$1
ScriptAlias %(urlPath)s %(gitwebPath)s
</IfModule>
</IfModule>
"""
        return apacheConfigTmpl % configVars

    def buildWsgiFile(self):
        path = self.dictionary[GIT_WSGI_SCRIPT_PATH]
        content = self.createWsgiScriptContent()
        purpose = 'Git WSGI script'
        self.filesystem.writeWsgiFile(path, content, purpose)

    def createWsgiScriptBody(self, pythonPathActivation):
        gitwebScriptPath = self.dictionary[GIT_GITWEB_SCRIPT]
        httpBackendScriptPath = self.dictionary[GIT_HTTP_BACKEND_SCRIPT]
        wsgiScriptBody = """
# KForge auto-generated Git WSGI File.

import os
import sys

"""
        wsgiScriptBody += pythonPathActivation
        wsgiScriptBody += """

from subprocess import Popen, PIPE
import shlex
import re

gitwebScriptPath = '""" + gitwebScriptPath + """'
httpBackendScriptPath = '""" + httpBackendScriptPath + """'
backend = re.compile(".*/(HEAD|info/refs|objects/(info/[^/]+|[0-9a-f]{2}/[0-9a-f]{38}|pack/pack-[0-9a-f]{40}\.(pack|idx))|git-(upload|receive)-pack)$")

def application(environ, start_response):
    os.environ['KFORGE_SETTINGS'] = '""" + self.dictionary[SYSTEM_CONFIG_PATH] + "'"

        wsgiScriptBody += """
    from kforge.handlers.modwsgi import GitWsgiAccessControlHandler
    from kforge.handlers.modwsgi import WsgiAccessControlHandler
    if backend.search(environ['PATH_INFO']):
        AccessControlHandler = GitWsgiAccessControlHandler
        cgiScriptPath = httpBackendScriptPath
    else:
        AccessControlHandler = WsgiAccessControlHandler
        cgiScriptPath = gitwebScriptPath

    def dispatch_cgi_request(environ, start_response):
        # Prepare environment.
        env = os.environ.copy()
        stdindata = environ.pop('wsgi.input').read()
        for k,v in environ.items():
            if k.startswith('wsgi') or k.startswith('mod_wsgi'):
                continue
            try:
                env[k] = v
            except:
                raise Exception, "Couldn't set %s = %s in new env." % (k, v)
        # Run the CGI script.
        p = Popen(shlex.split(cgiScriptPath), stdin=PIPE, stdout=PIPE, stderr=PIPE, env=env)
        stdoutdata, stderrdata = p.communicate(stdindata)
        if p.wait(): 
            os.stderr.write(stderrdata)
            os.stderr.flush()
        else:
            headers, body = stdoutdata.split('\\r\\n\\r\\n', 1)
            headers = headers.split('\\r\\n')
            headers = [tuple(h.split(': ', 1)) for h in headers]
            start_response('200 OK', headers)
            return [body]
    
    access_control = AccessControlHandler(dispatch_cgi_request)
    return access_control(environ, start_response)
"""    
        return wsgiScriptBody

    def getUserHelp(self, service, serviceLocation):
        values = {'httpUrl' : serviceLocation}
        if 'ssh' in self.registry.plugins:
            import getpass
            sshUrl = 'ssh://%(sshUser)s@%(sshHost)s/%(project)s/%(service)s'
            sshUrl %= {
                'sshUser': self.dictionary[SSH_USER_NAME] or getpass.getuser(),
                'sshHost': self.dictionary[SSH_HOST_NAME],
                'project': service.project.name,
                'service': service.name
            }
            values['sshUrl'] = sshUrl
        helpMessage = '''
<p>This service provides a single Git repository. To find out more about <a href="http://git-scm.com/">Git</a> see the <a href="http://git-scm.com/documentation">Git documentation</a>.</p>
<p>You can access the material in the repository the following ways (provided you have sufficient permission):</p>
<ul>
    <li>Browse the repository with your favorite Web browser.</li>
    <li>Access the repository with a suitable Git client via HTTP.</li>'''
        if 'ssh' in self.registry.plugins:
            helpMessage +='''
    <li>Access the repository with a suitable Git client via SSH.</li>'''
        helpMessage += '''
</ul>

<p>See the <a href="http://www.kernel.org/pub/software/scm/git/docs/user-manual.html">Git Manual</a> for more information on the Git command line client. Graphical user interfaces for Git and Git plugins for rapid development environments such as Eclipse are also available.

<h4>HTTP Access</h4>    
<p>The repository is available via HTTP here:
<b><pre>%(httpUrl)s

</pre></b></p>
<p>Configure HTTP authentication for Git by adding the following to the <code>~/.netrc</code> file. Create the <code>~/.netrc</code> file if necessary:
<pre>machine DOMAINNAME
login USERNAME
password PASSWORD

</pre></p>
<p>check the permissions are set correctly:
<pre>$ chmod 600 ~/.netrc

</pre></p>
<p>If you are using the command line client, you would do:
<pre>$ git clone %(httpUrl)s

</pre>
</p>
<p>After adding changes and committing to the cloned repository, do:
<pre>$ git push origin master

</pre></p>
'''
        if 'ssh' in self.registry.plugins:
            helpMessage +='''
<h4>SSH Access</h4>
<p>The repository is available via SSH here:
<b><pre>%(sshUrl)s

</pre></b></p>
<p>If necessary, register your SSH public key with your account.</p>
<p>If you are using the command line client, you would do:
<pre>$ git clone %(sshUrl)s

</pre>
</p>
<p>After adding changes and committing to the cloned repository, do:
<pre>$ git push origin master

</pre></p>

'''
        msg = helpMessage % values
        return msg


