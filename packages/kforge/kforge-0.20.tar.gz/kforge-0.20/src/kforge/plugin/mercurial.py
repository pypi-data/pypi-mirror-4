"""
KForge mercurial (hg) plugin.

Enabling this plugin allows KForge project administrators to create Mercurial
services.

Platform dependencies:

   * Mercurial. The Mercurial software is used to create, access, and update service repositories. For example, on Debian, the mercurial package must be installed.

KForge configuration file:

   * You may wish to set the path to the Mercurial admin script.

[mercurial]
admin_script = hg

You can enable, disable, and show status in the usual way.

  $ kforge-admin plugin enable mercurial
  $ kforge-admin plugin show mercurial
  $ kforge-admin plugin disable mercurial

"""
# Todo: Fix the helpMessage so it's https when necessary.
import os
import commands
import shutil
from StringIO import StringIO
import tarfile
import kforge.plugin.base
import kforge.utils.backup
from kforge.dictionarywords import *
from kforge.plugin.base import dictionary, setWord
from kforge.plugin.ssh import SSH_USER_NAME
from kforge.plugin.ssh import SSH_HOST_NAME

MERCURIAL_ADMIN_SCRIPT = ExecutableFileSetting('mercurial.admin_script', umask=022)
MERCURIAL_WSGI_SCRIPT_PATH = WsgiScriptSetting('mercurial.wsgi_file')
MERCURIAL_WSGI_PROCESS_GROUP = StringSetting('mercurial.wsgi_process_group')
MERCURIAL_CGI_SCRIPT_PATH = CgiScriptSetting('mercurial.cgi_file')
defaultAdminScript = os.path.join(dictionary[VIRTUALENVBIN_PATH], 'hg')
defaultWsgiScript = os.path.join(dictionary[FILESYSTEM_PATH], 'wsgi', 'mercurial.wsgi')
defaultWsgiProcessGroup = dictionary[WSGI_PROCESS_GROUP]
defaultCgiScript = os.path.join(dictionary[FILESYSTEM_PATH], 'cgi', 'mercurial.cgi')
setWord(MERCURIAL_ADMIN_SCRIPT, defaultAdminScript)
setWord(MERCURIAL_WSGI_SCRIPT_PATH, defaultWsgiScript)
setWord(MERCURIAL_WSGI_PROCESS_GROUP, defaultWsgiProcessGroup)
setWord(MERCURIAL_CGI_SCRIPT_PATH, defaultCgiScript)


