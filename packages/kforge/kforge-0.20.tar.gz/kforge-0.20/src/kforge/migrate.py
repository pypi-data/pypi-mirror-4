from dm.migrate import FilesDumper
from dm.migrate import DomainModelLoader
from kforge.command.backup import BackupPathBuilder
import os
import shutil

class FilesDumper(FilesDumper):

    def dumpInDir(self, fileDumpDirPath):
        super(FilesDumper, self).dumpInDir(fileDumpDirPath)
        self.backupPathBuilder = BackupPathBuilder(fileDumpDirPath)
        self.dumpProjects()

    def dumpProjects(self):
        for project in self.registry.projects:
            self.dumpProjectFiles(project)

    def dumpProjectFiles(self, project):
        projectBackupPath = self.backupPathBuilder.getProjectPath(project)
        if os.path.exists(projectBackupPath):
            shutil.rmtree(projectBackupPath)
        os.makedirs(projectBackupPath)
        print "Dumping project: %s" % projectBackupPath 
        for service in project.services:
            projectPluginPath = self.backupPathBuilder.getProjectPluginPath(
                service
            )
            if not os.path.exists(projectPluginPath):
                os.makedirs(projectPluginPath)
            pluginSystem = service.plugin.getSystem()
            pluginSystem.backup(service, self.backupPathBuilder)


