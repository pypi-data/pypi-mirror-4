"""
A Plugin to provide Joomla services in KForge projects.

## Notes ##

We follow an approach where we install a copy of the Joomla code for every
install.

## Installation ##

1. If necessary, configure Apache to run Joomla's .phtml files as PHP pages. 
    
AddType application/x-httpd-php .phtml

2. Install Joomla 1.5 on your system in a master directory.

3. Setup a MySQL database for use by the Joomla services (they will all
share the same db).

4. Edit configuration.php-dist to correspond to the database you have just set
up. This file will be use as the template for the config file for each of the
KForge Joomla installations created in the future. Leave the $secret parameter
with its default value since this will be randomly genererated upon service
creation. Leave also $dbprefix to its default since this will be set based
on the project and service name. 

5. Add the following configuration section to your KForge configuration file.

[joomla]
# path to your master Joomla installation that will be used as a template
master_path = /path/to/your/joomla/installation
# shell command to run in order to backup the Joomla db
backup_command = mysqldump --user=<insert-name> --password=<insert-password> <db-name>

6. Enable the Joomla plugin in your KForge installation by creating a
'joomla' plugin object in the domain model (see the KForge guide for details).

    $ kforge-admin plugin enable joomla

7. That's it!
"""
import os
import shutil
import commands
import string
from random import Random
import re

import kforge.plugin.base

class Plugin(kforge.plugin.base.ServicePlugin):
    """Joomla Plugin to provide joomla services to projects
    """

    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        master_path = self.dictionary['joomla.master_path']
        self.utils = kforge.plugin.joomla.JoomlaUtil(master_path)

    def onServiceCreate(self, service):
        if self.isOurs(service):
            self.assertServicesFolder(service)
            path = service.getDirPath()
            dbTablePrefix = '%s_%s_' % (service.project.name, service.name)
            self.utils.create(path, dbTablePrefix)
            msg = 'JoomlaPlugin: Created service %s on path: %s)' % (
                service, path
            )
            self.log(msg)
            self.buildAndReloadApacheConfig()

    def onServicePurge(self, service):
        super(Plugin, self),onServicePurge(service)
        # TODO: Delete the Joomla database instance.
    
    def getApacheConfig(self, service, configVars):
        apacheConfigTmpl = """
<IfModule mod_wsgi.c>
Alias %(urlPath)s %(fileSystemPath)s
<Location %(urlPath)s/administrator>
%(modWsgiAccessControl)s
</Location>
IfModule>
<IfModule !mod_wsgi.c>
<IfModule mod_python.c>
%(modPythonAccessControl)s
</IfModule>
</IfModule>
"""
        return apacheConfigTmpl % configVars

    def backup(self, service, backupPathBuilder):
        # this is not great at present since we do a backup of the **whole**
        # database for every service even though there is only one database for
        # all joomla services
        backupPath = backupPathBuilder.getServicePath(service)
        backupPath += '.gz'
        basecmd = self.dictionary['joomla.backup_command']
        cmd = basecmd + ' | gzip > %s' % backupPath
        status, output = commands.getstatusoutput(cmd)
        if status:
            # do not use KForge exceptions here as would like to be standalone
            raise Exception('Failed to backup. Output was: %s' % output)

    helpMessage = '''
<p>This service provides a <a href="http://www.joomla.org/">Joomla</a> site located at:</p>
<p style="text-align: center"><a href="%(url)s">%(url)s</a></p>
<p>When the service is created it adds an "admin" user with password "admin" which should be changed as soon as possible in the administrator interface located at:</p>
<p style="text-align: center"><a href="%(url)s/administrator">%(url)s/administrator</a></p>
<p>For more information on the Joomla CMS system, visit <a href="http://docs.joomla.org/">Joomla documentation</a></p>
'''

    def getUserHelp(self, service, serviceLocation):
        values = { 'url' : serviceLocation }
        msg = self.helpMessage % values
        return msg


