from dm.dom.stateful import *
from kforge.ioc import RequiredFeature

registry = RequiredFeature('DomainRegistry')

# Todo: Support changing repository service used by Trac.
  
def getRepoChoices(objectRegister, domainObject):
    available = []
    if domainObject:
        serviceClass = registry.getDomainClass('Service')
        if isinstance(domainObject, serviceClass):
            service = domainObject
        else:
            # Todo: Find out more about this domainObject, it seems not to be the same type of thing each time (Service in API, Project otherwise?).
            service = domainObject.service
        for pluginName in ['svn', 'mercurial', 'git']:
            if pluginName not in registry.plugins:
                continue
            plugin = registry.plugins[pluginName]
            available += plugin.services.findDomainObjects(project=service.project)
        services = serviceClass.createRegister()
        services.sortDomainObjects(available)
    return [(s.getUri(), s.name) for s in available]


class TracConfigFile(Text):

    hiddenOptions = [
        'smtp_password',
        'smtp_port',
        'smtp_server',
        'smtp_user',
        'email_sender',
        'base_url',
        'use_tls',
        'git_bin',
        'database',
        'log_file',
        'plugins_dir',
        'templates_dir',
        'repository_dir',
    ]

    def setAttributeValue(self, domainObject, attrValue):
        oldValue = self.readConfigFile(domainObject)
        oldLines = {}
        smtp_password = ''
        for line in oldValue.split('\n'):
            for option in self.hiddenOptions:
                if line.strip().startswith(option):
                    oldLines[option] = line
                    break
        newLines = []
        for line in attrValue.split('\n'):
            line = line.rstrip('\r')
            for option in self.hiddenOptions:
                if line.strip().startswith(option):
                    line = oldLines[option]
                    break
            newLines.append(line)
        attrValue = '\n'.join(newLines)
        self.writeConfigFile(domainObject, attrValue)

    def createValueRepr(self, domainObject, absoluteUriPrefix=None):
        try:
            attrValue = self.readConfigFile(domainObject)
        except:
            attrValue = ''
        lines = []
        for line in attrValue.split('\n'):
            for option in self.hiddenOptions:
                if line.strip().startswith(option):
                    line = option + ' = **system-controlled**'
                    break
            lines.append(line)
        return '\n'.join(lines)

    def readConfigFile(self, domainObject):
        path = self.getConfigFilePath(domainObject)
        return open(path).read()

    def writeConfigFile(self, domainObject, attrValue):
        path = self.getConfigFilePath(domainObject)
        configFile = open(path, 'w')
        configFile.write(attrValue)
        configFile.close()

    def getConfigFilePath(self, domainObject):
        if domainObject.service == None:
            raise Exception, "TracProject object has no service object: %s" % domainObject.id
        path = domainObject.service.getDirPath()
        return os.path.join(path, 'conf', 'trac.ini')


class TracProject(DatedObject):
    "Definition of TracProject domain object."

    isUnique = False
    isEnvironmentInitialised = Boolean(isHidden=True)
    service = HasA('Service', comment='A trac service.', isRequired=False,
        isSystem=True)
    repositories = AggregatesMany('TracRepository', key='repository',
        owner='tracProject', getChoices=getRepoChoices, title='Repositories',
        comment='Tracked repository services.', isRequired=False)
    tickets = AggregatesMany('Ticket', key='id', owner='service', ownerAsOwnerAttr='service', isRequired=False)
    configfile = TracConfigFile()

    #ownerAttrNames = ['service']

    def getLabelValue(self):
        if self.service:
            return self.service.getLabelValue()
        else:
            return 'no-parent-service'

    def isOperational(self):
        if not self.isEnvironmentInitialised:
            return False
        return self.hasEnvironment()

    def hasEnvironment(self):
        path = self.service.getDirPath()
        internalTracPath = os.path.join(path, 'VERSION')
        return os.path.exists(internalTracPath)

# Todo: Define repository service class and add aggregates-many repositories (and make it a system attribute), so that trac-repository association objects are deleted when a service is purged, just like when a trac-project is purged?

class TracRepository(SimpleObject):
    "Associates a Trac project with a repository service."

    isImplicitAssociation = True

    repository = HasA('Service')
    tracProject = HasA('TracProject', isRequired=False)


registry.registerDomainClass(TracProject)
registry.registerDomainClass(TracRepository)
if not hasattr(registry, 'tracProjects'):
    registry.tracProjects = TracProject.createRegister()
    TracProject.principalRegister = registry.tracProjects

