import unittest
from kforge.test.customer.plugin.base import PluginTestCase
import commands
from kforge.dictionary import *
from kforge.plugin.ssh import SSH_USER_NAME
from kforge.plugin.ssh import SSH_HOST_NAME

def suite():
    suites = [
        unittest.makeSuite(TestGitAccess),
        unittest.makeSuite(TestSvnAccess),
        unittest.makeSuite(TestMercurialAccess),
        unittest.makeSuite(TestSshKeyRegistration),
        unittest.makeSuite(TestSshKeyRegistrationFailBase64),
    ]
    return unittest.TestSuite(suites)

# Todo: Svn SSH access (is harder because we don't get told the service path in the command).
# Or given we know the user, create symlinks according to user, and start svnserve in
# user's folder (access control by only making symlinks to repos the user can write to. Will
# need to run checks whenever a repository is created/deleted and when a member is created/
# updated/deleted and when any access control objects (roles etc.) are changed....

class SshTestCase(PluginTestCase):

    requiredPlugins = None

    def setUp(self):
        super(SshTestCase, self).setUp()
        self.urlPersonSshKeys = self.url_for('people.admin', person=self.kuiPersonName,
            subcontroller='sshKeys')
        self.urlPersonSshKeyCreate = self.url_for('people.admin', person=self.kuiPersonName,
            subcontroller='sshKeys', action='create')

    def createSshKey(self):
        sshKeyIds = set(self.registry.sshKeys.keys())
        sshKeyString = self.getSshKeyString()
        params = {
            'keyString': sshKeyString,
        }
        self.postAssertCode(self.urlPersonSshKeyCreate, params)
        sshKeyId = (set(self.registry.sshKeys.keys()) - set(sshKeyIds)).pop()
        return sshKeyId

    def deleteSshKey(self, sshKeyId):
        url = self.url_for('people.admin', person=self.kuiPersonName,
            subcontroller='sshKeys', action='delete', id=sshKeyId)
        self.postAssertCode(url, {'Submit':'Delete'}, code=302)

    def getSshKeyString(self):
        keyString = ''
        paths = ['~/.ssh/id_rsa.pub', '~/.ssh/id_dsa.pub']
        for path in paths:
            s,o = commands.getstatusoutput('cat %s' % path)
            if not s:
                keyString = o
                break
        assert keyString, "Couldn't read SSH key: %s" % paths
        return keyString.strip()

    def svnCheckout(self, serviceName, expectCheckoutFail=False):
        url = 'svn+ssh://%('+SSH_USER_NAME+')s@%('+SSH_HOST_NAME+')s'
        url %= self.dictionary
        url += self.getServicePath(serviceName)
        cmd = 'svn co %s %s' % (url, serviceName)
        if self.system(cmd):
            if not expectCheckoutFail:
                self.fail('Failed to checkout: %s' % self.lastStatusOutput)
        elif expectCheckoutFail:
            self.fail('Checkout was a success, but failure was expected.')

    def mercurialClone(self, serviceName, expectCloneFail=False):
        url = 'ssh://%('+SSH_USER_NAME+')s@%('+SSH_HOST_NAME+')s'
        url %= self.dictionary
        url += self.getServicePath(serviceName)
        cmd = 'hg clone %s %s' % (url, serviceName)
        if self.system(cmd):
            if not expectCloneFail:
                self.fail('Failed to clone: %s' % self.lastStatusOutput)
        elif expectCloneFail:
            self.fail('Clone was a success, but failure was expected.')

    def gitClone(self, serviceName, expectCloneFail=False):
        url = '%('+SSH_USER_NAME+')s@%('+SSH_HOST_NAME+')s:'
        url %= self.dictionary
        url += self.getServicePath(serviceName)
        cmd = 'git clone %s %s' % (url, serviceName)
        if self.system(cmd):
            if not expectCloneFail:
                self.fail('Failed to clone: %s' % self.lastStatusOutput)
        elif expectCloneFail:
            self.fail('Clone was a success, but failure was expected.')
        

class SshAccessTestCase(SshTestCase):

    def setUp(self):
        super(SshAccessTestCase, self).setUp()
        self.sshKeyId = self.createSshKey()

    def tearDown(self):
        self.deleteSshKey(self.sshKeyId)
        super(SshAccessTestCase, self).tearDown()


class TestGitAccess(SshAccessTestCase):

    requiredPlugins = ['ssh', 'git']

    def testAccess(self):
        # As project administrator.
        for name in ['git', 'git2', 'git3', 'git4', 'git5']:
            self.createService('git', name)
        self.gitCloneAddCommitPush('git', 'Testing Git SSH access (project admin)...')
        # As project developer.
        self.changePersonProjectRole('Developer')
        self.gitCloneAddCommitPush('git2', 'Testing Git SSH access (project developer)...')
        # As project friend.
        self.changePersonProjectRole('Friend')
        self.gitCloneAddCommitPush('git3', 'Testing Git SSH access (project friend)...', expectPushFail=True)
        # As project visitor.
        self.changePersonProjectRole('Visitor')
        self.gitCloneAddCommitPush('git4', 'Testing Git SSH access (project visitor)...', expectCloneFail=True)
        # As project administrator, again.
        self.changePersonProjectRole('Administrator')
        self.gitCloneAddCommitPush('git5', 'Testing Git SSH access (project admin, again)...')


