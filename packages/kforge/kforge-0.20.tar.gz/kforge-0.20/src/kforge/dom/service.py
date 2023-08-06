import os
import kforge.regexps
from dm.dom.stateful import *
from kforge.command import ProjectPluginList

serviceNameRegex = '^%s$' % (kforge.regexps.serviceName)

def getPluginChoices(objectRegister, domainObject):
    command = kforge.command.ProjectPluginList(objectRegister.owner)
    try:
        command.execute()
    except KforgeCommandError:
        return []
    else:
        return [(p.getUri(), p.name) for p in command.results]
    

class Service(DatedStatefulObject):
    "Project service."

    hasModelExtn = True

    name = String(isIndexed=True, isUnique=True, isRequired=True, isImmutable=True, regex=serviceNameRegex, minLength=1, maxLength=256)
    plugin  = HasA('Plugin', isImmutable=True, getChoices=getPluginChoices)
    project = HasA('Project', isImmutable=True)

    isUnique = False
    ownerAttrNames = ['project', 'services']
    sortOnName = 'name'

    projectUrls = RequiredFeature('UrlScheme')

    def checkProjectPluginDir(self):
        if not self.hasProjectPluginDir():
            self.createProjectPluginDir()

    def hasProjectPluginDir(self):
        return os.path.exists(self.getProjectPluginDirPath())

    def createProjectPluginDir(self):
        if not self.hasProjectPluginDir():
            os.makedirs(self.getProjectPluginDirPath())

    def getProjectPluginDirPath(self):
        return self.paths.getProjectPluginPath(self.project, self.plugin)

    def hasDir(self):
        return os.path.exists(self.getDirPath())

    def createDir(self):
        if not self.hasDir():
            os.makedirs(self.getDirPath())

    def getDirPath(self):
        return self.paths.getServicePath(self)

    def getUrlPath(self):
        return self.projectUrls.getServicePath(self)

    def getUrl(self):
        return self.projectUrls.getServiceUrl(self)

    def getUserHelp(self, serviceLocation):
        return self.plugin.getSystem().getUserHelp(self, serviceLocation)

    def getStatusMessage(self):
        return self.plugin.getSystem().getStatusMessage(self)

    def getLabelValue(self):
        return "%s-%s" % (
            self.project.getLabelValue(),
            self.name,
        )

    def getExtnRegister(self):
        return self.plugin.getExtnRegister()

    def getExtnObject(self):
        return self.plugin.getExtnObject(self)

    def isReadyToReload(self):
        return self.plugin and self.plugin.isReadyToReload(self)

    def asDictValues(self, *args, **kwds):
        data = super(Service, self).asDictValues()
        data['status'] = self.getStatusMessage()
        return data

    def resolvePathPart(self, pathPart, **kwds):
        if self.getExtnRegister():
            extnObject = self.getExtnObject()
            try:
                attrValue = extnObject.resolvePathPart(pathPart, **kwds)
            except KforgeAttributeError:
                attrValue = super(Service, self).resolvePathPart(pathPart, **kwds)
        return attrValue

