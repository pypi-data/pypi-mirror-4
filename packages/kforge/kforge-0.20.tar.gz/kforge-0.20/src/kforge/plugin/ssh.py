"""KForge SSH Plugin

Enabling the 'ssh' plugin means that project developers will be able to access
Subversion, Git and Mercurial version control system services via SSH.

When the 'ssh' plugin is enabled, registered users will be able to upload SSH
public keys, see a list of SSH keys they have uploaded, and delete keys
invidually. An 'authorized_keys' file will be rewritten as public keys are
registered and deleted (if necessary, use a cron job to copy this file to SSH
user's authorized_keys file). The resulting 'authorized_keys' file entries will
all have the KForge SSH handler as the SSH "command". The KForge SSH handler
resolves, authorizes and executes SSH requests, and will not operate unless the
'ssh' plugin is enabled.

Instructions for accessing repositories with SSH is presented on Git and
Mercurial service pages.

Platform dependencies:

  * SSH server. The SSH server is used to authenticate users by public-private
    key, and then to pass on the authenticated SSH request to the KForge SSH
    handler. For example, on Debian the openssh-server package must be installed
    and enabled.

KForge configuration file:

  * You may wish to set the path to the SSH authorized_keys file, the username
    of the SSH account, and the hostname of the SSH server.

[ssh]
authorized_keys_file = ~/.ssh/authorized_keys
user_name = %(user_name)s
host_name = %(domain_name)s

You can enable, disable, and show status in the usual way.

  $ kforge-admin plugin enable ssh
  $ kforge-admin plugin show ssh
  $ kforge-admin plugin disable ssh

"""
import os
import commands
import shutil
from subprocess import Popen, PIPE
import shlex
import kforge.plugin.base
from kforge.dictionarywords import *
from kforge.plugin.base import dictionary, setWord

SSH_AUTHORIZED_KEYS_PATH = ConfigFileSetting('ssh.authorized_keys_file')
SSH_USER_NAME = SystemUserSetting('ssh.user_name')
SSH_HOST_NAME = DomainNameSetting('ssh.host_name')
setWord(SSH_USER_NAME, dictionary[SYSTEM_USER_NAME])
setWord(SSH_HOST_NAME, dictionary[SITE_HOST])
defaultKeysPath = os.path.join('/home', dictionary[SSH_USER_NAME], '.ssh', 'authorized_keys')
setWord(SSH_AUTHORIZED_KEYS_PATH, defaultKeysPath)


class Plugin(kforge.plugin.base.NonServicePlugin):
    "SSH plugin."

    settings = [SSH_AUTHORIZED_KEYS_PATH, SSH_USER_NAME, SSH_HOST_NAME]
    
    def getAuthorizedKeysPath(self):
        path = self.dictionary[SSH_AUTHORIZED_KEYS_PATH]
        return os.path.expanduser(path)
    getAuthorizedKeysPath = classmethod(getAuthorizedKeysPath)

    def isFileWritable(self, path):
        return os.path.isfile(path) and os.access(path, os.W_OK)
    isFileWritable = classmethod(isFileWritable)

    def onSshKeyCreate(self, sshKey):
        self.writeAuthorizedKeysFile()

    def onSshKeyDelete(self, sshKey):
        self.writeAuthorizedKeysFile(excludeSshKey=sshKey)

    def onCreate(self):
        self.writeAuthorizedKeysFile()
        super(Plugin, self).onCreate()

    def sync(self):
        self.writeAuthorizedKeysFile()

    def writeAuthorizedKeysFile(self, excludeSshKey=None):
        # Todo: Improve this simple implementation: probably want to delegate 
        # to a script which can be run by configured command, possibly with 
        # sudo if SSH user != Apache user, but which can alternatively be run
        # as a cron job?

        handlerPath = os.path.join(self.dictionary[VIRTUALENVBIN_PATH], 'kforge-ssh-handler')
        configPath = os.path.join(self.dictionary[SYSTEM_CONFIG_PATH])
        sshOptions = ',no-port-forwarding,no-agent-forwarding,no-X11-forwarding,no-pty'
        sshCommands = ''
        for sshKey in self.registry.sshKeys:
            if sshKey == excludeSshKey:
                continue
            keyId = sshKey.id
            keyString = sshKey.keyString
            sshCommand = 'command="%s %s %s"%s %s\n'
            sshCommand %= (handlerPath, configPath, keyId, sshOptions, keyString)
            sshCommands += sshCommand
        authorizedKeysPath = self.getAuthorizedKeysPath()
        self.logger.info("Writing SSH keys to file: %s" % authorizedKeysPath)
        if not os.path.exists(authorizedKeysPath):
            sshDirPath =  os.path.dirname(authorizedKeysPath)
            umask = os.umask(0o067)
            try:
                if not os.path.exists(sshDirPath):
                    os.makedirs(sshDirPath)
                os.umask(0o027)
                open(authorizedKeysPath, 'w').close()
            except Exception, inst:
                msg = "Unable to create SSH authorized keys file: %s: %s" % (authorizedKeysPath, inst)
                self.logger.error("Error: %s" % msg)
                raise Exception, msg
            finally:
                os.umask(umask)
        elif os.access(authorizedKeysPath, os.X_OK):
            p = Popen(shlex.split(authorizedKeysPath), stdin=PIPE, stdout=PIPE, stderr=PIPE)
            stdoutdata, stderrdata = p.communicate(stdindata)
            if p.wait(): 
                msg = "Couldn't write SSH keys using file: :%s" % (authorizedKeysPath, stderrdata)
                self.logger.error("Error: %s" % msg)
                raise Exception, msg
        elif os.access(authorizedKeysPath, os.W_OK):
            try:
                f = open(authorizedKeysPath, 'w')
                f.write(sshCommands)
                f.close()
            except Exception, inst:
                msg = "Couldn't write SSH keys to file: %s: %s" % (authorizedKeysPath, inst)
                self.logger.error("Error: %s" % msg)
                raise Exception, msg
        else:
            msg = "Couldn't write SSH keys to file (file exists but is neither writable nor executable): %s" % authorizedKeysPath
            self.logger.error("Error: %s" % msg)
            raise Exception, msg


