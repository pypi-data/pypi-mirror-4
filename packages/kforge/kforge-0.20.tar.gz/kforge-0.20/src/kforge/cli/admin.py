import dm.cli.admin
import dm.environment
from kforge.ioc import RequiredFeature
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'kforge.django.settings.main'

class AdministrationUtility(dm.cli.admin.AdministrationUtility):

    def buildApplication(self):
        import kforge.soleInstance
        self.appInstance = kforge.soleInstance.application

    def createFilesystem(self):
        #super(AdministrationUtility, self).createFilesystem()
        dm.cli.admin.AdministrationUtility.createFilesystem(self)
        dictionary = self.getSystemDictionary()
        from kforge.dictionarywords import PROJECTS_PATH
        projectsPath = dictionary[PROJECTS_PATH]
        if not os.path.exists(projectsPath):
            os.makedirs(projectsPath)

    def do_updatefeed(self, line=None):
        args = self.convertLineToArgs(line)
        if len(args) != 0:
            print 'Error: Unexpected arguments\n'
            self.help_updatefeed(line)
            return 1
        self.updateFeedEntries()

    def updateFeedEntries(self):
        # Loop over Trac projects.
        application = self.getApplication()
        accessController = RequiredFeature('AccessController')
        if 'trac' in application.registry.plugins:
            tracPlugin = application.registry.plugins['trac']
        else:
            print "Warning: The 'trac' plugin is not enabled."
            return 1
        from kforge.url import UrlScheme
        urls = UrlScheme()
        sourceUrls = []
        tracServices = tracPlugin.services
        print "Aggregating from the following locations (set 'domain_name' if necessary):"
        for service in tracServices:
            if accessController.isAccessAuthorised(None, 'Read', service.plugin, service.project):
                sourceUrl = urls.getServiceUrl(service) + '/timeline?ticket=on&changeset=on&milestone=on&wiki=on&max=50&daysback=90&format=rss'
                sourceUrls.append(sourceUrl)
                print sourceUrl
        application.registry.feedentries.readSources(sourceUrls)
        application.registry.feedentries.truncate()
        print "Feed summary now:"
        for e in application.registry.feedentries.listSummary():
            msg = u"%s %s %s" % (e.updated, e.source, e.title)
            print msg.encode('utf-8')

    def help_updatefeed(self, line=None):
        usage = \
