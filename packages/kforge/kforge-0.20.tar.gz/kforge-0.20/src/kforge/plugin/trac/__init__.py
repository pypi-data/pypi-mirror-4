"""KForge Trac Plugin

Enabling this plugin allows KForge project administrators to create Trac project services.

Creating services with this plugin requires:

  * Trac. The 'trac-admin' command is used to create Trac environments. It depends on the Trac Python library. 

Providing access to this plugin's services requires:

  * Trac. The Trac Python library is used to handle requests. Trac's htdocs is required for older versions.
  * Apache. The mod_python Apache module is used by KForge to provide access to Trac through Apache. For example, on Debian the libapache2-mod-python package must be installed and enabled.

Using Git repositories with Trac projects (optional) requires:

  * Trac's Git plugin. For example, on Debian the trac-git package can be installed.

If using Trac v0.11 or later, you do not need to add anything to the KForge config file. Otherwise, if necessary add the following section to your KForge configuration file. Set the 'admin_script' if trac-admin is available on the executable path. Set the 'templates_path' if you are using a version of Trac earlier than version 0.11. Set the 'htdocs_path' if your Trac pages aren't finding their static resources (style sheets, images, etc.). Please note, if you are using Trac v0.11 or later, this section is no longer required.

[trac]
# Path to Trac admin script.
#admin_script = /path/to/trac-admin
# Path to trac templates (only for < 0.11).
#templates_path = /usr/share/trac/templates
# Path to htdocs files (will be served at /trac).
#htdocs_path = /usr/share/trac/htdocs

You can enable, disable, and show status in the usual way.

  $ kforge-admin plugin enable trac
  $ kforge-admin plugin show trac
  $ kforge-admin plugin disable trac


"""
from kforge.dictionarywords import *
from kforge.plugin.trac.dictionarywords import *
from kforge.plugin.base import ServicePlugin
from kforge.plugin.trac.command.admin import InitialiseTracEnvironment
from kforge.plugin.trac.command.admin import UpgradeTracEnvironment
from kforge.plugin.trac.command.admin import TracRepositoryAdd
from kforge.plugin.trac.command.admin import TracRepositorySetType
from kforge.plugin.trac.command.admin import TracRepositoryResync
from kforge.plugin.trac.command.admin import TracRepositoryRemove
from kforge.plugin.trac.command.config import SetTracConfigOptions
from kforge.plugin.trac.command.perm import SetTracPermissions
from kforge.plugin.trac.command.pref import SetTracPreferences
from kforge.plugin.trac.command.ticket import CreateTracTicket
from kforge.plugin.trac.command.ticket import UpdateTracTicket
from kforge.plugin.trac.command.ticket import ListTracTicketIds
from kforge.plugin.trac.command.ticket import CreateOrUpdateTicket
from kforge.plugin.trac.dom import TracProject
from kforge.plugin.git import GIT_ADMIN_SCRIPT
from kforge.url import UrlScheme
import os
import distutils.version
import commands


