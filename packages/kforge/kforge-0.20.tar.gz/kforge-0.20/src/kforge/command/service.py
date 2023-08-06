from dm.command import * 
from kforge.exceptions import *
from dm.command.plugin import PluginRead, ProjectPluginList
from kforge.command.project import ProjectRead

class ServiceCommand(Command):
    "Abstract service command."
        
    def __init__(self, **kwds):
        super(ServiceCommand, self).__init__(**kwds)
        self.projectName = kwds['projectName']
        self.pluginName = ''
        self.serviceName = ''
        self.projects = self.registry.projects
        self.plugins = self.registry.plugins
        self.services = None

    def execute(self):
        "Make it so."
        super(ServiceCommand, self).execute()
        self.loadProject()

    def loadProject(self):
        command = ProjectRead(self.projectName)
        command.execute()
        self.project = command.project
        self.services = self.project.services
            
    def isService(self):
        return self.serviceName in self.services


class ServiceCreate(DomainObjectCreate):
    "Command to create a new service."
        
    def __init__(self, **kwds):
        super(ServiceCreate, self).__init__(
            typeName='Service', objectKwds=kwds
        )
        self.service = None

    def execute(self):
        super(ServiceCreate, self).execute()
        self.service = self.object
        
           
class ServiceRead(DomainObjectRead):
    "Command to read a registered service."

    def __init__(self, **kwds):
        super(ServiceRead, self).__init__(
            typeName='Service', objectKwds=kwds
        )

    def execute(self):
        super(ServiceRead, self).execute()
        self.service = self.object


class ServiceDelete(ServiceRead):
    "Command to delete a registered service."

    def execute(self):
        "Make it so."
        super(ServiceDelete, self).execute()
        try:
            self.service.delete()
            self.commitSuccess()
        except KforgeError, inst:
            message = "Couldn't delete that service: %s" % str(inst)
            self.raiseError(message)

class ServiceList(ServiceCommand):
    "Command to list project services."

    def execute(self):
        "Make it so."
        super(ServiceList, self).execute()
        self.results = self.services

