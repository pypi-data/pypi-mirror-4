"""KForge Mailman plugin

Enabling this plugin allows KForge project administrators to create Mailman mailing list services.

Creating services with this plugin requires:

  * Mailman. The 'newlist' and 'rmlist' commands are used to create and delete mailing lists.

Providing access to this plugin's services requires:

  * Apache. The mailman web interface should be  running (see the mailman installation instructions for how to set this up).
  * A mail transport agent (e.g. Exim, Postfix).

You do not need to add anything to the KForge config file. However, if you
wish to put the mailing list in a domain that is different from your KForge
domain, then adjust the [mailman] section of your KForge configuration file,
setting the variables as needed for your system.

You can enable, disable, and show status in the usual way.

  $ kforge-admin plugin enable mailman
  $ kforge-admin plugin show mailman
  $ kforge-admin plugin disable mailman

"""
import os
import commands
import shutil
import shlex
import kforge.plugin.base
import kforge.utils.backup
from kforge.ioc import RequiredFeature
from kforge.dictionarywords import *
from random import Random
import string
from kforge.command import KforgeCommandError
from kforge.command.emailmailmanpassword import EmailMailmanPassword
from kforge.plugin.base import dictionary, setWord

MAILMAN_NEWLIST = ShellCmdSetting('mailman.newlist')
MAILMAN_RMLIST = ShellCmdSetting('mailman.rmlist')
MAILMAN_ADD_MEMBERS = ShellCmdSetting('mailman.add_members')
MAILMAN_REMOVE_MEMBERS = ShellCmdSetting('mailman.remove_members')
MAILMAN_URLHOST = DomainNameSetting('mailman.urlhost')
MAILMAN_EMAILHOST = DomainNameSetting('mailman.emailhost')
defaultHost = 'lists.%s' % dictionary[DNS_DOMAIN_NAME] 
setWord(MAILMAN_NEWLIST, 'sudo newlist')
setWord(MAILMAN_RMLIST, 'sudo rmlist')
setWord(MAILMAN_ADD_MEMBERS, 'sudo add_members')
setWord(MAILMAN_REMOVE_MEMBERS, 'sudo remove_members')
setWord(MAILMAN_URLHOST, defaultHost)
setWord(MAILMAN_EMAILHOST, defaultHost)

# Todo: Handler for email address change events (unsubscribe and resubscribe).