'''kforge-admin updatefeed

Update feeds from site services.'''
        print usage

    def constructSystemDictionary(self):
        from kforge.dictionary import SystemDictionary
        return SystemDictionary()

    def do_plugin(self, line=None):
        args = self.convertLineToArgs(line)

        if len(args) == 0:
            print 'Error: Insufficient arguments\n'
            self.help_plugin(line)
            return 1
        actionName = args[0]
        if len(args) > 1:
            pluginName = args[1]
        else:
            pluginName = ''

        application = self.getApplication()
        pluginFactory = RequiredFeature('PluginFactory')
        availableNames = pluginFactory.getAvailableNames()

        hiddenServiceNames = ['accesscontrol']
        if actionName == 'available':
            availableNames.sort()
            for name in availableNames:
                if name not in hiddenServiceNames:
                    print name
            return 0
        if actionName == 'enabled':
            for plugin in application.registry.plugins:
                if plugin.name not in hiddenServiceNames:
                    print plugin.name
            return 0
        if not pluginName:
            print 'Error: Plugin name required. See command help for details.'
            return 1
        if actionName == 'enable':
            if pluginName not in application.registry.plugins:
                try:
                    plugin = application.registry.plugins.create(pluginName)
                    if not plugin.getSystem():
                        raise Exception("Cannot load '%s' plugin." % pluginName)
                    # Check dependencies.
                    dependencyErrors = plugin.getSystem().checkDependencies()
                    if dependencyErrors:
                        print "Error: The plugin's dependencies didn't check out:"
                        for e in dependencyErrors:
                            print e
                        plugin.delete()
                        plugin.purge()
                        print
                        print "Please refer to 'plugin doc %s' for information about this plugin." % pluginName
                        return 1
                    # Check configuration.
                    configurationErrors = []
                    pluginSystem = plugin.getSystem()
                    pluginSystem.checkSettings(errors=configurationErrors)
                    if configurationErrors:
                        print "Error: The plugin's settings didn't check out:"
                        for e in configurationErrors:
                            print e
                        plugin.delete()
                        plugin.purge()
                        print
                        print "Please refer to 'plugin doc %s' for information about this plugin." % pluginName
                        return 1
                    else:
                        msg = '''The '%s' plugin is now enabled (see 'doc' and 'show').''' % (pluginName)
                        print msg
                        return 0
                except Exception, inst:
                    if pluginName in application.registry.plugins:
                        del(application.registry.plugins[pluginName])
                    msg = "Error: Couldn't enable '%s' plugin: %s" % (pluginName, str(inst))
                    print msg
                    return 1
            else:
                msg = '''The '%s' plugin is already enabled.''' % (pluginName)
                print msg
                return 0
        elif actionName == 'show' or actionName == 'status':
            try:
                pluginClass = pluginFactory.getPluginClass(pluginName)
                if not pluginClass:
                    raise Exception("No plugin named '%s'." % pluginName)
            except Exception, inst:
                print "Error: %s" % str(inst)
                return 1
            print "Package: %s" % pluginClass.__module__
            try:
                pluginObject = application.registry.plugins[pluginName]
            except:
                pluginObject = None
            pluginState = bool(pluginObject) and 'enabled' or 'disabled'
            print "State: %s" % pluginState
            print "Dependencies:"
            for line in pluginClass.showDepends():
                print " %s" % line
            pluginServices = pluginObject and pluginObject.services or []
            settingErrors = []
            results = pluginClass.checkSettings(errors=settingErrors)
            print "Settings%s:" % (settingErrors and " (there are errors)" or "")
            for result in results:
                print " %s" % result
            from kforge.plugin.base import NonServicePlugin
            if not issubclass(pluginClass, NonServicePlugin):
                print "Services:"
                paths = RequiredFeature('FileSystem')
                for service in pluginServices:
                    print " %s %s %s" % (service.project.name, service.name, str(paths.getServicePath(service)))

            if settingErrors:
                print
                print "Warning: The settings are not okay (see above)."
                print
           
        elif actionName == 'sync':
            if pluginName not in application.registry.plugins:
                msg = "The '%s' plugin is not active." % pluginName
                print msg
                return 0
            plugin = application.registry.plugins[pluginName]
            pluginSystem = plugin.getSystem()
            if pluginSystem:
                pluginSystem.sync()
            else:
                print "Error: No plugin system for '%s'." % pluginName
                return 1

        elif actionName == 'disable':
            if pluginName not in application.registry.plugins:
                msg = "The '%s' plugin is not enabled." % (pluginName)
                print msg
                return 1
            plugin = application.registry.plugins[pluginName]
            if plugin.services:
                msg = "The '%s' plugin has active services, so cannot be disabled." % pluginName
                print msg
                return 1
            from kforge.plugin.base import NonServicePlugin
            isNonServicePlugin = isinstance(plugin.getSystem(), NonServicePlugin)
            plugin.delete()
            print "The '%s' plugin is now disabled." % pluginName
            return 0
        elif actionName == 'doc':
            # Todo: Move docstring into plugin class from module.
            try:
                plugin_system = pluginFactory.getPluginClass(pluginName)
                pluginPackage = __import__(plugin_system.__module__, '', '', '*')
                print pluginPackage.__doc__
                return 0
            except Exception, inst:
                msg = "Couldn't get doc for '%s' plugin: %s" % (
                    pluginName, str(inst)
                )
                print msg
                return 1
        else:
            self.help_plugin()
            return 1

    def help_plugin(self, line=None):
        usage = \
