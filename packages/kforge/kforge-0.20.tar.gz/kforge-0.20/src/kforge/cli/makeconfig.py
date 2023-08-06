from dm.cli.makeconfig import DomainConfigMaker
import os

class ConfigMaker(DomainConfigMaker):

    template = """[DEFAULT]
# Filesystem root (defaults to config file folder, or the config
# file folder's parent folder in the case where the config file
# folder's name is either 'etc' or 'config'). If other values 
# inside this configuration file substitute 'master_dir' with the
# syntax '%(master_dir)s' then the correct path must be set here.
#master_dir = /path/to/kforge

# Path to folder for KForge project service
# files (default: %(master_dir)s/var/projects).
#project_data_dir = %(master_dir)s/var/projects

# Name of KForge service (default: KForge).
#service_name = KForge

# DNS domain name (defaults to 'dnsdomainname' command).
#dns_domain_name = example.com

# Host name of KForge site (default: projects.%(dns_domain_name)s).
#site_host = projects.%(dns_domain_name)s

# Mode of operation (default: production).
#system_mode = production

# Umask (default: 0o007) for new file creation. The system umask is set
# with this value. Permissions for the 'group' can be masked when all
# processes accessing the KForge files are run with the same user. If other
# users will access the files then set a umask of 0o007. Permissons for
# 'other' users should always be masked.
#umask = 0o007

# Salt for password digests (default: not-a-secret). Please note,
# this value must be carried forward when migrating data otherwise
# users will not be able to authenticate with their true passwords.
#password_digest_secret = not-a-secret

[db]
# When type is sqlite, set name to be a file path. Otherwise
# for postgres (and mysql) set a normal database name and
# set the user, password and host if necessary.

# Database type (default: sqlite).
#type = sqlite

# Database name (default for sqlite: %(master_dir)s/var/sqlite.db
# otherwise, default for other database types: kforge).
#name = %(master_dir)s/var/sqlite.db

# Database user (default: kforge).
#user = kforge

# Database password (default: ).
#pass = 

# Database host (default: localhost).
#host = localhost

[django]
# Path to folder of template files (default: %(master_dir)s/templates).
#templates_dir = %(master_dir)s/templates

# Secret to seed session key generation (default: not-a-secret).
#secret_key = not-a-secret 

[email]
# Enable email (default: ).
#enable_sending = on

# Send notifications of changes to administrators (default: ).
#notify_changes = on

# Email address for sending service emails (default: noreply@%(dns_domain_name)s).
#service_address = noreply@%(dns_domain_name)s

# SMTP server host (default: localhost).
#smtp_host = localhost

# SMTP server port (default: ).
#smtp_port =

# SMTP server user (default: ).
#smtp_user =

# SMTP server password (default: ).
#smtp_password =

# SMTP server connection uses TLS (default: ).
#smtp_use_tls =

[environment]
# Timezone, see platform's zoneinfo database (defaults to environment).
#timezone = Europe/London

[feed]
# Maximum number of items in feed (default: 100).
#length = 100

# Maximum number of items in feed summary (default: 25).
#length_summary = 25

[logging]
# Path to KForge log file (default: %(master_dir)s/var/log/kforge.log).
#log_file = %(master_dir)s/var/log/kforge.log

# Log level ERROR, WARNING, or INFO (default: WARNING).
#level = WARNING

[memos]
# Enable memoization of access controller results (default: ).
# Note: Enable this if you want a performance boost. Don't enable this
# if you want access control to immediately follow project membership
# changes, otherwise access control will lag by the 'expire' option below.
#enabled = on

# Maximum number of memos to store (default: 3000).
#limit = 3000

# Maximum time (seconds) validity of memos (default: 30).
#expire = 30

[model_cache]
# Enable cache of domain model objects on domain model registers (default: ).
# Note: Enabling the model cache boots performance dramatically but can
# cause a relatively large amount of memory to be used (depending on how many
# projects and people and services there are).
# Note: Use in single-process multi-threaded Web server configurations,
# such as mod_wsgi runnnig in deamon mode. Don't use in multi-process Web
# server configurations such as mod_wsgi running in embedded mode with more than
# one child process, or mod_python running with more than one child process.
# Note: When both mod_wsgi and mod_python are enabled, the SVN HTTP service
# will run in mod_python so that authentication prompt does not appear when
# anonymous uses have read access to the repository (currently unavoidable
# when controlling authentication to DAV svn with mod_wsgi). This condition
# is detected so that the mod_python process will avoid cacheing the model,
# so it is possible to run everything else in a multi-threaded single process
# mod_wsgi daemon with model cacheing enabled.
# Note: When the model_cache is enabled, if changes to the model objects are
# made via the command line, then the Web server will need to be restarted
# for the changes to the model objects to appear in the Web interface (doing
# a graceful restart is okay).
#enable = on

# List of classes cached by model cache (default: Plugin, Person, Project,
# Member, Service, Session, Ticket, TracProject).
# Note: If this list is empty and cache is enabled, then all classes will be
# cached, which may take up quite a lot of memory. If access controller memos
# are enabled, performance will not be improved very much by cacheing access
# control objects (ProtectionObject, Permission, Grant, Bar) which is why they
# are not included in the default list.
# Note: Some classes (State, Role, Action, License) are modelled as constant
# and are therefore always cached, so nothing is gained by listing them here.
#classes = Plugin, Person, Project, Member, Service, Session, Ticket, TracProject

[virtualenv]
# Path to bin folder of virtual environment (required within virtualenv).
#bin_dir = %(master_dir)s/bin

[www]
# Enable reloading Apache (default: ).
#enable_reload_apache = on

# Command to reload Apache (default: sleep 1 && sudo /etc/init.d/apache2 graceful).
# The purpose of the delay before restarting is to allow successful service
# form submissions to be redirected to (and to load) the service status page
# before the server is restarted. The service status page monitors and indicates
# the status of services that are waiting for the server to restart, so that
# users can see exactly when the service is running.
# Note, adding "kforge ALL=(ALL) NOPASSWD: /etc/init.d/apache2 graceful" to
# your sudoers file will help to make reloading work. Of course, change
# "kforge" to whichever user the process will run as. Note well, on
# some systems it may be better to use the 'reload' command.
#reload_apache = sleep 1 && sudo /etc/init.d/apache2 graceful

# Path to auto-generated Apache configuration file (default:
# %(master_dir)s/var/httpd-autogenerated.conf).
#apache_config_file = %(master_dir)s/var/httpd-autogenerated.conf

# Path to the auto-generated WSGI file (default: %(master_dir)s/wsgi/kforge.wsgi).
#wsgi_file = %(master_dir)s/wsgi/kforge.wsgi

# Path to folder with css, images, and scripts (default: %(master_dir)s/media).
#media_dir = %(master_dir)s/media


## ********************************************************************
## Plugins
## ********************************************************************

[git]
# Absolute path to Git binary (default: /usr/bin/git).
#admin_script = /usr/bin/git

# Path to HTTP backend script (default: /usr/lib/git-core/git-http-backend).
#http_backend_script = /usr/lib/git-core/git-http-backend

# Path to GitWeb script (default: /usr/lib/cgi-bin/gitweb.cgi).
#gitweb_script = /usr/lib/cgi-bin/gitweb.cgi

# Path to GitWeb static media (default: /usr/share/gitweb/static).
#gitweb_static = /usr/share/gitweb/static


[joomla]
# Path to master Joomla installation to be used as a template (required).
master_path = /usr/share/joomla_1.5

# Shell command to dump the Joomla database to stdout (required).
backup_command = mysqldump --user=JOOMLADBUSER --password=JOOMLADBPASS JOOMLADBNAME

[mailman]
# Shell command (without arguments) to create a list (default: sudo newlist).
#newlist = sudo newlist

# Shell command (without arguments) to delete a list (default: sudo rmlist).
#rmlist = sudo rmlist

# Web interface host name (default: lists.%(dns_domain_name)s).
#urlhost = lists.%(dns_domain_name)s

# Email host name (default: lists.%(dns_domain_name)s).
#emailhost = lists.%(dns_domain_name)s

[mercurial]
#admin_script = %(master_dir)s/bin/hg

[moin]
# Path to MoinMoin folder containing the htdocs folder (default: /usr/share/moin).
#system_path = /usr/share/moin

# Version name used to locate MoinMoin files (default: 193)
#version = 193

[ssh]
# Commands and keys are written to this file.
#authorized_keys_file = ~/.ssh/authorized_keys

# The SSH user name (used to indicate how to access services).
#user_name = %(user_name)s 

# The SSH host (used to indicate how to access services).
#host_name = %(site_host)s

[svn]
# Enable ViewVC for SVN repositories (default: ).
#enable_viewvc = on

# Path to the ViewVC Python library (default: /usr/lib/viewvc/lib).
#viewvc_lib = /usr/lib/viewvc/lib

# Path to the ViewVC templates folder (default: /etc/viewvc/templates).
#viewvc_template_dir = /etc/viewvc/templates

# Path to the ViewVC media folder (default: /usr/share/viewvc/docroot).
#viewvc_media_dir = /usr/share/viewvc/docroot

[trac]
# Trac admin script (default: %(master_dir)s/bin/trac-admin).
#admin_script = %(master_dir)s/bin/trac-admin

# Path to Trac htdocs folder (default: ). This can be used to avoid
# streaming the htdocs through Trac, which may result in a performance
# improvement.
#htdocs_path = 

# Set preferences on Trac services for all registered people (default: ).
# Enabling this option will slow down user registration and updates when
# there are lots of projects. It is useful for allowing tickets to be followed
# in other projects.
#set_preferences_for_all_people =

[wordpress]
# Path to Wordpress folder containing template install (default: /usr/share/wordpress).
#master_path = /usr/share/wordpress

# Shell command to dump the Wordpress db to stdout (required).
backup_command = mysqldump --user=WORDPRESSDBUSER --password=WORDPRESSDBPASS WORDPRESSDBNAME

"""

    def __init__(self, systemName='kforge'):
        super(ConfigMaker, self).__init__(systemName=systemName)

    def addOptions(self, parser):
        super(ConfigMaker, self).addOptions(parser)

        parser.add_option(
            '--project-data-dir',
            dest='projectDataDir',
            help="""The folder to be used for project service data.
Please note, it is recommended to set a path to a directory outside of
the master folder (--master-dir) since new versions will be installed
in isolation from previous versions, but they will need to use the same
project service data folder, which may cause trouble if moved once
created. That is, if you put your project service data inside your first
installation, subsequent installations will be forced to refer to a path
in an older installation.""")

        parser.add_option(
            '--trac-admin',
            dest='tracAdmin',
            help="""The path to your trac-admin script.""")

        parser.add_option(
            '--viewvc-dir',
            dest='viewvcDir',
            help="""The path to your ViewVC installation.""")

        parser.add_option(
            '--mailman-domain-name',
            dest='mailmanDomainName',
            help="""The domain name of the mailing list server.""")

    def addOptionLines(self, options, optionLines):
        super(ConfigMaker, self).addOptionLines(options, optionLines)
        if options.projectDataDir:
            optionLines.append('[DEFAULT]')
            optionLines.append('project_data_dir = %s' % os.path.abspath(options.projectDataDir))
        if options.viewvcDir:
            optionLines.append('[svn]')
            optionLines.append('viewvc_lib = %s' % os.path.abspath(os.path.join(options.viewvcDir, 'lib')))
            optionLines.append('viewvc_template_dir = %s' % os.path.abspath(os.path.join(options.viewvcDir, 'templates')))
            optionLines.append('viewvc_media_dir = %s' % os.path.abspath(os.path.join(options.viewvcDir, 'templates', 'docroot')))
        if options.tracAdmin:
            optionLines.append('[trac]')
            optionLines.append('admin_script = %s' % options.tracAdmin)
        if options.mailmanDomainName:
            optionLines.append('[mailman]')
            optionLines.append('emailhost = %s' % options.mailmanDomainName)
            optionLines.append('urlhost = %s' % options.mailmanDomainName)