class Plugin(kforge.plugin.base.ServicePlugin):
    "Mailman plugin."

    settings = [MAILMAN_NEWLIST, MAILMAN_RMLIST, MAILMAN_URLHOST, MAILMAN_EMAILHOST]
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
    
    def onServiceCreate(self, service):
        if self.isOurs(service):
            self.assertServicesFolder(service)
            # Establish variables.
            listName = self.getListName(service)
            emailAddress = self.getAdminEmail(service)
            password = ''.join( Random().sample(string.letters+string.digits, 8) )
            # Create list (mailman sends emails).
            self.createMailingList(
                listName=listName,
                adminEmail=emailAddress,
                adminPass=password,
            )
            # Log result.
            msg = 'MailmanPlugin: Created service list %s.' % listName
            self.log(msg)
            # Email password to project admins.
            try:
                cmd = EmailMailmanPassword(password=password,
                        project=service.project, listName=listName)
                cmd.execute()
            except KforgeCommandError, inst:
                msg = "Error sending password for '%s' list: %s" % (self.listName, inst)
                self.logger.error(msg)
            # Add all existing members to the list (mailman sends emails).
            for member in service.project.members:
                try:
                    self.addMemberToList(member, service)
                except Exception, inst:
                    msg = "Couldn't add member to mailman list: %s %s: %s" % (member, service, inst)
                    self.logger.error(msg)
            # Finally, once all emails have been sent, do Apache config.
            self.buildAndReloadApacheConfig()

    def onServicePurge(self, service):
        if self.isOurs(service):
            listName = self.getListName(service)
            self.deleteMailingList(
                listName=listName
            )
            msg = 'MailmanPlugin: Deleted service list %s.' % listName
            self.log(msg)

    def onMemberCreate(self, member):
        for service in self.getMailmanServices(member):
            try:
                self.addMemberToList(member, service)
            except Exception, inst:
                msg = "Couldn't add member to mailman list: %s %s: %s" % (member, service, inst)
                self.logger.error(msg)

    def onMemberDelete(self, member):
        for service in self.getMailmanServices(member):
            try:
                self.removeMemberFromList(member, service)
            except Exception, inst:
                msg = "Couldn't remove member from mailman list: %s %s: %s" % (member, service, inst)
                self.logger.error(msg)

    def getMailmanServices(self, member):
        return [s for s in member.project.services if self.isOurs(s)]
        
    def addMemberToList(self, member, service):
        if member.person.name == 'visitor':
            return
        # Add regular member from stdin, send welcome msg, and msg to admin.
        listName = self.getListName(service)
        emailAddress = member.person.email
        if not (listName and emailAddress and member.person.fullname):
            return
        fullname = member.person.getLabelValue()
        fullname = fullname.encode('utf8')
        emailSpec = fullname + ' <' + str(member.person.email) + '>'
        cmd = shlex.split(self.dictionary[MAILMAN_ADD_MEMBERS])
        cmd += ['-r', '-', '-a', 'y', '-w', 'y', listName]
        self.runPopen(cmd, stdindata=emailSpec)

    def removeMemberFromList(self, member, service):
        # Add regular member from stdin, send welcome msg, and msg to admin.
        listName = self.getListName(service)
        emailAddress = member.person.email
        if not (listName and emailAddress):
            return
        cmd = shlex.split(self.dictionary[MAILMAN_REMOVE_MEMBERS])
        cmd += [listName, emailAddress]
        self.runPopen(cmd)

    def getListName(self, service):
        return service.project.name + '-' + service.name

    def getAdminEmail(self, service):
        adminRole = self.registry.roles['Administrator']
        for member in service.project.members:
            if member.role.name == adminRole.name:
                return member.person.email

    def getApacheConfig(self, service, configVars):
        configVars['hostname'] = self.dictionary[MAILMAN_URLHOST]
        configVars['baseUrl'] = 'http://%s/mailman/listinfo/' % configVars['hostname']
        configVars['listUrl'] = configVars['baseUrl'] + self.getListName(service)
        apacheConfigTmpl = """
Redirect %(urlPath)s %(listUrl)s
"""
        return apacheConfigTmpl % configVars
    
    def backup(self, service, backupPathBuilder):
        # TODO
        pass

   # Todo: Change to reflect usage and options of Mailman's newlist command.
    def createMailingList(self, listName, adminEmail, adminPass):
        cmd = shlex.split(self.dictionary[MAILMAN_NEWLIST])
        if self.dictionary[MAILMAN_URLHOST]:
            cmd += ['--urlhost', self.dictionary[MAILMAN_URLHOST]]
        if self.dictionary[MAILMAN_EMAILHOST]:
            cmd += ['--emailhost', self.dictionary[MAILMAN_EMAILHOST]]
        cmd += ['-q', listName, adminEmail, adminPass]
        try:
            self.runPopen(cmd)
        except Exception, inst:
            if "List already exists" in str(inst):
                raise Exception, "Mailman list '%s' already exists." % listName
            else:
                msg = "Error creating list: %s" % inst
                self.logger.error(msg)
                raise Exception, "Couldn't create '%s' Mailman list (see log for defails)." % listName

    def deleteMailingList(self, listName=''):
        """Delete mailing list with name listName.
        
        NB: listName *cannot* include domain name.
        """
        cmd = shlex.split(self.dictionary[MAILMAN_RMLIST])
        cmd += ['-a', listName]
        self.runPopen(cmd)

    def runCommand(self, cmd, input=''):
        status, output = commands.getstatusoutput(cmd)
        if status:
            msg = "Mailman error: cmd '%s' caused error: %s" % (cmd, output)
            raise Exception(msg)

