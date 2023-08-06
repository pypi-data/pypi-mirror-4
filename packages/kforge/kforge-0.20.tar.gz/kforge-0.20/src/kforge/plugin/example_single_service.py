"""
Example plugin module.
"""

import kforge.plugin.base

class Plugin(kforge.plugin.base.SingleServicePlugin):
    "Example 'single service' plugin."

    def onServiceCreate(self, service):
        if self.isOurs(service):
            self.buildAndReloadApacheConfig()

