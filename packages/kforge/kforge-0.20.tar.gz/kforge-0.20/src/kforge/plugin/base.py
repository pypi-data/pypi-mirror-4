import dm.plugin.base
import os
from dm.strategy import FindProtectionObject
from dm.strategy import CreateProtectionObject
from dm.dictionarywords import APACHE_RELOAD_CMD
import dm.times
from kforge.dictionarywords import *
from subprocess import Popen, PIPE
import shlex
from kforge.apache.config import ApacheConfigBuilder
from kforge.ioc import RequiredFeature

dictionary = RequiredFeature('SystemDictionary')
config = dictionary.configFileReader
configKeys = config.keys()

def setWord(word, default):
    if word in configKeys:
        value = config[word]
    else:
        value = default
    dictionary.set(word, value)


class AbstractServicePlugin(dm.plugin.base.PluginBase):
    """
    Service plugins deploy adapted software applications as project services.
    """
    
    pluginController = RequiredFeature('PluginController')
    accessController = RequiredFeature('AccessController')
    apacheConfigBuilder = None
    settings = []

    @classmethod
    def checkSettings(self, errors=[]):
        results = []
        for setting in self.settings:
            if not isinstance(setting, DictionaryDef):
                continue
            try:
                value = self.dictionary[setting]
                result = setting.check(value, self.dictionary)
                results.append(result)
            except DictionaryDefinitionError, inst:
                errors.append(inst)
                results.append(inst)
        return results

    @classmethod
    def getApacheConfigBuilder(self):
        if self.apacheConfigBuilder == None:
            self.apacheConfigBuilder = ApacheConfigBuilder()
        return self.apacheConfigBuilder

    def buildAndReloadApacheConfig(self):
        self.getApacheConfigBuilder().buildAndReload()

    def checkDependencies(self):
        errors = []
        return errors

    def showDepends(self):
        return [
        ]
    showDepends = classmethod(showDepends)

    def getMaxServicesPerProject(self):
        raise Exception("Abstract method not implemented.")

    def isOurs(self, service):
        "Checks whether a service belongs to this plugin."
        return service and service.plugin and \
            service.plugin.name == self.domainObject.name
    
    def ensureProjectPluginDirectoryExists(self, service):
        self.assertServicesFolder(service)

    def assertServicesFolder(self, service):
        path = self.filesystem.getProjectPluginPath(service.project, service.plugin)
        self.filesystem.assertFolder(path, 'project %s services' % service.plugin.name)
    
    def backup(self, service, backupPathBuilder):
        """Backup the plugged-in application service.

        @backupPathBuilder: any object supporting a function getServicePath.
        """
        pass

    def sync(self):
        pass
    
    def onCreate(self):
        # Setup access control.
        createObject = CreateProtectionObject(self.domainObject)
        protectionObject = createObject.create()
        import kforge.command
        cmd = kforge.command.GrantStandardProjectAccess(protectionObject)
        cmd.execute()
        # Setup filesystem.
        self.buildWsgiFile() 
        self.buildCgiFile() 
        self.buildLocksDir()
        # Check settings.
        errors = []
        self.checkSettings(errors=errors)
        if errors:
            raise Exception, "Plugin settings not okay. %s" % '; '.join([str(i) for i in errors])
    
    def onDelete(self):
        findObject = FindProtectionObject(self.domainObject)
        try:
            protectionObject = findObject.find()
        except:
            pass
        else:
            if protectionObject:
                protectionObject.delete()

    def getUserHelp(self, service, serviceLocation):
        """Provide a service user help message.
        """
        return ''

    def getStatusMessage(self, service):
        """Provide a service status message.
        """
        # Todo: Check at least whether HEAD gets a 404?
        # Todo: Involve the Apache config file last-modified time: make sure 
        # file last modified after service date created; then make sure system
        # started after file was last modified.
        serviceCreated = service.dateCreated
        if serviceCreated < self.dictionary[APACHE_CONFIG_LAST_MODIFIED]:
            # Created before Apache config last modified when system started.
            msg = "Running"
        else:
            # Created after Apache config last modified when system started.
            msg = "Configuring"
        return msg

    def getApacheConfigCommon(self):
        """
        Return a fragment of Apache config that is only needed once per plugin
        per virtual host (so common across all instances
        """
        return ''

    def getApacheConfig(self, service, configVars):
        """
        Returns a fragment of apache config appropriate for the plugin instance.
        """
        return ''

    def buildWsgiFile(self):
        pass

    def buildCgiFile(self):
        pass

    def buildLocksDir(self):
        pass

    def createWsgiScriptContent(self):
        pythonVirtualenvActivation = self.createVirtualenvActivation()
        if not pythonVirtualenvActivation:
            pythonPathActivation = self.createPythonPathActivation()
        else:
            pythonPathActivation = ''
        wsgiScriptBody = self.createWsgiScriptBody(pythonPathActivation)
        wsgiScriptContent = pythonVirtualenvActivation + wsgiScriptBody
        return wsgiScriptContent

    def createWsgiScriptBody(self, pythonPathActivation):
        raise Exception, "Method not implemented on %s" % self

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

    def writeFile(self, *args, **kwds):
        self.filesystem.writeFile(*args, **kwds)

    def onServicePurge(self, service):
        if self.isOurs(service):
            self.trashServiceFolder(service)

    def trashServiceFolder(self, service):
        servicePath = self.filesystem.getServicePath(service)
        msg = "%sPlugin: Trashing service folder: %s" % (self.domainObject.name.capitalize(), servicePath)
        self.logger.info(msg)
        if not os.path.exists(servicePath):
            return
        self.filesystem.assertTrashFolder()
        trashPath = self.filesystem.getTrashPath()
        trashBase = os.path.join(trashPath, str(service.id))
        trashNew = trashBase
        trashIndex = 0
        while os.path.exists(trashNew):
            trashNew = "%s.%s" % (trashBase, trashIndex)
            trashIndex += 1
        try:
            import shutil
            shutil.move(servicePath, trashNew)
        except Exception, inst:
            msg = "Couldn't move service files into trash: tried moving %s to %s: %s" % (
                servicePath, trashNew, inst
            )

    def isReadyToReload(self, service):
        return True

    def runPopen(self, cmd, stdindata=None, shell=False):
        stdin = None
        if stdindata:
            stdin = PIPE
        if type(cmd) == list:
            args = [str(i) for i in cmd]
        else:
            args = shlex.split(str(cmd))
        msg = "Running command with Popen using args: %s" % (args)
        msg += " with stdin data: %s" % stdindata
        self.logger.debug(msg)
        try:
            p = Popen(args=args, stdin=stdin, stdout=PIPE, stderr=PIPE, shell=shell)
            stdoutdata, stderrdata = p.communicate(stdindata)
            status = p.wait()
            if status:
                msg = 'status: %s' % status
                if stdoutdata:
                    msg += stdoutdata
                if stderrdata:
                    msg += stderrdata
                raise Exception(msg)
        except Exception, inst:
            msg = "Error: Popen args %s caused error: %s" % (args, repr(inst))
            self.logger.error(msg)
            raise Exception(msg)
  

class ServicePlugin(AbstractServicePlugin):
    
    def getMaxServicesPerProject(self):
        return None


class SingleServicePlugin(AbstractServicePlugin):

    def getMaxServicesPerProject(self):
        return 1


class NonServicePlugin(AbstractServicePlugin):

    def getMaxServicesPerProject(self):
        return 0

