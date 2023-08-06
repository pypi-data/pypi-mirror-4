"""
To run tests:
    (a) run UpgradeTest
    (b) run bin/kforge-test (note that if you aren't running in development
    mode you will need to run createDevelopmentData first)
"""
import os
import unittest
import kforge.utils.upgrade
import kforge.utils.admin

class UpgradeDbTo0Point13Test(unittest.TestCase):
    tags = [ 'cli' ]
    disable = True

    oldSql = '~/svnroot/kforge/misc/knowledgeforge-kforge-0.12.sql'

    def setUp(self):
        os.system('kforge-admin db delete')
        os.system('kforge-admin db create')
        self.cmd = kforge.utils.upgrade.UpgradeDbTo0Point13()
        self.cmd.run_sql('-q --file %s' % self.oldSql)

    def test_1(self):
        self.cmd.execute()

class UpgradeDataTo0Point11Test(unittest.TestCase):
    tags = [ 'cli' ]
    disable = True
    
    def setUp(self):
        self.tmpDir = tempfile.mkdtemp()
        self.cmd = kforge.utils.admin.InitialiseFilesystem(self.tmpDir)
        self.cmd.execute()
        self.upgradeCmd = UpgradeEnvCmd(self.tmpDir)
        self.upgradeCmd.execute()
        
    def tearDown(self):
        shutil.rmtree(self.tmpDir)

    def test_backupOldConfiguration(self):
        backupPath = os.path.join(self.tmpDir, 'etc/kforge.conf.old')
        self.assertTrue(os.path.exists(backupPath))


class UpgradeDbTo0Point10Test(unittest.TestCase):
    """
    For test to work you need to provide a db dump of a 0.9 db and provide link
    to it below and also edit the other values to reflect your setup.
    """
    tags = [ 'cli' ]
    disable = True
    
    oldSql = os.path.normpath('~/db_dumps/kforge_0.9.sql')
    # edit these values to reflect the state of your original install
    numberOfUsers = 31
    numberOfProjects = 10
    personName = 'rgrp'
    # put a project on which personName is an administrator
    projectName = 'kforge'
    
    def setUp(self):
        upgradeCmd = kforge.utils.upgrade.UpgradeDbTo0Point10()
        upgradeCmd.pgsqlCommand('dropdb')
        upgradeCmd.pgsqlCommand('createdb')
        upgradeCmd.pgsqlCommand('psql', '-q --file %s' % self.oldSql)
        upgradeCmd.execute()
        import kforge.dom
        self.registry = kforge.dom.DomainRegistry()
    
    def _test_basic(self):
        people = self.registry.people
        self.failUnless('admin' in people)
        self.failUnless('visitor' in people)
        self.failIf('guest' in people)
        self.failUnless(len(people) == self.numberOfUsers)
        self.failUnless(self.personName in people)
        
        projects = self.registry.projects
        self.failUnless('administration' in projects)
        self.failUnless(self.projectName in projects)
        self.failUnless(len(projects) == self.numberOfProjects)
        
        roles = self.registry.roles
        testPerson = people[self.personName]
        testProject = projects[self.projectName]
        self.failUnless(testPerson in testProject.members)
        self.failUnless(testProject.members[testPerson].role == roles['Administrator'])

    def test_upgrade(self):
        "All in one tests because setup takes so long."
        self._test_basic()


class UpgradeDbTo0Point11Test(UpgradeDbTo0Point10Test):
    tags = [ 'cli' ]
    disable = True
    
    oldSql = os.path.normpath('~/db_dumps/kforge_0.10.sql')
    numberOfUsers = 36
    numberOfProjects = 16
    
    def setUp(self):
        upgradeCmd = kforge.utils.upgrade.UpgradeDbTo0Point11()
        upgradeCmd.pgsqlCommand('dropdb')
        upgradeCmd.pgsqlCommand('createdb')
        upgradeCmd.pgsqlCommand('psql', '-q --file %s' % self.oldSql)
        upgradeCmd.execute()
        # now we can use stuff that affects the db
        app = kforge.getA()
        self.registry = app.registry
    
    def _test_0point11(self):
        # test purpose has disappeared
        # concerned this tests model rather than db ...
        project = self.registry.projects[self.projectName]
        try:
            pp = project.purpose
        except:
           pass
        else:
           fail('Purpose attribute should not exist')
        # plugins are now dated and stateful
        plugin = self.registry.plugins['accesscontrol']
        self.assertEqual(1, plugin.state.id)
        self.assertTrue(len(str(plugin.dateCreated)) > 0)

    def test_upgrade(self):
        self._test_basic()
        self._test_0point11()
    

def createDevelopmentData():
    "Create the data used for testing in development mode"
    print 'Running createDevelopmentData'
    import kforge.soleInstance
    sys = kforge.soleInstance.application.registry.systems[1]
    sys.mode = 'development'
    sys.save()
    # weird behaviour
    # import kforge.command.initialise gives us dm.command.initialise
    # initialiseCmd = kforge.command.initialise.InitialiseDomainModel()
    from kforge.command import InitialiseDomainModel
    initialiseCmd = InitialiseDomainModel()
    print 'Running createTestPlugins()'
    initialiseCmd.createTestPlugins()
    print 'Running setUpTestFixtures()'
    initialiseCmd.setUpTestFixtures()

if __name__ == '__main__':
    # suite = unittest.makeSuite(UpgradeDbTo0Point10Test)
    suites = [ 
        unittest.makeSuite(UpgradeDbTo0Point13Test),
        ]
    testRunner = unittest.TextTestRunner()
    testRunner.run(unittest.TestSuite(suites))
    # create dev data so we can run the tests
    createDevelopmentData()