class TestSvnAccess(SshAccessTestCase):

    requiredPlugins = ['ssh', 'svn']

    def testAccess(self):
        # As project administrator.
        for name in ['svn', 'svn2', 'svn3', 'svn4', 'svn5']:
            self.createService('svn', name)
        self.svnCheckoutAddCommit('svn', 'Testing Subversion SSH access (project admin)...')
        # As project developer.
        self.changePersonProjectRole('Developer')
        self.svnCheckoutAddCommit('svn2', 'Testing Subversion SSH access (project developer)...')
        # As project friend.
        self.changePersonProjectRole('Friend')
        self.svnCheckoutAddCommit('svn3', 'Testing Subversion SSH access (project friend)...', expectCommitFail=True)
        # As project visitor.
        self.changePersonProjectRole('Visitor')
        self.svnCheckoutAddCommit('svn4', 'Testing Subversion SSH access (project visitor)...', expectCheckoutFail=True)
        # As project administrator, again.
        self.changePersonProjectRole('Administrator')
        self.svnCheckoutAddCommit('svn5', 'Testing Subversion SSH access (project admin, again)...')
        

class TestMercurialAccess(SshAccessTestCase):

    requiredPlugins = ['ssh', 'mercurial']

    def testAccess(self):
        # As project administrator.
        for name in ['mercurial', 'mercurial2', 'mercurial3', 'mercurial4', 'mercurial5', 'mercurial6']:
            self.createService('mercurial', name)
        self.mercurialCloneAddCommitPush('mercurial', 'Testing Mercurial SSH access (project admin)...')

        # As project developer.
        self.changePersonProjectRole('Developer')
        self.mercurialCloneAddCommitPush('mercurial2', 'Testing Mercurial SSH access (project developer)...')

        # As project friend.
        self.changePersonProjectRole('Friend')

        # Todo: Make this work with expectPushFail=True instead. :-)
        self.mercurialCloneAddCommitPush('mercurial3', 'Testing Mercurial SSH access (project friend)...', expectPushFail=True)

        # As project visitor.
        self.changePersonProjectRole('Visitor')
        self.mercurialCloneAddCommitPush('mercurial4', 'Testing Mercurial SSH access (project visitor)...', expectCloneFail=True)

        # As project administrator, again.
        self.changePersonProjectRole('Administrator')
        self.mercurialCloneAddCommitPush('mercurial5', 'Testing Mercurial SSH access (project admin, again)...')

        # Check performance for project developer.
        self.changePersonProjectRole('Developer')
        self.mercurialCloneAddCommitPush('mercurial6', 'Testing Mercurial SSH access (push performance)...', checkPushPerformance=30)
        self.mercurialCloneAddCommitPush('mercurial6', 'Testing Mercurial SSH access (clone performance)...', checkClonePerformance=30)
        

class TestWillowGarageMercurialAccess(SshAccessTestCase):

    requiredPlugins = ['ssh', 'mercurial']

    def testPerformanceWillowGarage(self):
        self.createService('mercurial', 'mercurial7')
        oldcwd = os.getcwd()
        try:
            os.chdir(self.makeTempFolder())
            # Clone the service.
            self.mercurialClone('mercurial7')
            os.chdir('mercurial7')
            os.system('hg pull -f https://kforge.ros.org/navigation/navigation')
            #os.system('hg merge')
            #os.system('hg commit -m"Checking Willow Garage repository"')
            os.system('hg push')
        finally:
            os.chdir(oldcwd)
        self.mercurialCloneAddCommitPush('mercurial7', 'Testing Mercurial SSH access with Willow Garage repository (clone performance)...', checkClonePerformance=30)
        self.mercurialCloneAddCommitPush('mercurial7', 'Testing Mercurial SSH access with Willow Garage repository (push performance)...', checkPushPerformance=10)


class TestSshKeyRegistration(SshTestCase):

    requiredPlugins = ['ssh']

    def testCreateDelete(self):
        self.getAssertContent(self.urlPersonHome, 'SSH')
        sshKeyString = self.getSshKeyString()
        # Check the SSH key doesn't exist.
        wrapableKeyString = '&#8203;'.join(list(sshKeyString)) # For Firefox.
        self.getAssertNotContent(self.urlPersonSshKeyCreate, wrapableKeyString)
        # Create the SSH key.
        self.getAssertContent(self.urlPersonSshKeyCreate, 'SSH keys')
        sshKeyId = self.createSshKey()
        # Check the SSH key does exist.
        self.getAssertContent(self.urlPersonSshKeyCreate, wrapableKeyString)
        # Delete the SSH key.
        self.deleteSshKey(sshKeyId)
        # Check the SSH key doesn't exist.
        self.getAssertNotContent(self.urlPersonSshKeyCreate, wrapableKeyString)
        

class TestSshKeyRegistrationFailBase64(SshTestCase):

    requiredPlugins = ['ssh']

    def testCreate(self):
        self.getAssertContent(self.urlPersonHome, 'SSH')
        sshKeyString = self.getSshKeyString()
        # Check the SSH key doesn't exist.
        self.getAssertNotContent(self.urlPersonSshKeyCreate, sshKeyString)
        # Create the SSH key.
        self.getAssertContent(self.urlPersonSshKeyCreate, 'SSH keys')
        sshKeyId = self.createSshKey()
        sshKeyString = 'ssh-rsa fff some@domain'
        params = {'keyString': sshKeyString}
        self.postAssertContent(self.urlPersonSshKeyCreate, params, "Key does not appear to be encoded with base64.", code=400)
        # Check the SSH key doesn't exist.
        self.getAssertNotContent(self.urlPersonSshKeyCreate, sshKeyString)

