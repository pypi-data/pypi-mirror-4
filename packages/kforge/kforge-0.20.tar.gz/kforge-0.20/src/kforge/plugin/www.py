"""
KForge www (project home) Plugin.

Enabling this plugin creates a project web directory (that is a directory on
the file system the contents of which are displayed at the project's url on the
KForge site).

## Installation ##

1. Dependencies. There are no dependencies beyond those required for KForge.

2. KForge config file. You do not need to add anything to the KForge config
   file.
"""
import os
import shutil

import kforge.plugin.base
import kforge.url

class Plugin(kforge.plugin.base.ServicePlugin):
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
    
    def onServiceCreate(self, service):
        """
        For www since a single service plugin only want the plugin directory
        and do not need a service subdirectory
        """
        if self.isOurs(service):
            fsPath = self.paths.getServicePath(service)
            self.paths.assertFolder(fsPath, 'project services')
            self.buildAndReloadApacheConfig()
    
    def getApacheConfig(self, service, configVars):
        # It's a Web site, so allow access to everyone -- even guest
        configVars['fsPath'] = self.paths.getServicePath(service)
        apacheConfigTmpl = """
Alias %(urlPath)s %(fsPath)s
"""
        return apacheConfigTmpl % configVars