class JoomlaUtil(object):

    def __init__(self, master_path):
        self.master_path = master_path

    def _get_parent_directory(self, new_path):
        if new_path.endswith('/'): # assumes unix style path!
            new_path = new_path[:-1]
        # this should work once we have stripped the trailing /
        parentDir = os.path.dirname(new_path)
        return parentDir

    def create(self, new_path, db_prefix):
        """Create joomla installation
		This follows exactly the manual installation procedure as
		explained at http://help.joomla.org/content/view/1944/302/
		This adds by default an admin user with password admin.
		To provide some guards against misuse of this simple login,
		the administrator web interface is secured so only the members
		of the project are allowed. The password for admin should
		however be changed to something more appropriate after
		service is created.
        """
        parentDir = self._get_parent_directory(new_path)
        if not os.path.exists(parentDir):
            os.makedirs(parentDir)
        shutil.copytree(self.master_path, new_path)

	# Read the sample config file
        src_path = os.path.join(self.master_path, 'configuration.php-dist')
        dest_path = os.path.join(new_path, 'configuration.php')
        config = file(src_path).read()

	# Extract the mysql host parameter
	host = re.search('var \$host = .*', config).group()
	host = re.search('\'.*\'', host).group()
	host = host[1:-1]

	# Extract the mysql user parameter
	user = re.search('var \$user = .*', config).group()
	user = re.search('\'.*\'', user).group()
	user = user[1:-1]

	# Extract the mysql password parameter
	password = re.search('var \$password = .*', config).group()
	password = re.search('\'.*\'', password).group()
	password = password[1:-1]

	# Extract the mysql database parameter
	db = re.search('var \$db = .*', config).group()
	db = re.search('\'.*\'', db).group()
	db = db[1:-1]

	# Replace the table prefix
        config = config.replace("$dbprefix = 'jos_';", "$dbprefix = '%s';" % db_prefix)

	# Generate a new secret word
	secret = ''.join( Random().sample(string.letters+string.digits, 20) )
	config = config.replace("$secret = 'FBVtggIk5lAzEU9H';", "$secret = '%s';" % secret)

	# Write the new configuration
        outfile = file(dest_path, 'w')
        outfile.write(config)
        outfile.close()


	# Read the SQL file for populating the database
        src_path = os.path.join(self.master_path, 'installation', 'sql', 'mysql', 'joomla.sql')
        dest_path = os.path.join(new_path, 'installation', 'sql', 'mysql', 'joomla.sql')
        sql = file(src_path).read()

	# Replace the table prefix
        sql = sql.replace("#__", db_prefix)

	# Write the SQL file
        outfile = file(dest_path, 'w')
        outfile.write(sql)
        outfile.close()

	# Populate the database
	cmd = "mysql --host=%s --database=%s --user=%s --password=%s < %s" % (
		host, db, user, password, dest_path
	)
	status, output = commands.getstatusoutput(cmd)


	# Create the SQL file for adding the default admin user
        dest_path = os.path.join(new_path, 'installation', 'sql', 'mysql', 'admin.sql')
	sql = "INSERT INTO `%susers` VALUES (62, 'Administrator', 'admin', 'your-email@email.com', '21232f297a57a5a743894a0e4a801fc3', 'Super Administrator', 0, 1, 25, '2005-09-28 00:00:00', '2005-09-28 00:00:00', '', '');" % db_prefix
	sql += "INSERT INTO `%score_acl_aro` VALUES (10,'users','62',0,'Administrator',0);" % db_prefix
	sql += "INSERT INTO `%score_acl_groups_aro_map` VALUES (25,'',10);" % db_prefix

        outfile = file(dest_path, 'w')
        outfile.write(sql)
        outfile.close()

	# Create the admin user
	cmd = "mysql --host=%s --database=%s --user=%s --password=%s < %s" % (
		host, db, user, password, dest_path
	)
	status, output = commands.getstatusoutput(cmd)

	# Remove the installation directory
        dest_path = os.path.join(new_path, 'installation')
	cmd = "rm -rf %s" % dest_path
	status, output = commands.getstatusoutput(cmd)