class Plugin(kforge.plugin.base.ServicePlugin):

    settings = [MERCURIAL_ADMIN_SCRIPT, MERCURIAL_WSGI_SCRIPT_PATH, 
        MERCURIAL_WSGI_PROCESS_GROUP, MERCURIAL_CGI_SCRIPT_PATH]
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        self.utils = MercurialUtils(self.dictionary[MERCURIAL_ADMIN_SCRIPT])

    def checkDependencies(self):
        errors = []
        return errors
        hgPath = self.dictionary[MERCURIAL_ADMIN_SCRIPT]
        cmd = 'which %s' % hgPath
        (status, output) = commands.getstatusoutput(cmd)
        if status:
            errors.append("Couldn't find Mercurial admin script '%s' on path." % hgPath)
        cmd = 'python -c "import mercurial"'
        (status, output) = commands.getstatusoutput(cmd)
        if status:
            errors.append("Couldn't import mercurial Python package.")
        return errors

    def showDepends(self):
        results = []
        hgPath = self.dictionary[MERCURIAL_ADMIN_SCRIPT]
        cmd = 'which %s' % hgPath
        (status, output) = commands.getstatusoutput(cmd)
        results.append("Mercurial admin: %s" % (status and "Not found!" or ("Found OK. %s" % output)))
        cmd = 'python -c "import mercurial"'
        (status, output) = commands.getstatusoutput(cmd)
        results.append("Python package: %s" % (status and "Not found!" or "Found OK."))
        return results

    showDepends = classmethod(showDepends)
    
    def onServiceCreate(self, service):
        if self.isOurs(service):
            self.assertServicesFolder(service)
            servicePath = service.getDirPath()
            self.assertNotFileForPath(servicePath)
            self.utils.createRepo(servicePath)
            self.assertFileForPath(servicePath)
            self.log('MercurialPlugin: Created Mercurial repository: %s' % (
                servicePath))
            self.buildAndReloadApacheConfig()
    
    def assertNotFileForPath(self, path):
        if os.path.exists(path):
            message = "Mercurial service exists on path: %s" % path
            self.logger.error(message)
            raise Exception(message)

    def assertFileForPath(self, path):
        if not os.path.exists(path):
            message = "Mercurial service doesn't exist on path %s" % path
            self.logger.error(message)
            raise Exception(message)
    
    def getApacheConfig(self, service, configVars):
        # The implementation of Apache configuration follows:
        # http://www.selenic.com/mercurial/wiki/index.cgi/PublishingRepositories
        configVars['serviceName'] = service.project.name + '-' + service.name
        configVars['wsgiScriptPath'] = self.dictionary[MERCURIAL_WSGI_SCRIPT_PATH]
        configVars['wsgiProcessGroup'] = self.dictionary[MERCURIAL_WSGI_PROCESS_GROUP]
        configVars['cgiScriptPath'] = self.dictionary[MERCURIAL_CGI_SCRIPT_PATH]
        apacheConfigTmpl = """
<IfModule mod_wsgi.c>
WSGIScriptAlias %(urlPath)s %(wsgiScriptPath)s
WSGIApplicationGroup %%{GLOBAL}
WSGIProcessGroup %(wsgiProcessGroup)s
<Location %(urlPath)s>
SetEnv KFORGE_MERCURIAL_REPO_PATH %(fileSystemPath)s/repo
SetEnv KFORGE_MERCURIAL_REPO_NAME %(serviceName)s
WSGIPassAuthorization On
</Location>
</IfModule>
<IfModule !mod_wsgi.c>
<IfModule mod_python.c>
ScriptAlias %(urlPath)s %(cgiScriptPath)s
<Location %(urlPath)s>
SetEnv KFORGE_MERCURIAL_REPO_PATH %(fileSystemPath)s/repo
SetEnv KFORGE_MERCURIAL_REPO_NAME %(serviceName)s
%(modPythonAccessControl)s
</Location>
</IfModule>
</IfModule>
"""
        return apacheConfigTmpl % configVars

    def buildWsgiFile(self):
        path = self.dictionary[MERCURIAL_WSGI_SCRIPT_PATH]
        content = self.createWsgiScriptContent()
        purpose = 'Mercurial WSGI script'
        self.filesystem.writeWsgiFile(path, content, purpose)

    def createWsgiScriptBody(self, pythonPathActivation):
        wsgiScriptBody = """
# KForge auto-generated Mercurial WSGI File.

import os
import sys

"""
        wsgiScriptBody += pythonPathActivation
        wsgiScriptBody += """

from mercurial.hgweb import hgweb
os.environ["HGENCODING"] = "UTF-8"

def application(environ, start_response):
    os.environ['KFORGE_SETTINGS'] = '""" + self.dictionary[SYSTEM_CONFIG_PATH] + "'"

        wsgiScriptBody += """
    from kforge.handlers.modwsgi import WsgiAccessControlHandler
    repositoryPath = environ.pop('KFORGE_MERCURIAL_REPO_PATH')
    repositoryName = environ.pop('KFORGE_MERCURIAL_REPO_NAME')
    accessapplication = WsgiAccessControlHandler(hgweb(repositoryPath, repositoryName))
    return accessapplication(environ, start_response)
"""    
        return wsgiScriptBody

    def buildCgiFile(self):
        path = self.dictionary[MERCURIAL_CGI_SCRIPT_PATH]
        content = self.createCgiScriptContent()
        purpose = 'Mercurial CGI script'
        self.filesystem.writeCgiFile(path, content, purpose)

    def createCgiScriptContent(self):
        # Todo: Fixup so it uses virtualenv or PYTHONPATH, if they exist.
        cgiScriptContent = '''#!/usr/bin/env python

import os
os.environ["HGENCODING"] = "UTF-8"

from mercurial.hgweb.hgweb_mod import hgweb
from mercurial.hgweb.request import wsgiapplication
import mercurial.hgweb.wsgicgi as wsgicgi

def make_web_app():
    repositoryPath = os.environ.pop('KFORGE_MERCURIAL_REPO_PATH')
    repositoryName = os.environ.pop('KFORGE_MERCURIAL_REPO_NAME')
    return hgweb(repositoryPath, repositoryName)

wsgicgi.launch(wsgiapplication(make_web_app))
'''
        return cgiScriptContent

    def backup(self, service, backupPathBuilder):
        path = service.getDirPath()
        backupPath = backupPathBuilder.getServicePath(service)
        self.utils.backup(path, backupPath)

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
<p>This service provides a single Mercurial repository. To find out more about <a href="http://mercurial.selenic.com/">Mercurial</a> see the <a href="http://mercurial.selenic.com/guide/">Mercurial Guide</a>.</p>
<p>You can access the material in the repository the following ways (provided you have sufficient permission):</p>
<ul>
    <li>Browse the repository with your favorite Web browser.</li>
    <li>Access the repository with a suitable Mercurial client via HTTP.</li>'''
        if 'ssh' in self.registry.plugins:
            helpMessage +='''
    <li>Access the repository with a suitable Mercurial client via SSH.</li>'''
        helpMessage += '''
