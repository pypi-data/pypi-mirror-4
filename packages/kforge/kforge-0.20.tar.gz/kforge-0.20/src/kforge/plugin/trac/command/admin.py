from kforge.plugin.trac.command.base import TracCommand
from kforge.plugin.trac.dictionarywords import TRAC_ADMIN_SCRIPT
import os

class TracAdminCommand(TracCommand):
    """Base class for executing 'trac-admin' command line programme."""

    def __init__(self, tracProject):
        super(TracAdminCommand, self).__init__(tracProject)
        self.tracAdminScript = self.dictionary[TRAC_ADMIN_SCRIPT]
        self.tracArgs = None
    
    def execute(self):
        self.executeTracAdmin()
        if self.status:
            msg = "Error running trac admin script, for service %s.\n"
            msg = msg % self.tracProject.service
            msg += "Trac admin script path: %s\n" % self.tracAdminScript
            msg += "Trac admin script args: %s\n" % self.tracArgs
            msg += "Trac env path: %s\n" % self.envPath
            msg += "Status was: %s\n" % self.status
            msg += "Output was: %s\n" % self.output
            self.logger.error(msg)
            raise Exception, msg

    def executeTracAdmin(self): 
        if self.tracArgs == None:
            raise Exception, "Error: self.tracArgs not set in %s" % self
        cmdArgs = [self.tracAdminScript, self.envPath] + self.tracArgs
        self.logger.debug("Calling Trac admin command: %s" % cmdArgs)
        try:
            import subprocess
            pipe = subprocess.Popen(cmdArgs, shell=False, universal_newlines=True,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.output = str.join("", pipe.stdout.readlines()) 
            self.status = pipe.wait()
            if self.status is None:
                self.status = 0
        except Exception, inst:
            import traceback
            self.status = 1
            self.output = traceback.format_exc()
        if "Unknown syntax" in self.output:
            self.status = 1


class InitialiseTracEnvironment(TracAdminCommand):
    """
    Creates Trac project environment by running "trac-admin initenv".
    """

    def execute(self):
        self.assertTracConfigFileNotFound()
        tracProjectName = self.tracProject.service.project.name.capitalize()
        if self.tracProject.service.name != self.tracProject.service.plugin.name:
            tracProjectName += " " + self.tracProject.service.name.capitalize()
        self.tracArgs = ['initenv', tracProjectName, 'sqlite:db/trac.db']
        super(InitialiseTracEnvironment, self).execute()
        self.assertTracConfigFileExists()
        os.chmod(os.path.join(self.envPath, 'db/trac.db'), 0660 & ~ self.dictionary.getUmask())
        msg = "Initialised trac environment at: %s" % self.envPath
        self.tracProject.logger.info(msg)

    def assertTracConfigFileNotFound(self):
        if self.tracConfigFileExists():
            msg = "Trac config file exists on path: %s" % self.getTracConfigFilePath()
            raise Exception, msg

    def assertTracConfigFileExists(self):
        if not self.tracConfigFileExists():
            msg = "Trac config file not found on path: %s" % self.getTracConfigFilePath()
            self.raiseError(msg)

    def tracConfigFileExists(self):
        return os.path.exists(self.getTracConfigFilePath())

    def getTracConfigFilePath(self):
        tracDirPath = self.tracProject.service.getDirPath()
        return os.path.join(tracDirPath, 'conf', 'trac.ini')


class UpgradeTracEnvironment(TracAdminCommand):

    def execute(self):
        self.tracArgs = ['upgrade']
        super(UpgradeTracEnvironment, self).execute()
        self.tracArgs = ['wiki', 'upgrade']
        super(UpgradeTracEnvironment, self).execute()
        msg = "Upgraded trac environment (and wiki pages) at: %s" % self.envPath
        self.tracProject.logger.info(msg)


class TracConfigCommand(TracAdminCommand):

    action = None


class GetTracConfig(TracAdminCommand):

    def __init__(self, tracProject, section, option):
        super(GetTracConfig, self).__init__(tracProject)
        self.tracArgs = ['config', 'get', section, option]

    def execute(self):
        super(GetTracConfig, self).execute()
        return self.output.strip()


class TracRepositoryCommand(TracAdminCommand):

    def __init__(self, tracRepository, action, *args):
        super(TracRepositoryCommand, self).__init__(tracRepository.tracProject)
        self.tracArgs = ['repository', action] + list(args)


class TracRepositoryAdd(TracRepositoryCommand):

    def __init__(self, tracRepo):
        service = tracRepo.repository
        name = service.name
        path = service.getDirPath()
        if service.plugin.name == 'mercurial':
            path = os.path.join(path, 'repo')
        super(TracRepositoryAdd, self).__init__(tracRepo, 'add', name, path)


class TracRepositorySetType(TracRepositoryCommand):

    def __init__(self, tracRepo):
        service = tracRepo.repository
        name = service.name
        if service.plugin.name == 'mercurial':
            repotype = 'hg'
        else:
            repotype = service.plugin.name
        super(TracRepositorySetType, self).__init__(tracRepo, 'set',  name,
            'type', repotype)


class TracRepositoryRemove(TracRepositoryCommand):

    def __init__(self, tracRepo):
        name = tracRepo.repository.name
        super(TracRepositoryRemove, self).__init__(tracRepo, 'remove', name)


class TracRepositoryResync(TracRepositoryCommand):

    def __init__(self, tracRepo):
        name = tracRepo.repository.name
        super(TracRepositoryResync, self).__init__(tracRepo, 'resync', name)


