"""
KForge MoinMoin plugin.

Installing this plugin allows users to create moinmoin services to provide
moinmoin wikis associated with their project.

This Plugin has been tested against moinmoin v1.3 and v1.5 but should worked with later versions.

## Installation

1. To create services using this plugin you must have installed the following
   external applications:

   * moinmoin

2. Add the following to your kforge.conf file

[moin]
# where moin system data is installed (htdocs etc)
system_path = /usr/share/moin

3. This plugin will copy data from that location in order to create each new
wiki (see MoinUtils below). A couple of changes that may be required:

    1. This plugin mounts the moinmoin htdocs at /moinhtdocs. You will
    therefore need to ensure that the standard wikiconfig.py has this set as
    the htdocs prefix.

    2. Any other wikiconfig variables that you want to be same in all the
    kforge services you should set in the master wikiconfig.py.

3. Install and enable this plugin in the usual way (see the KForge Guide
   for details).
"""
import kforge.plugin.base
from kforge.ioc import *
import os
import shutil
import tarfile
import fileinput
import sys
from kforge.dictionarywords import *
from kforge.plugin.base import dictionary, setWord

MOIN_SYSTEM_PATH = DirSetting('moin.system_path')
MOIN_VERSION = StringSetting('moin.version')
MOIN_WSGI_PROCESS_GROUP = StringSetting('moin.wsgi_process_group')
setWord(MOIN_SYSTEM_PATH, '/usr/share/moin')
setWord(MOIN_VERSION, '193')
setWord(MOIN_WSGI_PROCESS_GROUP, dictionary[WSGI_PROCESS_GROUP])


class Plugin(kforge.plugin.base.ServicePlugin):
    "MoinMoin Wiki Plugin"

    settings = [MOIN_SYSTEM_PATH, MOIN_VERSION, MOIN_WSGI_PROCESS_GROUP]
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        self.moinUtils = MoinUtils(self.dictionary[MOIN_SYSTEM_PATH])
    
    def onServiceCreate(self, service):
        if self.isOurs(service):
            self.assertServicesFolder(service)
            wikiPath = service.getDirPath()
            self.moinUtils.createWiki(wikiPath)
            self.buildAndReloadApacheConfig()
    
    #def onServicePurge(self, service):
    #    if self.isOurs(service):
    #        wikiPath = service.getDirPath()
    #        self.moinUtils.deleteWiki(wikiPath)
    
    def getApacheConfigCommon(self):
        """
        Ensure that you have edited the moin config file to use the moinhtdocs
        values set here
        """
        kwds = {
            'htdocsPath': os.path.join(self.dictionary[MOIN_SYSTEM_PATH], 'htdocs'),
            'moinVersion': self.dictionary[MOIN_VERSION],
        }
        return """
Alias /moinhtdocs %(htdocsPath)s
Alias /moin_static%(moinVersion)s %(htdocsPath)s
""" % kwds
    
    def getApacheConfig(self, service, configVars):
        configVars['wsgiProcessGroup'] = self.dictionary[MOIN_WSGI_PROCESS_GROUP]
        apacheConfigTmpl = """
<IfModule mod_wsgi.c>
WSGIScriptAlias %(urlPath)s %(fileSystemPath)s/moin.wsgi
WSGIApplicationGroup %%{GLOBAL}
WSGIProcessGroup %(wsgiProcessGroup)s
<Location %(urlPath)s>
WSGIPassAuthorization On
</Location>
</IfModule>
<IfModule !mod_wsgi.c>
<IfModule mod_python.c>
ScriptAlias %(urlPath)s %(fileSystemPath)s/moin.cgi
<Location %(urlPath)s>
%(modPythonAccessControl)s
</Location>
</IfModule>
</IfModule>
"""
        return apacheConfigTmpl % configVars
    
    def backup(self, service, backupPathBuilder):
        self.moinUtils.backupWiki(service.getDirPath(), backupPathBuilder.getServicePath(service))


