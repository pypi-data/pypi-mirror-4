import kforge.command
from kforge.exceptions import KforgeError

class TracCommand(kforge.command.Command):
    
    def __init__(self, tracProject):
        super(TracCommand, self).__init__()
        if not tracProject:
            raise KforgeError, "TracProject object not given."
        self.tracProject = tracProject
        self.envPath = tracProject.service.getDirPath()


class TracEnvironmentCommand(TracCommand):

    envClass = None

    def __init__(self, tracProject=None, env=None):
        super(TracEnvironmentCommand, self).__init__(tracProject)
        self.env = env

    @classmethod
    def getEnvClass(self):
        if self.envClass == None:
            from trac.env import Environment
            self.envClass = Environment
        return self.envClass

    def getEnv(self):
        if not self.env:
            # Todo: Perhaps use trac.env.open_environment() which aquires
            # a lock and check the environment doesn't need upgrading?
            self.env = self.getEnvClass()(self.envPath)
        return self.env

    def resetEnvPath(self, envPath):
        self.envPath = envPath
        self.env = None


class TracModelCommand(TracEnvironmentCommand):

    resourceNotFoundClass = None

    @classmethod
    def getResourceNotFoundClass(self):
        if self.resourceNotFoundClass == None:
            from trac.resource import ResourceNotFound
            self.resourceNotFoundClass = ResourceNotFound
        return self.resourceNotFoundClass