</ul>

<p>See the <a href="http://mercurial.selenic.com/guide/">Mercurial Guide</a> for more information on the Mercurial command line client. Graphical user interfaces for Mercurial and Mercurial plugins for rapid development environments such as Eclipse are also available.

<h4>HTTP Access</h4>
<p>The repository is available via HTTP here:
<b><pre>%(httpUrl)s

</pre></b></p>
<p>Configure HTTP authentication by adding the following to your <code>~/.hgrc</code> file. Create the <code>~/.hgrc</code> file if necessary:
<pre>
[ui]
username = FULLNAME <you@example.com>

[auth]
kforge.prefix = http://DOMAINNAME/
kforge.username = USERNAME
kforge.password = PASSWORD

</pre></p>
<p>If you are using the command line client, you would do:
<pre>$ hg clone %(httpUrl)s

</pre>
</p>
<p>After adding changes and committing to the cloned repository, do:</p>
<pre>$ hg push

</pre>
'''
        if 'ssh' in self.registry.plugins:
            helpMessage +='''
<h4>SSH Access</h4>
<p>The repository is available via SSH here:
<b><pre>%(sshUrl)s

</pre></b></p>
<p>If necessary, register your SSH public key with your account.</p>
<p>If you are using the command line client, you would do:
<pre>$ hg clone %(sshUrl)s

</pre>
</p>
<p>After adding changes and committing to the cloned repository, do:
<pre>$ hg push

</pre></p>

'''
        msg = helpMessage % values
        return msg


class MercurialUtils(object):
   
    def __init__(self, adminScriptPath='hg'):
        self.adminScriptPath = adminScriptPath
 
    def createRepo(self, servicePath):
        repoPath = os.path.join(servicePath, 'repo')
        if not os.path.exists(repoPath):
            os.makedirs(repoPath)
        self.initRepo(repoPath)
        self.pushEnableRepo(repoPath)

    def initRepo(self, repoPath):
        cmd = '%s init %s' % (self.adminScriptPath, repoPath)
        s, o = commands.getstatusoutput(cmd)
        if s:
            msg = 'Could not create mercurial repository: %s: %s' % (cmd, o)
            raise Exception(msg)

    def pushEnableRepo(self, repoPath):
        hgrcFileContent = '''
[web]
allow_push = *
# allow pushing over http as well as https 
push_ssl = false
'''
        hgrcFilePath = os.path.join(repoPath, '.hg', 'hgrc')
        hgrcFile = open(hgrcFilePath, 'w')
        hgrcFile.write(hgrcFileContent)
        hgrcFile.close()

    def delete(self, path):
        if os.path.exists(path):
            shutil.rmtree(path)

    def backup(self, path, dest):
        dest = dest + '.tgz'
        tar = tarfile.open(dest, 'w:gz')
        tar.add(path)
        tar.close()