class DomainModelLoader(DomainModelLoader):

    def migrateDataDump(self):
        # Migrate from old to 0.19.
        if self.getDumpVersion().split('.') < '0.19'.split('.'):
            self.migrateDataDump__pre0_19__to__0_19()

        # Migrate from 0.19 to 0.20.
        if self.getDumpVersion() == '0.19':
            self.migrateDataDump__0_19__to__0_20()

        # Fix dumped URIs for tracProject (on TracRepository objects).
        if self.getDumpVersion() == '0.20':
            self.fixDataDump__0_20()

    def migrateDataDump__pre0_19__to__0_19(self):
        # Grant permission for members to leave projects.
        for (personId, person) in self.dataDump['Person'].items():
            if personId == 'metaData':
                continue
            if person['name'] == 'visitor':
                continue
            for projectName in person['memberships']:

                members = self.findInstances('Member', project=projectName, person=person['name'])
                if not members:
                    raise Exception, "Can't find membership object for person %s and project %s." % (person['name'], projectName)
                (memberId, member) = members.items()[0]

                protectionObjectName = 'Member.%s' % memberId
                self.addInstance('ProtectionObject',
                    name=protectionObjectName,
                )
                newPermissionId = self.addInstance('Permission',
                    action='Delete',
                    protectionObject=protectionObjectName,
                )
                self.addInstance('PersonalGrant',
                    person=person['name'],
                    permission=newPermissionId,
                )

        # Digest the passwords more, see dm.dom.meta.Password.makeDigest().
        from dm.messagedigest import hmac
        from dm.messagedigest import sha256
        from dm.dictionarywords import PASSWORD_DIGEST_SECRET
        for person in self.dataDump['Person'].values():
            md5hexdigest = person['password']
            key = self.dictionary[PASSWORD_DIGEST_SECRET]
            text = hmac(key=key, msg=md5hexdigest, digestmod=sha256).hexdigest()
            person['password'] = text
        # Update the version.
        self.setDumpVersion('0.19')

    def fixDataDump__0_20(self):
        # Fix tracProject attribute of tracRespository.
        tracRepositories = self.findInstances('TracRepository').items()
        for (tracRepositoryId, tracRepositoryData) in tracRepositories:
            # Incorrect value is the service URI.
            tracProjectUri = tracRepositoryData['tracProject']
            if '/services/' not in tracProjectUri:
                continue
            serviceUri = tracProjectUri
            # Use service URI to get associated trac projects (should only be one).
            tracProjects = self.findInstances('TracProject', service=serviceUri)
            #if len(tracProjects) != 1:
            #    print "Warning: There are %s trac projects for service: %s" % (len(tracProjects), serviceUri)
            #    for tracProjectId, tracProjectData in tracProjects.items():
            #        print tracProjectId, tracProjectData['isEnvironmentInitialised']
            for tracProjectId, tracProjectData in tracProjects.items():
                tracRepositoryData['tracProject'] = '/tracProjects/%s' % tracProjectId
        # Remove any PersonTicket objects.
        self.deleteDomainClass('PersonTicket')
        # Remove any 'apacheconfig' plugin object.
        for pluginId in self.findInstances('Plugin', name='apacheconfig').keys():
            self.deleteInstance('Plugin', pluginId)
        # Remove all FeedEntry instances.
        self.deleteDomainClass('FeedEntry')
        # Remove all sessions.
        self.deleteDomainClass('Session')
        # Remove all visitor personal grants.
        personalGrantIds = self.findInstances('PersonalGrant', person='/people/visitor').keys()
        for personalGrantId in personalGrantIds:
            self.deleteInstance('PersonalGrant', personalGrantId)
        # Todo: Add TracProject objects for trac services that don't have one.

    def migrateDataDump__0_19__to__0_20(self):
        # Move email addresses.
        self.dataDump['EmailAddress'] = {}
        self.dataDump['EmailAddress']['metaData'] = {'person': 'HasA', 'emailAddress': 'String'}
        for personId in self.getDomainClassIds('Person'):
            person = self.dataDump['Person'][str(personId)]
            emailAddressIds = [int(i) for i in self.dataDump['EmailAddress'].keys() if i != 'metaData']
            if len(emailAddressIds):
                emailAddressIds.sort(reverse=True)
                newEmailAddressId = emailAddressIds[0] + 1
            else:
                newEmailAddressId = 1
            newEmailAddressId = self.addInstance('EmailAddress',
                emailAddress=person['email'],
                person=person['name'],
            )

            self.addInstance('ProtectionObject',
                name='EmailAddress.%s' % newEmailAddressId,
            )
            for actionName in ['Read', 'Delete']:
                newPermissionId = self.addInstance('Permission',
                    action=actionName,
                    protectionObject='EmailAddress.%s' % newEmailAddressId,
                )
                self.addInstance('PersonalGrant',
                    person=person['name'],
                    permission=newPermissionId,
                )
        # Add pending state, if missing.
        states = self.findInstances('State', name='pending')
        if len(states) == 0:
            self.addInstance('State', name='pending')
        # Move pending members.
        for (memberId, member) in self.findInstances('PendingMember').items():
            member['state'] = 'pending'
            member['role'] = 'Friend'
            self.addInstance('Member', **member)
        self.deleteDomainClass('PendingMember')
        # Grant permission to read Role and License.
        for domainClassName in ['Role', 'License']:
            protectionObjects = self.findInstances('ProtectionObject', name=domainClassName)
            if len(protectionObjects) == 0:
                self.addInstance('ProtectionObject', name=domainClassName)
            elif len(protectionObjects) == 1:
                pass
            else:
                raise Exception, "There is already more than one protection object for '%s'." % domainClassName
            readPermissionIds = self.findInstances('Permission', protectionObject=domainClassName, action='Read').keys()
            if len(readPermissionIds) == 0:
                readPermissionId = self.addInstance('Permission', protectionObject=domainClassName, action='Read')
            elif len(readPermissionIds) == 1:
                readPermissionId = readPermissionIds[0]
            else:
                raise Exception, "There is already more than one read permission object for '%s'." % domainClassName
            for (roleId, role) in self.findInstances('Role').items():
                if roleId == 'metaData':
                    continue
                grants = self.findInstances('Grant', role=role['name'], permission=readPermissionId)
                if len(grants) == 0:
                    self.addInstance('Grant', role=role['name'], permission=readPermissionId)
        # Move the Trac repository service references.
        self.dataDump['TracRepository'] = {}
        self.dataDump['TracRepository']['metaData'] = {'repository': 'HasA', 'tracProject': 'HasA'}
        for (tracProjectId, tracProject) in self.findInstances('TracProject').items():
            repositoryId = tracProject['svn']
            if repositoryId == None:
                continue
            self.addInstance('TracRepository',
                tracProject=str(tracProjectId),
                repository=repositoryId,
            )
        # Update the version.
        self.setDumpVersion('0.20')

