"""
KForge dav Plugin.

Enabling this plugin gives dav access to the project directory and all
subdirectories.

## Installation ##

1. Dependencies. To create services using this plugin you must have installed
   the following external applications:

   * Apache dav module (mod_dav). Note that on many systems this will be
     installed by default.

2. KForge config file. You do not need to add anything to the KForge config
   file.


NB: If you see "Invalid method in request USERINFO" in Apache error log, this
seems to be a result of using a particular client. It isn't a KForge error.

"""
import kforge.plugin.base
from dm.strategy import FindProtectionObject
from kforge.dictionarywords import *
from kforge.plugin.base import dictionary, setWord
from kforge.ioc import RequiredFeature
import os
import shutil

filesystem = RequiredFeature('FileSystem')
DAV_LOCK_PATH = DavLockSetting('dav.lock_path')
DAV_WSGI_SCRIPT_PATH = WsgiScriptSetting('dav.wsgi_script')
DAV_WSGI_PROCESS_GROUP = DictionaryDef('dav.wsgi_process_group')
defaultLocksPath = os.path.join(dictionary[FILESYSTEM_PATH], 'var', 'locks', 'DAV.lock')
defaultWsgiScriptPath = os.path.join(dictionary[FILESYSTEM_PATH], 'wsgi', 'dav.wsgi')
defaultWsgiProcessGroup = dictionary[WSGI_PROCESS_GROUP]
setWord(DAV_LOCK_PATH, defaultLocksPath)
setWord(DAV_WSGI_SCRIPT_PATH, defaultWsgiScriptPath)
setWord(DAV_WSGI_PROCESS_GROUP, defaultWsgiProcessGroup)