'''kforge-admin plugin available

    list the plugins that are available

kforge-admin plugin enabled

    list the plugins that are enabled

kforge-admin plugin doc PLUGIN

    documentation on the specified plugin including details of any
    additional software that needs to be installed to use the plugin's
    functionality.

kforge-admin plugin show PLUGIN

    inidicate status of the plugin, indicates status of dependencies, and
    lists all project services that have been created with this plugin.

kforge-admin plugin enable PLUGIN

    enable the specified plugin on this KForge service.

kforge-admin plugin disable PLUGIN

    disable the specified plugin on this KForge service. Warning: you
    will not be able to delete a plugin if it has any associated services.

kforge-admin plugin sync PLUGIN

    for trac: refresh KForge tickets from Trac project tickets
    for ssh: rewrite SSH authorized keys file
    for others: nothing is effected
'''
        print usage

    def backupSystemService(self):
        application = self.getApplication()
        commandSet = application.commands
        backupCommandName = 'Backup'
        backupCommand = commandSet[backupCommandName](self.args[0])
        backupCommand.execute()

    def createFilesDumper(self):
        from kforge.migrate import FilesDumper
        return FilesDumper()

    def getDomainModelLoaderClass(self):
        from kforge.migrate import DomainModelLoader
        return DomainModelLoader

    def takeDatabaseAction(self, actionName):
        from kforge.utils.db import Database
        db = Database()
        actionMethod = getattr(db, actionName)
        actionMethod()

    def upgradeSystemServiceDatabase(self):
        # TODO fix this to be generic
        import kforge.utils.upgrade
        dbCommand = kforge.utils.upgrade.UpgradeDbTo0Point14()
        dbCommand.execute()
        # print 'No changes required.'

    def upgradeSystemServiceFilesystem(self):
        # ditto here with filesystem
        # should make this generic 
        # import kforge.utils.upgrade
        # filesystemCommand = kforge.utils.upgrade.UpgradeDataTo0Point11(
        #     self.servicePath, self.systemPath
        # )
        # filesystemCommand.execute()
        # nothing in fact to do
        print 'No changes required.'

    def getApacheConfigBuilderClass(self):
        from kforge.apache.config import ApacheConfigBuilder
        return ApacheConfigBuilder

    def getSystemName(self):
        return "KForge"
        
    def getSystemVersion(self):
        import kforge
        return kforge.__version__
        
    def createAboutMessage(self):
        systemName = self.getSystemName()
        systemVersion = self.getSystemVersion()
        return '%s %s' % (systemName, systemVersion)

    def touchMigratedDomainModel(self):
        application = self.getApplication()
        system = application.registry.systems[1]
        version = system.version.split('.')

        ## Migrate versions earlier than v0.19.
        #version_0_19 = '0.19'.split('.')
        #if version < version_0_19:
        #   self.migrateDataDump__pre0_19__to__0_19()
        #   version = version_0_19

        ## Migrate from v0.19 to v0.20.
        #version_0_20 = '0.20'.split('.')
        #if version == version_0_19:
        #   self.migrateDataDump__0_19__to__0_20()
        #   version = version_0_20


    def migrateDataDump__pre0_19__to__0_19(self):
        # Update system version number.
        application = self.getApplication()
        system = application.registry.systems[1]
        system.version = '0.19'
        system.save()

        # Grant permission for members to leave projects.
        from dm.strategy import CreateProtectionObject
        for person in application.registry.people:
            for membership in person.memberships:
                protectionObject = CreateProtectionObject(membership).create()
                deleteAction = application.registry.actions['Delete']
                deletePermission = protectionObject[deleteAction]
                if not deletePermission in person.grants:
                    person.grants.create(deletePermission)

        # Digest the passwords more, see dm.dom.meta.Password.makeDigest().
        from dm.messagedigest import hmac
        from dm.messagedigest import sha256
        from dm.dictionarywords import PASSWORD_DIGEST_SECRET
        dictionary = self.constructSystemDictionary()
        for person in application.registry.people:
            md5hexdigest = person.password
            key = dictionary[PASSWORD_DIGEST_SECRET]
            text = hmac(key=key, msg=md5hexdigest, digestmod=sha256).hexdigest()
            person.password = text
            person.save()
        
    def migrateDataDump__0_19__to__0_20(self):
        # Update system version number.
        application = self.getApplication()
        system = application.registry.systems[1]
        system.version = '0.20'
        system.save()


class UtilityRunner(dm.cli.admin.UtilityRunner):

    systemName = 'kforge'
    utilityClass = AdministrationUtility
    usage  = """Usage: %prog [options] [command]

Administer a KForge service, including its domain objects. 

To obtain information about the commands available run the "help" command.

    $ kforge-admin help

Domain objects (e.g. people, projects, etc) can be administered by starting
a python shell from within interactive mode. Run "help shell" for more details.

Report bugs to <bugs@appropriatesoftware.net>."""

