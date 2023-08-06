# -*- coding=utf-8 -*-
from dm.command import Command
from dm.command.state import *
from dm.command.accesscontrol import GrantStandardSystemAccess, GrantStandardProjectAccess
from dm.command.person import *
from kforge.command.project import *
from dm.command.initialise import InitialiseDomainModelBase 
from kforge.dictionarywords import SERVICE_EMAIL
from kforge.dictionarywords import SITE_HOST
from kforge.dictionarywords import SYSTEM_MODE
from kforge.dictionarywords import VISITOR_ROLE
from kforge.dictionarywords import VISITOR_NAME
from kforge.dictionarywords import INITIAL_PERSON_ROLE

class InitialiseDomainModel(InitialiseDomainModelBase):
    """
    Creates default domain model objects.
    """
    
    def execute(self):
        super(InitialiseDomainModel, self).execute()
        self.createRoles()
        self.createProtectionObjects()
        self.createGrants()
        self.createRefusals()
        self.createAccessControlPlugin()
        self.createLicenses()
        self.createPersons()
        self.createProjects()
        self.createServicePlugins()
        if self.dictionary[SYSTEM_MODE] == 'development':
            self.createTestPlugins()
            self.setUpTestFixtures()
        self.createNotifyPlugin()
        self.commitSuccess()

    def createRoles(self):
        roles = self.registry.roles
        self.adminRole = roles.create('Administrator')
        self.developerRole = roles.create('Developer')
        self.friendRole = roles.create('Friend')
        self.visitorRole = roles.create('Visitor')
        
    def createProtectionObjects(self):
        self.registry.protectionObjects.create('Session')
        self.registry.protectionObjects.create('Member')
        self.registry.protectionObjects.create('System')
        self.registry.protectionObjects.create('Person')
        self.registry.protectionObjects.create('Plugin')
        self.registry.protectionObjects.create('Project')
        self.registry.protectionObjects.create('Role')
        self.registry.protectionObjects.create('Service')
        self.registry.protectionObjects.create('License')
        #self.registry.protectionObjects.create('Ticket')
        if self.dictionary[SYSTEM_MODE] == 'development':
            self.registry.protectionObjects.create('MemoryDump')

    def createGrants(self):
        self.grantAdministratorAccess()
        self.grantRegistrationAccess()
        self.grantStandardSystemAccess('Member')
        self.grantStandardSystemAccess('System')
        self.grantStandardSystemAccess('Person')
        #self.grantStandardSystemAccess('Plugin')
        self.grantStandardSystemAccess('Project')
        self.grantStandardSystemAccess('Role')
        self.grantStandardSystemAccess('Service')
        self.grantStandardSystemAccess('License')
        #self.grantStandardSystemAccess('Ticket')

    def grantAdministratorAccess(self):
        "Grants all permissions to Administrator role."
        for protectionObject in self.registry.protectionObjects:
            for permission in protectionObject.permissions:
                if not permission in self.adminRole.grants:
                    self.adminRole.grants.create(permission)

    def grantRegistrationAccess(self):
        "Grants 'Create Person' permission to all roles, but bar the Visitor."
        create = self.registry.actions['Create']
        protectionObjects = self.registry.protectionObjects
        for role in self.registry.roles:
            personProtection = protectionObjects['Person']
            createPerson = personProtection.permissions[create]
            if not createPerson in role.grants:
                role.grants.create(createPerson)
            projectProtection = protectionObjects['Project']
            createProject = projectProtection.permissions[create]
            if not createProject in role.grants:
                role.grants.create(createProject)

    def grantStandardSystemAccess(self, protectedName):
        protectionObject = self.registry.protectionObjects[protectedName]
        cmd = GrantStandardSystemAccess(protectionObject)
        cmd.execute()

    def grantReadAccess(self, protectedName):
        readAction = self.registry.actions['Read']
        protectionObject = self.registry.protectionObjects[protectedName]
        readPermission = protectionObject.permissions[readAction]
        for role in self.registry.roles:
            if readPermission not in role.grants:
                role.grants.create(readPermission)

    def createRefusals(self):
        pass

    def createLicenses(self):
        licenses = self.registry.licenses
        licenses.create(name='Other/Proprietary License')
        licenses.create(name='General Public License (GPL)')
        licenses.create(name='BSD')
        licenses.create(name='Creative Commons (Attribution, Share Alike)')
        licenses.create(name='Creative Commons (Attribution, Derivatives)')

    def createPersons(self):
        if self.dictionary[SERVICE_EMAIL]:
            adminEmailAddress = self.dictionary[SERVICE_EMAIL]
        else:
            adminEmailAddress ='kforge-admin@%s' % self.dictionary[SITE_HOST]
        cmd = PersonCreate('admin', 
            role=self.adminRole,
            fullname='Administrator',
        )
        cmd.execute()
        self.adminPerson = cmd.person
        self.adminPerson.setPassword('pass')
        self.adminPerson.save()
        self.adminPerson.setEmailAddress(adminEmailAddress)
        
        visitorRoleName = self.dictionary[VISITOR_ROLE]
        visitorRole = self.registry.roles[visitorRoleName]
        cmd = PersonCreate(self.dictionary[VISITOR_NAME],
            role = visitorRole,
            fullname='Visitor',
        )
        cmd.execute()
        self.visitorPerson = cmd.person
        projectProtection = self.registry.protectionObjects['Project']
        create = self.registry.actions['Create']
        createProject = projectProtection.permissions[create]
        if not createProject in self.visitorPerson.bars:
                self.visitorPerson.bars.create(createProject)
        
    def createProjects(self):
        cmd = ProjectCreate('administration')
        cmd.execute()
        self.adminProject = cmd.project
        self.adminProject.title = 'Administration'
        self.adminProject.save()
        self.adminProject.members.create(
            self.adminPerson, role=self.adminRole
        )
        self.adminProject.members.create(
            self.visitorPerson, role=self.visitorRole
        )
    
    def createAccessControlPlugin(self):
        plugins = self.registry.plugins
        plugins.create('notify')
    
    def createAccessControlPlugin(self):
        plugins = self.registry.plugins
        plugins.create('accesscontrol')
    
    def createNotifyPlugin(self):
        plugins = self.registry.plugins
        plugins.create('notify')
    
    def createServicePlugins(self):
        pass
    
    def createTestPlugins(self):
        plugins = self.registry.plugins
        plugins.create('example')
        plugins.create('example_single_service')
    
    def setUpTestFixtures(self):
        domainName = self.dictionary[SITE_HOST]
        personRoleName = self.dictionary[INITIAL_PERSON_ROLE]
        personRole = self.registry.roles[personRoleName]
        # do not reuse roles set in other methods as this method
        # should be callable on its own
        adminPerson = self.registry.people['admin']
        adminRole = self.registry.roles['Administrator']
        friendRole = self.registry.roles['Friend']

        cmd = PersonCreate('levin',
            role = personRole,
            fullname=u'Levin Ç\'është',
        )
        cmd.execute()
        levin = cmd.person
        levin.setPassword('levin')
        levin.save()
        levin.setEmailAddress('levin@%s' % domainName)
        
        cmd = PersonCreate('natasha',
            role = personRole,
            fullname=u'Natasha Что такое',
        )
        cmd.execute()
        natasha = cmd.person
        natasha.setPassword('natasha')
        natasha.save()
        natasha.setEmailAddress('natasha@%s' % domainName)

        visitor = self.registry.people[self.dictionary[VISITOR_NAME]]
        
        
        cmd = ProjectCreate('example')
        cmd.execute()
        exampleProject = cmd.project
        
        cmd = ProjectCreate('warandpeace')
        cmd.execute()
        warAndPeace = cmd.project
        warAndPeace.title = u'War and Peace Τί εἶναι τὸ'
        warAndPeace.save()
        cmd2 = ProjectCreate('annakarenina')
        cmd2.execute()
        annaKarenina = cmd2.project
        annaKarenina.title = u'Anna Karenina யூனிக்கோடு என்றால்'
        annaKarenina.save()
        
        exampleProject.members.create(adminPerson,  role=adminRole)
        warAndPeace.members.create(  natasha,    role=adminRole)
        warAndPeace.members.create(  visitor,    role=friendRole)
        annaKarenina.members.create( levin,      role=adminRole)
        
        examplePlugin = self.registry.plugins['example']
        exampleSingleService = self.registry.plugins['example_single_service']
        for project in [warAndPeace, annaKarenina, exampleProject]:
            project.services.create('example', plugin=examplePlugin)
            project.services.create('example_single_service', plugin=exampleSingleService)
    
    def tearDownTestFixtures(self):
        # [[TODO: factor this out into a command class]]
        def purgeProject(projectName):
            if self.registry.projects.has_key(projectName):
                self.registry.projects[projectName].delete()
            if self.registry.projects.getAll().has_key(projectName):
                self.registry.projects.getAll()[projectName].purge()
        purgeProject('warandpeace')
        purgeProject('annakarenina')
        
        def purgePerson(personName):
            if self.registry.people.has_key(personName):
                self.registry.people[personName].delete()
            if self.registry.people.getAll().has_key(personName):
                self.registry.people.getAll()[personName].purge()
        purgePerson('natasha')
        purgePerson('levin')
        purgePerson('anna')
        purgePerson('bolskonski')

