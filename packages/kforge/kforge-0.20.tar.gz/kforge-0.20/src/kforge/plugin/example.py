"""
Example plugin module.

To create a new KForge plugin:

    1. Duplicate this example.py module with the new (lowercase) plugin name.
    2. Rename the Example class after the new (CamelCase) plugin name.
    3. Edit the createPlugin() method below to use your new (CamelCase) plugin class.
    4. Implement the various on() methods appropriately.
    5. Deploy your new plugin by adding the (lowercase) plugin name to plugin.conf file.

    *  Write unittest class for the example. Also provide indications for changing this file.

"""

import kforge.plugin.base
from kforge.ioc import *
import os

debug = RequiredFeature('Debug')

class Plugin(kforge.plugin.base.ServicePlugin):
    "Example plugin."

    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        self.counts = {}
        self.counts['onRun'] = 0
        self.counts['onProjectCreate'] = 0
        self.counts['onProjectUpdate'] = 0
        self.counts['onProjectApprove'] = 0
        self.counts['onProjectDelete'] = 0
        self.counts['onProjectUndelete'] = 0
        self.counts['onProjectPurge'] = 0
        self.counts['onPersonCreate'] = 0
        self.counts['onPersonUpdate'] = 0
        self.counts['onPersonApprove'] = 0
        self.counts['onPersonDelete'] = 0
        self.counts['onPersonUndelete'] = 0
        self.counts['onPersonPurge'] = 0
        self.counts['onMemberCreate'] = 0
        self.counts['onMemberUpdate'] = 0
        self.counts['onMemberApprove'] = 0
        self.counts['onMemberDelete'] = 0
        self.counts['onMemberUndelete'] = 0
        self.counts['onMemberPurge'] = 0
        self.counts['onServiceCreate'] = 0
        self.counts['onServiceUpdate'] = 0
        self.counts['onServiceApprove'] = 0
        self.counts['onServiceDelete'] = 0
        self.counts['onServiceUndelete'] = 0
        self.counts['onServicePurge'] = 0

    def onRun(self, sender):
        if debug:
            self.logger.debug("Example plugin received onRun event.")
        self.counts['onRun'] += 1

    def onProjectCreate(self, project):
        if debug:
            self.logger.debug("Example plugin received onProjectCreate event!")
        self.counts['onProjectCreate'] += 1

    def onProjectUpdate(self, project):
        if debug:
            self.logger.debug("Example plugin received onProjectUpdate event!")
        self.counts['onProjectUpdate'] += 1

    def onProjectApprove(self, project):
        if debug:
            self.logger.debug("Example plugin received onProjectApprove event!")
        self.counts['onProjectApprove'] += 1

    def onProjectDelete(self, project):
        if debug:
            self.logger.debug("Example plugin received onProjectDelete event!")
        self.counts['onProjectDelete'] += 1

    def onProjectUndelete(self, project):
        if debug:
            self.logger.debug("Example plugin received onProjectUndelete event!")
        self.counts['onProjectUndelete'] += 1

    def onProjectPurge(self, project):
        if debug:
            self.logger.debug("Example plugin received onProjectPurge event!")
        self.counts['onProjectPurge'] += 1

    def onPersonCreate(self, person):
        if debug:
            self.logger.debug("Example plugin received onPersonCreate event!")
        self.counts['onPersonCreate'] += 1 

    def onPersonUpdate(self, person):
        if debug:
            self.logger.debug("Example plugin received onPersonUpdate event!")
        self.counts['onPersonUpdate'] += 1

    def onPersonApprove(self, person):
        if debug:
            self.logger.debug("Example plugin received onPersonApprove event!")
        self.counts['onPersonApprove'] += 1

    def onPersonDelete(self, person):
        if debug:
            self.logger.debug("Example plugin received onPersonDelete event!")
        self.counts['onPersonDelete'] += 1

    def onPersonUndelete(self, person):
        if debug:
            self.logger.debug("Example plugin received onPersonUndelete event!")
        self.counts['onPersonUndelete'] += 1

    def onPersonPurge(self, person):
        if debug:
            self.logger.debug("Example plugin received onPersonPurge event!")
        self.counts['onPersonPurge'] += 1

    def onMemberCreate(self, member):
        if debug:
            self.logger.debug("Example plugin received onMemberCreate event!")
        self.counts['onMemberCreate'] += 1

    def onMemberUpdate(self, member):
        if debug:
            self.logger.debug("Example plugin received onMemberUpdate event!")
        self.counts['onMemberUpdate'] += 1

    def onMemberApprove(self, member):
        if debug:
            self.logger.debug("Example plugin received onMemberApprove event!")
        self.counts['onMemberApprove'] += 1

    def onMemberDelete(self, member):
        if debug:
            self.logger.debug("Example plugin received onMemberDelete event!")
        self.counts['onMemberDelete'] += 1
    
    def onMemberUndelete(self, member):
        if debug:
            self.logger.debug("Example plugin received onMemberUndelete event!")
        self.counts['onMemberUndelete'] += 1
    
    def onMemberPurge(self, member):
        if debug:
            self.logger.debug("Example plugin received onMemberPurge event!")
        self.counts['onMemberPurge'] += 1
    
    def onServiceUpdate(self, service):
        if debug:
            self.logger.debug("Example plugin received onServiceUpdate event!")
        self.counts['onServiceUpdate'] += 1

    def onServiceCreate(self, service):
        if debug:
            self.logger.debug("Example plugin received onServiceCreate event!")
        self.counts['onServiceCreate'] += 1
        # Todo: Put this under test.
        if self.isOurs(service):
            indexContent = """
<html>
  <head>
    <title>%s</title>
  </head>
  <body>
    <h1>Hello World!</h1>
    <h2>About</h2>
    <p>%s services are provided to the %s project by the KForge example plugin.</p>
    <h2>Specification of Service</h2>
    <ul>
      <li>Print 'Hello World!'.</li>
    </ul>
  </body>
</html>
    """ % (service.name.capitalize(), service.name.capitalize(), service.project.getLabelValue())
            servicePath = self.paths.getServicePath(service)
            try:
                os.makedirs(servicePath)
                indexPath = os.path.join(servicePath, 'index.html')
                indexFile = open(indexPath, 'w')
                indexFile.write(indexContent.encode('ascii', 'xmlcharrefreplace'))
                indexFile.close()
            except Exception, inst:
                msg = "ExamplePlugin: Couldn't create service files: %s" % str(inst)
                raise Exception(msg)

    def onServiceApprove(self, service):
        if debug:
            self.logger.debug("Example plugin received onServiceApprove event!")
        self.counts['onServiceApprove'] += 1

    def onServiceDelete(self, service):
        if debug:
            self.logger.debug("Example plugin received onServiceDelete event!")
        self.counts['onServiceDelete'] += 1
    
    def onServiceUndelete(self, service):
        if debug:
            self.logger.debug("Example plugin received onServiceUndelete event!")
        self.counts['onServiceUndelete'] += 1
    
    def onServicePurge(self, service):
        super(Plugin, self).onServicePurge(service)
        if debug:
            self.logger.debug("Example plugin received onServicePurge event!")
        self.counts['onServicePurge'] += 1

    def trashServiceFolder(self, service):
        servicePath = self.paths.getServicePath(service)
        self.paths.assertTrashFolder()
        trashPath = self.paths.getTrashPath()
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
            msg = "Couldn't move service files to trash: moving %s to %s: %s" % (
                servicePath, trashNew, inst
            )
    
    def getApacheConfig(self, service, configVars):
        # E.g. protect with access control, alias to the project path.
        configVars['fsPath'] = self.paths.getServicePath(service)
        # Todo: Figure out why this matches the "/login/ + urlPath" locations.
        apacheConfigTmpl = """
<IfModule mod_wsgi.c>
<Location %(urlPath)s>
%(modWsgiAccessControl)s
</Location>
Alias %(urlPath)s %(fsPath)s
</IfModule>
<IfModule !mod_wsgi.c>
<IfModule mod_python.c>
<Location %(urlPath)s>
%(modPythonAccessControl)s
</Location>
Alias %(urlPath)s %(fsPath)s
</IfModule>
</IfModule>
"""
        return apacheConfigTmpl % configVars

    def getUserHelp(self, service, serviceLocation):
        return """
<p>These are instructions on how to use this example service. The service
online location is:<a href="%(url)s">%(url)s</a></p>
<p>The resource will be available once the service configuration has been loaded (check the status). 
Access the resource by clicking on the link to the location.
</p> """ % {'url': serviceLocation}