class Plugin(kforge.plugin.base.SingleServicePlugin):

    settings = [DAV_LOCK_PATH, DAV_WSGI_SCRIPT_PATH, DAV_WSGI_PROCESS_GROUP]
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
    
    def onServiceCreate(self, service):
        if self.isOurs(service):
            self.paths.assertProjectFolder(service.project)
            self.buildAndReloadApacheConfig()

    def getApacheConfigCommon(self):
        configVars = {'lockFilePath': self.dictionary[DAV_LOCK_PATH]}
        configTmpl = """
DavLockDB %(lockFilePath)s
"""
        return configTmpl % configVars

    def getApacheConfig(self, service, configVars):
        projectPath = self.paths.getProjectPath(service.project)
        configVars['wsgiScriptPath'] = self.dictionary[DAV_WSGI_SCRIPT_PATH]
        configVars['wsgiProcessGroup'] = self.dictionary[DAV_WSGI_PROCESS_GROUP]
        configVars['projectPath'] = self.paths.getProjectPath(service.project)
        apacheConfigTmpl = """
<IfModule mod_wsgi.c>
WSGIScriptAlias %(urlPath)s %(wsgiScriptPath)s
WSGIApplicationGroup %%{GLOBAL}
WSGIProcessGroup %(wsgiProcessGroup)s
<Location %(urlPath)s>
SetEnv KFORGE_DAV_FILESYSTEM_PATH %(projectPath)s
SetEnv KFORGE_DAV_MOUNT_PATH %(urlPath)s
WSGIPassAuthorization On
</Location>
</IfModule>

<IfModule !mod_wsgi.c>
<IfModule mod_python.c>
Alias %(urlPath)s %(projectPath)s
<Location %(urlPath)s>
DAV On
Options +Indexes
# Remove use DirectoryIndex
DirectoryIndex none.none.none
# 'ForceType text/plain' so DAV interprets all file types as text.
ForceType text/plain
%(modPythonAccessControl)s
</Location>
</IfModule>
</IfModule>
"""
        return apacheConfigTmpl % configVars
    
    def onCreate(self):
        # Todo: Pull various bits of access controller setup together under the name 'setupAccessControl'.
        super(Plugin, self).onCreate()
        protectionObject = FindProtectionObject(self.domainObject).find()
        # Don't allow Friends to read the DAV plugin, as it gives access to all project data.
        permission = protectionObject.permissions[self.registry.actions['Read']]
        friend = self.registry.roles['Friend']
        if permission in friend.grants:
            grant = friend.grants[permission]
            grant.delete()
        # Don't allow Developers to write to the DAV plugin, as it gives access to all project data.
        permission = protectionObject.permissions[self.registry.actions['Update']]
        friend = self.registry.roles['Developer']
        if permission in friend.grants:
            grant = friend.grants[permission]
            grant.delete()

    def buildWsgiFile(self):
        path = self.dictionary[DAV_WSGI_SCRIPT_PATH]
        content = self.createWsgiScriptContent()
        purpose = 'DAV WSGI script'
        self.filesystem.writeWsgiFile(path, content, purpose)

    def buildLocksDir(self):
        # Create dirs if they don't exist.
        lockDirPath = os.path.dirname(self.dictionary[DAV_LOCK_PATH])
        if not os.path.exists(lockDirPath):
            # Parents need to have permission 750.
            umask = os.umask(0o027)
            if not os.path.dirname(lockDirPath):
                os.makedirs(os.path.dirname(lockDirPath))
            # Locks directory needs to have permission 770.
            os.umask(0o007)
            os.makedirs(lockDirPath)
            os.umask(umask)

    def createWsgiScriptBody(self, pythonPathActivation):
        wsgiScriptBody = """
# KForge auto-generated DAV WSGI File.

import os
import sys
"""
        wsgiScriptBody += pythonPathActivation
        wsgiScriptBody += """
from wsgidav.wsgidav_app import DEFAULT_CONFIG, WsgiDAVApp

def application(environ, start_response):
    os.environ['KFORGE_SETTINGS'] = '""" + self.dictionary[SYSTEM_CONFIG_PATH] + "'"
        wsgiScriptBody += """
    from kforge.handlers.modwsgi import WsgiAccessControlHandler
    davFsPath = environ.pop('KFORGE_DAV_FILESYSTEM_PATH')
    davConfig = DEFAULT_CONFIG.copy()
    davConfig.update({
        'provider_mapping': {'/': davFsPath},
        'mount_path': environ.pop('KFORGE_DAV_MOUNT_PATH'),
        'verbose': 0,
    })
    davapplication = WsgiDAVApp(davConfig)
    accessapplication = WsgiAccessControlHandler(davapplication)
    return accessapplication(environ, start_response)
"""    
        return wsgiScriptBody

    def getUserHelp(self, service, serviceLocation):
        values = {'httpUrl' : serviceLocation}
        helpMessage = '''
<p>This service provides a WebDAV filesystem. To find out more about <a href="http://www.webdav.org/">WebDAV</a> see the <a href="http://www.webdav.org/other/faq.html">WebDAV FAQ</a>.</p>
<p>You can access the material in the filesystem in the following ways (provided you have sufficient permission):</p>
<ul>
    <li>Browse the material online by following the link to the WebDAV filesystem in your browser.</li>
    <li>Update the material online by opening the WebDAV filesystem in a WebDAV enabled application such as Internet Explorer, Konqueror and Nautilus.</li>
    <li>Mount the WebDAV filesystem within your local filesystem from the command line.</li>
</ul>

<h4>HTTP Access</h4>
<p>The repository is available via HTTP here:
<b><pre>%(httpUrl)s/

</pre></b>

</p>
<h4>Mounting the Filesystem</h4>
<p>If you wish to mount the WebDAV filesystem within your local filesystem from the command line client, you would do:
<pre>$ mkdir mydavfs
$ sudo mount -t davfs %(httpUrl)s mydavfs -o uid=$USER
Please enter the username to authenticate with server
%(httpUrl)s or hit enter for none.
  Username: KFORGEUSER
Please enter the password to authenticate user KFORGEUSER with server
%(httpUrl)s or hit enter for none.
  Password: </pre>
</p>
<p>To unmount the filesystem, you would do:
<pre>$ sudo umount mydavfs </pre>
</p>
'''
        msg = helpMessage % values
        return msg