class MoinUtils(object):
    """
    Scripts to assist with setting up moinmoin wikis:
      1. Wiki creation and deletion
      2. Automate upgrading moin wikis from version 1.2 to version 1.3
    """
    
    logger = RequiredFeature('Logger')
    dictionary = RequiredFeature('SystemDictionary')
    
    def __init__(self, systemPath, basePath = ''):
        """
        @systemPath: path on which moin was installed (e.g. /usr/share/moin)
        @basePath: base path at which to create wikis. If not set defaults to
                   empty string in which case wikiName where supplied in
                   functions below must be full path of wiki
        """
        self.systemPath = systemPath
        self.basePath = basePath
    
    def getWikiPath(self, wikiName):
        return os.path.join(self.basePath, wikiName)

    def wikiExists(self, wikiName):
        return os.path.exists(self.getWikiPath(wikiName))

    def createWiki(self, wikiName, copyFiles=True):
        """
        Create a new wiki instance with default files.
        Originally written to work for moinmoin1.3.
        Adapted to work with v1.9.
        """
        # Todo: Test with versions of MoinMoin from 1.3 to 1.9.
        if self.wikiExists(wikiName):
            raise Exception('Cannot create wiki as path already exists: %s' % self.getWikiPath(wikiName))
        newWikiBasePath = self.getWikiPath(wikiName)
        self.logger.info('Creating new wiki: %s' % newWikiBasePath)
        os.makedirs(newWikiBasePath)
        if copyFiles:
            shutil.copytree(os.path.join(self.systemPath, 'data'),
                            os.path.join(newWikiBasePath, 'data'))
            shutil.copytree(os.path.join(self.systemPath, 'underlay'),
                            os.path.join(newWikiBasePath, 'underlay'))
        shutil.copy(os.path.join(self.systemPath, 'config/wikiconfig.py'),
                    newWikiBasePath)
        # do cgi-bin (do not install to cgi-bin but to base dir)
        # that way all paths will work out of the box
        # installCgiPath = os.path.join(newWikiBasePath, 'cgi-bin')
        # os.makedirs(installCgiPath)
        scriptNames = ['moin.cgi', 'moin.wsgi']
        for scriptName in scriptNames:
            origPath = os.path.join(self.systemPath, 'server', scriptName)
            shutil.copy(origPath, newWikiBasePath)
            scriptPath = os.path.join(newWikiBasePath, scriptName)
            replacePath = '/etc/moin'
            self.logger.debug("Modifying moin script %s, to replace '%s' with '%s'." % (scriptPath, replacePath, newWikiBasePath))
            for line in fileinput.input(scriptPath, inplace=1):
                line = line.replace(replacePath, newWikiBasePath)
                sys.stdout.write(line)
        # Add virtualenv activation and KForge access control to WSGI script.
        wsgiScriptPath = os.path.join(newWikiBasePath, 'moin.wsgi')
        wsgiScriptContent = self.createVirtualenvActivation()
        hasPythonPathActivation = not wsgiScriptContent
        wsgiScript = open(wsgiScriptPath)
        origScriptContent = wsgiScript.read()
        wsgiScript.close()
        #wsgiScriptContent += origScriptContent.replace('/etc/moin', newWikiBasePath)
        wsgiScriptContent += origScriptContent
        if hasPythonPathActivation:
            wsgiScriptContent += self.createPythonPathActivation()
        wsgiScriptContent += self.createWsgiAccessControl(newWikiBasePath)
        wsgiScript = open(wsgiScriptPath, 'w')
        wsgiScript.write(wsgiScriptContent)
        wsgiScript.close()
        # Set permissions.
        self.setPermissions(wikiName)

    def createWsgiAccessControl(self, newWikiBasePath):
        wsgiScriptBody = """
# KForge auto-generated Moin WSGI access control.

"""
        wsgiScriptBody += """

moinmoin = application

def application(environ, start_response):
    os.environ['KFORGE_SETTINGS'] = '"""+self.dictionary[SYSTEM_CONFIG_PATH]+"""'
    from kforge.handlers.modwsgi import WsgiAccessControlHandler
    access_control = WsgiAccessControlHandler(moinmoin)
    return access_control(environ, start_response)
"""    
        return wsgiScriptBody

    def createVirtualenvActivation(self):
        virtualenvActivation = ''
        if self.dictionary[VIRTUALENVBIN_PATH]:
            # Todo: Revisit in favour of 
            # http://code.google.com/p/modwsgi/wiki/VirtualEnvironments.
            # would just need to know "the full path to the 'site-packages'
            # directory for the virtual environment", but that is available 
            # as os.path.dirname(os.__file__)? Need to baseline WSGI with
            # WSGIPythonHome /usr/local/pythonenv/BASELINE in main Apache
            # configuration. So would have to add that to install guides?
            virtualenvActivation = """activate_this = '%(ACTIVATE_THIS_PATH)s'
execfile(activate_this, dict(__file__=activate_this))

"""         % {
                'ACTIVATE_THIS_PATH': os.path.join(self.dictionary[VIRTUALENVBIN_PATH], 'activate_this.py')
            }
        return virtualenvActivation

    def createPythonPathActivation(self):
        pythonPathActivation = ''
        if self.dictionary[PYTHONPATH]:
            pythonPathActivation = """
for path in %(PYTHON_PATH_LIST)s:
    if path not in sys.path:
        sys.path.append(path)

"""         % {
                'PYTHON_PATH_LIST': self.dictionary[PYTHONPATH].split(':'),
            }
        return pythonPathActivation

    def setPermissions(self, wikiName):
        newWikiBasePath = self.getWikiPath(wikiName)
        # now set permissions
        # only webserver should have access
        if (
            os.system('chmod -R ug+rwX %s' % newWikiBasePath)
            or
            os.system('chmod -R o-rwx %s' % newWikiBasePath)):
            self.logger.error('Failed to set permissions and owner correctly on %s' % newWikiBasePath)

    def deleteWiki(self, wikiName):
        path = self.getWikiPath(wikiName)
        if os.path.exists(path):
            shutil.rmtree(path)

    def migrateWikiData(self, dataSource, dataTarget):
        import re
        # moin migration scripts path
        scriptsPath = '/usr/lib/python2.3/site-packages/MoinMoin/scripts/migration'
        dataForMigration = os.path.join(scriptsPath, 'data')
        # delete all dirs named data* in scriptsPath dir
        tfiles  = os.listdir(scriptsPath)
        regexFilter  = re.compile("data.*", re.IGNORECASE)
        tfiles = filter(regexFilter.search, tfiles)
        for ff in tfiles:
            shutil.rmtree(os.path.join(scriptsPath, ff))
        shutil.copytree(dataSource, dataForMigration)
        scriptsToRun = [
            '12_to_13_mig01.py',
            '12_to_13_mig02.py',
            '12_to_13_mig03.py',
            '12_to_13_mig04.py',
            '12_to_13_mig05.py',
            '12_to_13_mig06.py',
            '12_to_13_mig07.py',
            '12_to_13_mig08.py',
            '12_to_13_mig09.py',
            '12_to_13_mig10.py',
            '12_to_13_mig11.py']# move the data to the right place
        # have to run the scripts from the local dir for it to work
        os.chdir(scriptsPath)
        print 'Migration: START'
        for script in scriptsToRun:
            os.system('./%s > /dev/null' % script)
        print 'Migration: COMPLETED'
        if os.path.exists(dataTarget):
            shutil.rmtree(dataTarget)
        shutil.copytree(dataForMigration, dataTarget)

    def migrateWiki(self, oldWikiPath, newWikiName):
        dataSource = os.path.join(oldWikiPath, 'data')
        dataTarget = os.path.join(self.getWikiPath(newWikiName), 'data')
        # first create new wiki (without data dir)
        if self.wikiExists(newWikiName):
            self.removeWiki(newWikiName)
        self.createWiki(newWikiName, copyFiles=False)
        # now migrate
        self.migrateWikiData(dataSource,  dataTarget)
        # need to redo permissions because of data directory
        self.setPermissions(newWikiName)
    
    def backupWiki(self, wikiName, destPath):
        destPath = destPath + '.tgz'
        tar = tarfile.open(destPath, 'w:gz')
        tar.add(self.getWikiPath(wikiName))
        tar.close()
