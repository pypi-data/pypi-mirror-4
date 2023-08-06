Administration Guide
====================

Site administrators have access to all functionality of the Web interface.
For example, site administrators can update and delete all registered accounts.
Site administrators are also able to act as project administrator for all projects 
without actually being a member of any project.
Site administrators can also access the administration section of the Web interface (**Admin**).

System administrators are able to administer most aspects of a KForge service easily via the command line. KForge is installed and setup from the command line. The KForge configuration file is editable from the command line. Since KForge plugins often depend on other programs that will be installed and configured from the command line, it is recommended to enable KForge plugins from the command line so that any dependencies can be checked and resolved. KForge can also be backed up and upgraded from the command line.


Edit Configuration
------------------

With your editor, open the KForge configuration file.
::

    $ editor $KFORGE_SETTINGS

Optional settings are mostly well documented within the configuration file (more detailed documentation is forthcoming).

After making changes to the file, reload Apache.
::

    $ kforge-admin apacheconfig reload


Create Administrators
---------------------

Any registered user can be made into a site administrator by setting their personal role to
'Administrator'.

To promote a user to a site administrator, when logged into the Web interface as a site administrator, go to the 'Person' register in the model administration section (**Admin** >> **Model** >> **Person**).

Select the registered Person to be promoted to a site administrator.

Press the 'Update Person' button.

Change the 'role' to 'Administrator' and submit the form.

The selected user will immediately have access to all functionality of the Web interface.


Enable Plugins
---------------

Some plugins, such as 'git', provide functionality for project services.
Other plugins, such as 'ssh', optionally enhance core and project service functionality.
Site administrators can adjust the types of project services and
other functionality that is available on a KForge site by enabling
and disabling the plugins which are available.

Please note, project administrators can only create new project services with enabled
plugins. Disabling a service plugin which has been used to create project
services will not disable those services. However, if accessing a project
service depends on an optional extra plugin (e.g. ssh access to git services),
then disabling the optional extra plugin will necessarily inhibit access to
the project service in the way that was previously enabled.

The recommended way to enable and disable plugins is the `kforge-admin plugin`
command, which checks the plugin dependencies are satisfied before the plugin
is enabled.

::

    $ kforge-admin help plugin

If you wish to use Subversion, Mercurial and Git, then install these packages.
::

    $ sudo aptitude install subversion libapache2-svn
    $ sudo aptitude install mercurial
    $ sudo aptitude install git gitweb

If you want to use DAV or Subversion make sure the corresponding Apache modules are
enabled.
::

    $ sudo a2enmod dav
    $ sudo a2enmod dav_fs
    $ sudo a2enmod dav_svn

Discover all available plugins with the 'kforge-admin plugin choices'
command.
::

    $ kforge-admin plugin choices
    dav
    joomla
    mailman
    mercurial
    moin
    notify
    svn
    trac
    wordpress
    www

List the enabled plugins with the 'kforge-admin plugin list' command.
::

    $ kforge-admin plugin list
    dav
    www

For each plugin you would to use, read the 'plugin doc', then 'plugin enable'
the plugin, and then 'plugin show' its status. You won't be able to enable
a plugin if its dependencies aren't available on your system.

For example, enable the Trac, Subversion, and Mercurial plugins.
::

    $ kforge-admin plugin enable trac
    The 'trac' plugin is now enabled (see 'doc' and 'status').
    $ kforge-admin plugin enable svn
    The 'svn' plugin is now enabled (see 'doc' and 'status').
    $ kforge-admin plugin enable mercurial
    The 'mercurial' plugin is now enabled (see 'doc' and 'status').
    $ kforge-admin plugin list
    dav
    mercurial
    svn
    trac
    www

For example, read the documentation for the Subversion plugin.
::

    $ kforge-admin plugin doc mercurial
    ...

For example, read the status of the Subversion plugin.
::

    $ kforge-admin plugin status mercurial
    ...

Please note, it is also possible to enable plugins by directly creating a plugin object
in the model. However, dependencies will not be checked and so if there are
any missing dependencies, they will only be discovered when a service is
created.

To create a plugin object via the
Web interface, go to the Plugin Model Administration page (**Admin** >>
**Model** >> **Plugin**).

Press the 'Create Plugin' button. Complete and submit the form.

The plugin will be enabled immediately.



Adjust Model
------------

Site administrators may wish to adjust the objects of the domain model.

When logged in as a site administrator, go to the Model page (**Admin** >> **Model**).

Select the type of object you want to adjust. Either create a new object, read an existing object, update an existing object, or delete an existing object.

The changes will be effective immediately.

Please note, from the command line it is also possible to invoke a Python
shell and directly manipulate the KForge domain model as Python objects.

For example, to change the role of a user::

    $ kforge-admin shell
    >>> from kforge.soleInstance import application
    >>> person = application.registry.persons['anna']
    >>> person.role = application.registry.roles['Administrator']
    >>> person.save()

Alternatively, to enable a plugin::

    $ kforge-admin shell
    >>> from kforge.soleInstance import application
    >>> application.registry.plugins.create('ssh')


Change Themes
-------------

The KForge Web user interface theme is defined by:

  * the CSS and images in the media directory (config file: 'media_dir')
  * the HTML in the templates directory (config file: 'templates_dir')

If you want to create a new theme you should:

  1. Create new media and template directories (probaby best done by copying
     the existing directories).
  2. Edit the necessary files (to understand how the templates work please
     read up on Django templates: http://www.djangoproject.com/).
  3. Adjust your KForge configuration file to use your new directories.
  4. Regenerate the Apache configuration file and reload apache.

For example:

  * If you wanted to change the colours, use Firebug and adjust .css files.

  * If you wanted to change the text on the front page of the site edit
    snippets/introduction.html, snippets/sitesummary.html, and 
    snippets/userlinks.html in the base template directory.

  * If you wish to change the basic look and feel of all pages you start by
    editing master.html in the base template directory.