class Plugin(ServicePlugin):
    "Trac plugin."

    modelExtnClassName = 'TracProject'
    tracModule = None

    settings = [TRAC_ADMIN_SCRIPT, TRAC_HTDOCS_PATH, TRAC_WSGI_SCRIPT_PATH, TRAC_WSGI_PROCESS_GROUP, TRAC_ADMIN_PERMS, TRAC_VIEW_PERMS, TRAC_WRITE_PERMS, TRAC_SET_PREFS_FOR_ALL_PEOPLE]

    @classmethod
    def getTracModule(self):
        if self.tracModule == None:
            import trac
            self.tracModule = trac
        return self.tracModule
    
    def getRegister(self):
        domainClass = self.getModelExtnClass()
        return domainClass.createRegister(keyName='service')

    def checkDependencies(self):
        errors = []
        try:
            trac = self.getTracModule()
        except:
            errors.append("Couldn't import Trac Python library.")
        return errors

    def showDepends(self):
        messages = []
        msg = "Trac Python library: "
        try:
            trac = self.getTracModule()
        except:
            msg += "Not found! %s" % importTracOutput
        else:
            tracVersion = distutils.version.LooseVersion(trac.__version__)
            tracPath = trac.__path__[0]
            msg += "Found OK. Trac %s in %s." % (tracVersion, tracPath)
        messages.append(msg)
        return messages

    showDepends = classmethod(showDepends)
    
    def onServiceCreate(self, service):
        if self.isOurs(service):
            if not self.getTracProject(service):
                self.paths.assertServiceFolder(service)
                tracProject = self.register.create(service)
                try:
                    self.initialiseTracEnvironment(tracProject)
                    tracProject.isEnvironmentInitialised = True
                    tracProject.save()
                except:
                    tracProject.delete()
                    raise
                self.buildAndReloadApacheConfig()

    # Todo: Write test, delete repository service tracked by Trac service
    # and check repository is no longer tracked.
    def onServiceDelete(self, service):
        domainClass = self.registry.getDomainClass('TracRepository')
        register = domainClass.createRegister()
        for tracRepository in register.findDomainObjects(repository=service):
            tracRepository.delete()
        self.buildAndReloadApacheConfig()

    def onServicePurge(self, service):
        try:
            if self.isOurs(service):
                tracProject = self.getTracProject(service)
                if tracProject:
                    tracProject.delete()
        finally:
            super(Plugin, self).onServicePurge(service)

    def getTracProjects(self, member):
        services = [s for s in member.project.services if self.isOurs(s)]
        tracProjectRegister = self.getRegister()
        # Be careful about getting TracProjects, they are sometimes missing.
        tracProjects = []
        for service in services:
            tracProject = self.getTracProject(service)
            if tracProject != None:
                tracProjects.append(tracProject)
        return tracProjects

    def getTracProject(self, service):
        # Be careful about getting TracProject, they are sometimes missing.
        if service in self.register:
            return self.register[service]
        else:
            msg = "TracProject object not found for service: %s" % service
            self.logger.error(msg)
        return None

    def isReadyToReload(self, service):
        return service in self.register and self.register[service].isEnvironmentInitialised

    def initialiseTracEnvironment(self, tracProject):
        InitialiseTracEnvironment(tracProject).execute()
        self.setTracConfigFileOptions(tracProject)
        self.setTracPermissions(tracProject)
        self.setTracPreferencesForTracProject(tracProject)
    
    def setTracConfigFileOptions(self, tracProject):
        urlBuilder = UrlScheme()
        servicePath = urlBuilder.getServicePath(tracProject.service)
        serviceUrl = 'http://%s%s' % (self.dictionary[SITE_HOST], servicePath)
        settings = []
        # - configure email notification options
        # Note well, writing SMTP account details into the trac.ini file could
        # cause them to be revealed to users who are able to see the trac.ini file.
        # That would happen if the DAV plugin is enabled. It would also happen if
        # the trac.ini file is exposed for editing.
        settings += [
            ('notification', 'smtp_from', self.dictionary[SERVICE_EMAIL]),
            ('notification', 'smtp_replyto', self.dictionary[SERVICE_EMAIL]),
            ('notification', 'smtp_server', self.dictionary[SMTP_HOST]),
            ('notification', 'smtp_port', self.dictionary[SMTP_PORT]),
            ('notification', 'always_notify_owner', 'true'),
            ('notification', 'always_notify_reporter', 'true'),
            ('notification', 'always_notify_updater', 'true'),
            ('notification', 'smtp_user', self.dictionary[SMTP_USER]),
            ('notification', 'smtp_password', self.dictionary[SMTP_PASSWORD]),
            ('notification', 'use_tls', self.dictionary[SMTP_USE_TLS]),
            ('notification', 'smtp_enabled', self.dictionary[ENABLE_EMAIL_SENDING] and 'true' or 'false'),
        ]
        # - set banner image
        settings += [
            ('header_logo', 'src', 'common/trac_banner.png'),
            ('header_logo', 'alt', 'Trac service'),
            ('header_logo', 'link', serviceUrl),
        ]
        # - enable drop-down menu for owner
        settings += [
            ('ticket', 'restrict_owner', 'true'),
        ]
        # - set 'task' as default ticket type 
        settings += [
            ('ticket', 'default_type', 'task'),
        ]
        # - set charset to UTF8
        settings += [
            ('trac', 'default_charset', 'utf8'),
        ]
        # - set base URL
        settings += [
            ('trac', 'base_url', serviceUrl),
        ]
        # - enable svn, mercurial, git 
        settings += [
            ('components', 'tracext.hg.*', 'enabled'),
            ('components', 'tracext.git.*', 'enabled'),
            ('components', 'tracopt.versioncontrol.git.*', 'enabled'),
            ('components', 'tracopt.versioncontrol.svn.*', 'enabled'),
            ('git', 'git_bin', self.dictionary[GIT_ADMIN_SCRIPT]),
        ]
        # - enable ticket deleter
        settings += [
            ('components', 'tracopt.ticket.deleter', 'enabled'),
        ]
        self.setTracConfigOptions(tracProject, settings)

    def setTracConfigOptions(self, tracProject, settings):
        self.logger.debug("Setting trac config: %s" % settings)
        SetTracConfigOptions(tracProject, settings).execute()

    def setTracPermissions(self, tracProject):
        # Set Trac permissions.
        # - revoke all permissions for 'authenticated' and 'anonymous' users
        # - grant appropriate permission for each project member
        permSpecs = [
            'revoke authenticated *',
            'revoke anonymous *',
        ]
        for member in tracProject.service.project.members:
            permSpecs += self.getMemberPermSpecs(member)
        SetTracPermissions(tracProject, permSpecs).execute()

    def onTracRepositoryCreate(self, tracRepository):
        self.clearConfigRepositoryDir(tracRepository.tracProject)
        # Add repo without passing repostype, then set repo type, then resync.
        # Seems to be something odd about running trac-admin (sometimes says:
        # "'git' is not supported").
        TracRepositoryAdd(tracRepository).execute()
        TracRepositorySetType(tracRepository).execute()
        if tracRepository.repository.plugin.name != 'svn':
            TracRepositoryResync(tracRepository).execute()
        self.setRepositorySyncPerRequest(tracRepository)

    def onTracRepositoryDelete(self, tracRepository):
        self.clearConfigRepositoryDir(tracRepository.tracProject)
        TracRepositoryRemove(tracRepository).execute()
        self.setRepositorySyncPerRequest(tracRepository, isDeleting=True)

    def clearConfigRepositoryDir(self, tracProject):
        settings = [('trac', 'repository_dir', None)]
        self.setTracConfigOptions(tracProject, settings)

    def setRepositorySyncPerRequest(self, tracRepository, isDeleting=False):
        # Set the svn repositories in 'repository_sync_per_request' option.
        if tracRepository.repository.plugin.name == 'svn':
            option = 'repository_sync_per_request'
            tracProject = tracRepository.tracProject
            r = [i.repository for i in tracProject.repositories]
            s = [i.name for i in r if i.plugin.name == 'svn']
            if isDeleting:
                deletingName = tracRepository.repository.name
                # Condition shouldn't be necessary.
                if deletingName in s:
                    s.remove(deletingName) 
            value = ",".join(s) or '""'
            settings = [('trac', option, value)]
            self.setTracConfigOptions(tracProject, settings)

    def onPersonCreate(self, person):
        self.setTracPreferencesForPerson(person)

    def onPersonUpdate(self, person):
        self.setTracPreferencesForPerson(person)

    def onPersonDelete(self, person):
        self.setTracPreferencesForPerson(person, clear=True)

    def onEmailAddressCreate(self, emailAddress):
        self.setTracPreferencesForPerson(emailAddress.person)

    def onEmailAddressUpdate(self, emailAddress):
        self.setTracPreferencesForPerson(emailAddress.person)

    def onMemberCreate(self, member):
        for tracProject in self.getTracProjects(member):
            permSpecs = self.getMemberPermSpecs(member)
            SetTracPermissions(tracProject, permSpecs).execute()
        self.setPreferencesForMember(member)

    def onMemberUpdate(self, member):
        for tracProject in self.getTracProjects(member):
            permSpecs = self.getMemberPermSpecs(member)
            SetTracPermissions(tracProject, permSpecs).execute()
        
    def onMemberDelete(self, member):
        for tracProject in self.getTracProjects(member):
            subject = self.getTracPermissionSubject(member.person)
            permSpecs = ['revoke %s *' % subject]
            SetTracPermissions(tracProject, permSpecs).execute()
        self.setPreferencesForMember(member, clear=True)
    
    def getMemberPermSpecs(self, member):
        # If person can create with plugin, then set admin perms.
        # Else, if person can update with the plugin, then set view and write perms.
        # Else, if person can read with the plugin, then set view perms.
        person = member.person
        project = member.project
        perms = []
        if self.isAccessAuthorised(person, 'Create', project):
            perms += self.getTracPermsFromDictionary(TRAC_ADMIN_PERMS)
        elif self.isAccessAuthorised(person, 'Update', project):
            perms += self.getTracPermsFromDictionary(TRAC_VIEW_PERMS)
            perms += self.getTracPermsFromDictionary(TRAC_WRITE_PERMS)
        elif self.isAccessAuthorised(person, 'Read', project):
            perms += self.getTracPermsFromDictionary(TRAC_VIEW_PERMS)
        subject = self.getTracPermissionSubject(person)
        permSpecs = ['revoke %s *' % subject]
        for perm in perms:
            permSpecs.append('grant %s %s' % (subject, perm))
        return permSpecs

    def getTracPermissionSubject(self, person):
        if person.name == self.dictionary[VISITOR_NAME]:
            subject = 'anonymous'
        else:
            subject = person.name
        return subject

    def isAccessAuthorised(self, person, actionName, project):
        return self.accessController.isAccessAuthorised(person=person, 
            actionName=actionName, protectedObject=self.domainObject,
            project=project, avoidMemos=True)

    def getTracPermsFromDictionary(self, dictionaryWord):
        perms = self.dictionary[dictionaryWord]
        return [p.strip() for p in perms.split(',')]

    def listDependencies(self):
        dependencies = super(Plugin, self).listDependencies()
        dependencies.append('svn')
        return dependencies
        
    listDependencies = classmethod(listDependencies)

    def getMetaDomainObject(self):
        return TracProject.meta

    def getStatusMessage(self, service):
        """Provide a service status message.
        """
        tracProject = self.getTracProject(service)
        if tracProject:
            if tracProject.isEnvironmentInitialised:
                msg = super(Plugin, self).getStatusMessage(service)
            else:
                msg = "Error: Trac project environment not initialised."
        else:
            msg = "Error: Trac project object is missing in model."
        return msg

    def getApacheConfigCommon(self):
        return ""
    
    def buildWsgiFile(self):
        path = self.dictionary[TRAC_WSGI_SCRIPT_PATH]
        content = self.createWsgiScriptContent()
        purpose = 'Trac WSGI script'
        self.filesystem.writeWsgiFile(path, content, purpose)

    def createWsgiScriptBody(self, pythonPathActivation):
        wsgiScriptVars = {
            'pythonPathActivation': pythonPathActivation,
            'systemConfigPath': self.dictionary[SYSTEM_CONFIG_PATH],
        }
        wsgiScriptTmpl = """
# KForge auto-generated Trac WSGI File.

import os
import sys

%(pythonPathActivation)s

def application(environ, start_response):
    os.environ['KFORGE_SETTINGS'] = '%(systemConfigPath)s'

    if 'PYTHON_EGG_CACHE' in environ:
        os.environ['PYTHON_EGG_CACHE'] = environ['PYTHON_EGG_CACHE']
    elif 'trac.env_path' in environ:
        os.environ['PYTHON_EGG_CACHE'] = os.path.join(environ['trac.env_path'],
                                                      '.egg-cache')
    elif 'trac.env_path_parent_dir' in environ:
        os.environ['PYTHON_EGG_CACHE'] = os.path.join(environ['trac.env_path_parent_dir'],
                                                      '.egg-cache')
    from kforge.handlers.modwsgi import WsgiAccessControlHandler
    from trac.web.main import dispatch_request
    access_control = WsgiAccessControlHandler(dispatch_request)
    return access_control(environ, start_response)
"""    
        return wsgiScriptTmpl % wsgiScriptVars

    def getApacheConfig(self, service, configVars):
        configVars['wsgiScriptPath'] = self.dictionary[TRAC_WSGI_SCRIPT_PATH]
        configVars['wsgiProcessGroup'] = self.dictionary[TRAC_WSGI_PROCESS_GROUP]
        if self.dictionary[VIRTUALENVBIN_PATH]:
            configVars['tracHandlerName'] = 'kforgevirtualenvhandlers::trachandler'
        else:
            trac = self.getTracModule()
            tracVersion = distutils.version.LooseVersion(trac.__version__)
            v0_9 = distutils.version.LooseVersion('0.9')
            if tracVersion < v0_9:
                configVars['tracHandlerName'] = 'trac.ModPythonHandler'
            else:
                configVars['tracHandlerName'] = 'trac.web.modpython_frontend'
        configVars['tracHtdocsPath'] = self.dictionary[TRAC_HTDOCS_PATH] 
        if configVars['tracHtdocsPath']:
            apacheConfigTmpl = """
Alias %(urlPath)s/chrome %(tracHtdocsPath)s
"""
        else:
            apacheConfigTmpl = ''
        apacheConfigTmpl += """
<IfModule mod_wsgi.c>
WSGIScriptAlias %(urlPath)s %(wsgiScriptPath)s
WSGIApplicationGroup %%{GLOBAL}
WSGIProcessGroup %(wsgiProcessGroup)s
<Location %(urlPath)s>
SetEnv trac.env_path %(fileSystemPath)s
WSGIPassAuthorization On
</Location>
</IfModule>
<IfModule !mod_wsgi.c>
<IfModule mod_python.c>
<Location %(urlPath)s>
SetHandler mod_python
PythonHandler %(tracHandlerName)s
PythonInterpreter main_interpreter
PythonOption TracEnv %(fileSystemPath)s
PythonOption TracUriRoot %(urlPath)s

%(modPythonAccessControl)s
</Location>
</IfModule>
</IfModule>
"""
        return apacheConfigTmpl % configVars
    
    def backup(self, service, backupPathBuilder):
        backupPath = backupPathBuilder.getServicePath(service)
        os.system('%s %s hotcopy %s' % (self.dictionary[TRAC_ADMIN_SCRIPT], service.getDirPath(), backupPath))

    def sync(self):
        for service in self.domainObject.services:
            self.syncService(service)

    def syncService(self, service):
        # Check trac project object exists, otherwise create it.
        tracProject = self.getTracProject(service)
        if not tracProject:
            tracProject = self.register.create(service)

        # Check environment actually exists.
        if not tracProject.hasEnvironment():
            return

        # Check trac project object attribute 'isEnvironmentInitialised' is True.
        if not tracProject.isEnvironmentInitialised:
            tracProject.isEnvironmentInitialised = True
            tracProject.save()

        # Upgrade environment.
        UpgradeTracEnvironment(tracProject).execute()

        # Sync tickets from Trac environment.
        for tracTicketId in ListTracTicketIds(tracProject).execute():
            CreateOrUpdateTicket(tracProject, tracTicketId).execute()

        # Set preferences for all members of service's project.
        self.setTracPreferencesForTracProject(tracProject, clear=True)

        # Set permissions for all members of service's project.
        permSpecs = []
        for member in service.project.members:
            permSpecs += self.getMemberPermSpecs(member)
        SetTracPermissions(tracProject, permSpecs).execute()

        # Update Trac config file options.
        self.setTracConfigFileOptions(tracProject)

    def onTicketCreate(self, ticket):
        if not ticket or not self.isOurs(ticket.service):
            return    
        if ticket.ref:
            # KForge ticket was created from an existing Trac ticket.
            pass
        else:
            # KForge ticket was created before a corresponding Trac ticket.
            ticketData = ticket.asDictValues()
            tracProject = ticket.service.getExtnObject()
            ticketId = CreateTracTicket(tracProject, ticketData).execute()
            ticket.ref = str(ticketId)
            ticket.saveSilently()

    def onTicketUpdate(self, ticket):
        if not ticket or not self.isOurs(ticket.service):
            return
        if not ticket.ref:
            return
        tracProject = ticket.service.getExtnObject()
        tracTicketId = ticket.ref
        tracTicketData = ticket.asDictValues()
        UpdateTracTicket(tracProject, tracTicketId, tracTicketData).execute()

