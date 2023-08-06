import unittest

def suite():
    import kforge.test.developer
    suites = [
        kforge.test.developer.suite(),
    ]
    return unittest.TestSuite(suites)


class RequiresPlugins(unittest.TestCase):

    requiredPlugins = []

    def setUp(self):
        self.enabledPlugins = []
        for pluginName in self.requiredPlugins:
            if pluginName not in self.registry.plugins:
                plugin = self.registry.plugins.create(pluginName)
                self.enabledPlugins.append(plugin)
        super(RequiresPlugins, self).setUp()

    def tearDown(self):
        super(RequiresPlugins, self).tearDown()
        for plugin in self.enabledPlugins:
            plugin.delete()
            #plugin.purge()

