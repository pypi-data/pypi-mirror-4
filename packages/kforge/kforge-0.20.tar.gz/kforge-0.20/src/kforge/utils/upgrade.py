"""
Upgrade a system service database and filesystem from one version to another.

"""
import os
import kforge.utils.db
from dm.strategy import FindProtectionObject

class UpgradeDbTo0Point14(kforge.utils.db.Database):
    """Upgrade system service database from 0.13 to 0.14
    """

    def execute(self):
        import kforge
        app = kforge.getA()
        sys = app.registry.systems[1]
        sys.version = '0.14'
        sys.save()

class UpgradeDbTo0Point13(kforge.utils.db.Database):
    """Upgrade system service database from 0.13 to 0.14.
    """

    sql = '''ALTER TABLE plugin ADD COLUMN last_modified timestamp without time zone;
             ALTER TABLE system ADD COLUMN last_modified timestamp without time zone;
             ALTER TABLE project ADD COLUMN last_modified timestamp without time zone;
             ALTER TABLE person ADD COLUMN last_modified timestamp without time zone;
             ALTER TABLE session ADD COLUMN last_modified timestamp without time zone;
             ALTER TABLE system ADD COLUMN mode text;
             UPDATE plugin SET last_modified = now();
             UPDATE system SET last_modified = now();
             UPDATE project SET last_modified = now();
             UPDATE person SET last_modified = now();
             UPDATE session SET last_modified = now();
             UPDATE system SET mode = 'production';
             UPDATE system SET version = '0.13';
            '''

    def execute(self):
        print 'WARNING: this sql has been tested on postgres only ...'
        self.run_sql('-c "%s"' % self.sql)
        # now we have done basic upgrade safe to load soleinstance
        self.upgrade_protection_object_names()

    def run_sql(self, extra):
        self._registerSystemDictionaryFeature()
        sysdict = self.features['SystemDictionary']
        dbhost = sysdict['db.host']
        dbuser = sysdict['db.user']
        dbname = sysdict['db.name']
        # deregister before running command as command may raise exception
        self._deregisterSystemDictionaryFeature()
        cmd = 'psql -h %s -U %s %s %s' % (dbhost, dbuser, dbname, extra)
        self._runCommand(cmd)
        print 'SQL execution completed successfully'

    def upgrade_protection_object_names(self):
        import kforge.soleInstance
        from dm.strategy import MakeProtectedName
        registry = kforge.soleInstance.application.registry
        for item in registry.protectionObjects:
            name = item.name
            if name.startswith('Plugin.'):
                plugin_name = name[7:]
                # sometimes underlying object might have been deleted even
                # though protection object still here
                try:
                    plugin = registry.plugins.getAll()[plugin_name]
                except:
                    # print 'Did not find plugin with name %s' % plugin_name
                    continue
                makeName = MakeProtectedName(plugin)
                protectedName = makeName.make()
                print 'ProtectionObject with name %s now has name %s' % (name,
                        protectedName)
                item.name = protectedName
                item.save()
            if name.startswith('Person.'):
                person_name = name[7:]
                # sometimes underlying object might have been deleted even
                # though protection object still here
                try:
                    person = registry.people.getAll()[person_name]
                except:
                    print 'Did not find person with name %s' % person_name
                    continue
                makeName = MakeProtectedName(person)
                protectedName = makeName.make()
                print 'ProtectionObject with name %s now has name %s' % (name,
                        protectedName)
                item.name = protectedName
                item.save()
        print 'Upgrade of ProtectionObject names completed successfully'


class UpgradeDataTo0Point11(object):
    """Back up old system service configuration file and install new.
    """
    
    def execute(self):
        print \
'''To upgrade your data all you need to do is upgrade your configuration file

    1. Backup existing file (</path/to/installed/service>/etc/kforge.conf)

    2. Copy over new file (./etc/kforge.conf.new) and amend to reflect your
       new setup (suggest using your backed up configuration file).
'''

class UpgradeDbTo0Point11(kforge.utils.db.Database):
    """Upgrade system service database from 0.10 to 0.11.
    """
    
    sql = """ALTER TABLE project DROP COLUMN purpose;
            ALTER TABLE plugin ADD COLUMN state_id integer;
            ALTER TABLE plugin ADD CONSTRAINT state_id_exists FOREIGN KEY (state_id) REFERENCES state(id);
            ALTER TABLE plugin ADD COLUMN date_created timestamp without time zone;
            UPDATE plugin SET state_id = 1;
            UPDATE plugin SET date_created = now();
            """

class UpgradeDbTo0Point10(object):
    """Upgrade system service database from 0.9 to 0.10.
    
    NB: Some import statements are inline since they automatically create a
    connection to the db and we can't do this until the sql has been rewritten
    """

    def __init__(self):
        import kforge.dictionary
        sysdict = kforge.dictionary.SystemDictionary()
        self.dbuser = sysdict['db.user']
        self.dbname = sysdict['db.name']
        self.dbhost = sysdict['db.host']

    def pgsqlCommand(self, dbcmd, extra=''):
        print "Command %s requires '%s' user authentication:" % (dbcmd, self.dbuser)
        cmd = "%s -h %s -U %s %s %s" % (dbcmd, self.dbhost, self.dbuser, self.dbname, extra)
        if os.system(cmd):
            raise "ERROR (Kforge): Could not execute command: %s" % cmd
    
    def execute(self):
        self.alterRawSql()
        import kforge.dom
        self.registry = kforge.dom.DomainRegistry()
        self.createAccessControlData()
        self.createPersonalGrants()
        self.createPlugins()
    
    def alterRawSql(self):
        sql = """DROP TABLE role_permission;
    DROP TABLE permission;
    DROP TABLE protection_object;
    DROP TABLE permission_type;
    
    ALTER TABLE person ADD COLUMN role_id integer;
    ALTER TABLE person ADD CONSTRAINT role_id_exists FOREIGN KEY (role_id) REFERENCES role (id);
    
    UPDATE role SET name = 'Visitor' where name = 'Guest';
    DELETE FROM member where role_id = 5 or role_id = 6;
    DELETE FROM role where name = 'SystemAdministrator' OR name = 'SystemGuest';
    -- # get rid of sysadmin role and system guest role
    UPDATE person SET name = 'visitor' where name = 'guest';
    -- make all people have general role visitor
    UPDATE person SET role_id = 4;
    -- make 
    UPDATE person SET role_id = 1 where name = 'admin';"""
        self.pgsqlCommand('psql', '-c "%s"' % sql)
    
    def createAccessControlData(self):
        import kforge.command.initialise
        roles = self.registry.roles
        initialiseCmd = kforge.command.initialise.InitialiseDomainModel()
        initialiseCmd.adminRole = roles['Administrator']
        initialiseCmd.developerRole = roles['Developer']
        initialiseCmd.friendRole    = roles['Friend']
        initialiseCmd.visitorRole   = roles['Visitor']
        initialiseCmd.createSystem()
        initialiseCmd.createActions()
        initialiseCmd.createProtectionObjects()
        initialiseCmd.createGrants()
        initialiseCmd.createRefusals()
        initialiseCmd.createPersonalBars()
        
    def createPersonalGrants(self):
        for person in self.registry.people:
            findObject = FindProtectionObject(person)
            protectionObject = findObject.find()
            for permission in protectionObject.permissions:
                if not permission in person.grants:
                    person.grants.create(permission)
    
    def createPluginPermissions(self):
        for plugin in self.registry.plugins:
            plugin.getSystem().onCreate()
    
    def createPlugins(self):
        self.registry.plugins.create('accesscontrol')