# Todo: onTicketDelete() Problem being what resolution should be given?

# Note on setting preferences.
#
# If setting preferences for all people on all tracs:
#  - set preferences for each person when trac is created
#  - set preferences on each trac when person is created
#  - set preferences on each trac when person is updated
#  - remove preferences for person on each trac when person is deleted
#  - set preferences for each person on each trac when plugin is sync-ed
# 
# If not setting preferences for all project on all tracs:
#  - set preferences for each project member when trac is created
#  - set preferences on each project trac when member is created
#  - set preferences on each project trac for each membership when person is updated
#  - remove preferences for each project trac when member is deleted
#  - remove preferences on each project trac for each membership when person is deleted
#  - set preferences for each project member on each project trac when plugin is sync-ed

# Therefore:
#  case1: maintain preferences for all people on all tracs
#  case2: maintain preferences for all people on tracs they can access
#  event1: when trac service is created:
#    case1: set prefs for all people on one trac
#    case2: set prefs for all people with access on one trac
#  event2: when person is created:
#    case1: set prefs for one person on all tracs
#    case2: set prefs for one person on tracs s/he can access
#  event3: when person (email or fullname) is updated:
#    case1: set prefs for one person on all tracs
#    case2: set prefs for one person on tracs s/he can access
#  event4: when person (email of fullname) is deleted:
#    case1: clear prefs for one person on all tracs
#    case2: clear prefs for one person on tracs s/he can access
#  event5: when membership is created:
#    case1: do nothing
#    case2: set prefs for one person on associated tracs (complication for visitor)
#  event7: when membership is deleted:
#    case1: do nothing
#    case2: clear prefs for one person on associated tracs (complication for visitor)
#  event8: when trac plugin is synced:
#    case1: set prefs for all people on all tracs
#    case2: clear all prefs, and set prefs for all people on tracs s/he can access
#  event9: when grant is created
#  event10: when grant is deleted
#
#  where 'can access' means 'can update'? or assume if visitor is a member then all can access

    def setTracPreferencesForTracProject(self, tracProject, clear=False):
        if self.dictionary[TRAC_SET_PREFS_FOR_ALL_PEOPLE]:
            people = self.registry.people
        else:
            if clear:
                people = self.registry.people
                self.setTracPreferences([tracProject], people, clear=True)
            people = [m.person for m in tracProject.service.project.members]
        self.setTracPreferences([tracProject], people)

    def setTracPreferencesForPerson(self, person, clear=False):
        if self.dictionary[TRAC_SET_PREFS_FOR_ALL_PEOPLE]:
            tracProjects = self.registry.tracProjects
        else:
            tracProjects = []
            for membership in person.memberships:
                for service in membership.project.services:
                    if self.isOurs(service):
                        tracProject = self.getTracProject(service)
                        if tracProject:
                            tracProjects.append(tracProject)
        self.setTracPreferences(tracProjects, [person], clear=clear)

    def setPreferencesForMember(self, member, clear=False):
        if not self.dictionary[TRAC_SET_PREFS_FOR_ALL_PEOPLE]:
            tracProjects = []
            for service in member.project.services:
                if self.isOurs(service):
                    tracProject = self.getTracProject(service)
                    if tracProject:
                        tracProjects.append(tracProject)
            self.setTracPreferences(tracProjects, [member.person], clear=clear)

    def setTracPreferences(self, tracProjects, people, clear=False):
        for tracProject in tracProjects:
            preferences = []
            for person in people:
                if person.name == self.dictionary[VISITOR_NAME]:
                    continue
                name = person.name
                if clear:
                    fullname = ''
                    email = ''
                else:
                    fullname = person.fullname
                    email = person.email
                preferences.append((person.name, fullname, email))
            SetTracPreferences(tracProject, preferences).execute()

