import dm.dom.builder
from dm.dictionarywords import SYSTEM_MODE

class ModelBuilder(dm.dom.builder.ModelBuilder):

    def construct(self):
        super(ModelBuilder, self).construct()
        self.loadTicket()
        self.loadApiKey()
        self.loadProject()
        self.loadLicense()
        self.loadService()
        self.loadMember()
        self.loadFeedEntry()
        if self.dictionary[SYSTEM_MODE] == 'development':
            self.loadMemoryDump()

    def loadApiKey(self):
        from dm.dom.apikey import ApiKey
        self.registry.registerDomainClass(ApiKey)
        self.registry.apiKeys = ApiKey.createRegister()

    def loadPlugin(self): 
        from kforge.dom.plugin import Plugin
        self.registry.registerDomainClass(Plugin)
        self.registry.plugins = Plugin.createRegister()
        Plugin.principalRegister = self.registry.plugins

    def loadPerson(self):
        from kforge.dom.person import Person
        from kforge.dom.person import SshKey
        self.registry.registerDomainClass(Person)
        self.registry.registerDomainClass(SshKey)
        self.registry.people = Person.createRegister()
        self.registry.sshKeys = SshKey.createRegister()
        Person.principalRegister = self.registry.people
        SshKey.principalRegister = self.registry.sshKeys

    def loadTicket(self):
        from kforge.dom.ticket import Ticket
        self.registry.registerDomainClass(Ticket)
        self.registry.tickets = Ticket.createRegister()
        Ticket.principalRegister = self.registry.tickets

    def loadProject(self):
        from kforge.dom.project import Project 
        self.registry.registerDomainClass(Project)
        self.registry.projects = Project.createRegister()
        Project.principalRegister = self.registry.projects

    def loadLicense(self):
        from kforge.dom.license import License  
        self.registry.registerDomainClass(License)
        from kforge.dom.license import ProjectLicense  
        self.registry.registerDomainClass(ProjectLicense)
        self.registry.licenses = License.createRegister()
        License.principalRegister = self.registry.licenses
        self.registry.loadBackgroundRegister(self.registry.licenses)

    def loadService(self):
        from kforge.dom.service import Service
        self.registry.registerDomainClass(Service)
        #self.registry.services = Service.createRegister()
        #Service.principalRegister = self.registry.services

    def loadMember(self):
        from kforge.dom.member import Member
        self.registry.registerDomainClass(Member)
        #self.registry.members = Member.createRegister()
        #Member.principalRegister = self.registry.members

    def loadFeedEntry(self):
        from kforge.dom.feedentry import FeedEntry
        self.registry.registerDomainClass(FeedEntry)
        self.registry.feedentries = FeedEntry.createRegister()
        FeedEntry.principalRegister = self.registry.feedentries

    def loadImage(self): # Replace dm.dom stuff -- kforge does not need Image
        pass

    def loadMemoryDump(self):
        from dm.dom.memory import MemoryDump
        self.registry.registerDomainClass(MemoryDump)
        self.registry.memoryDumps = MemoryDump.createRegister()

