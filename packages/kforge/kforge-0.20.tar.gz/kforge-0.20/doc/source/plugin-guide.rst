============
Plugin Guide
============

.. toctree::
   :maxdepth: 2

Plugins are central to KForge and the main way it can be extended. This document introduces the KForge plugin system and explains how to write a new plugins.

System Design
*************

Please take a look at the (ascii) UML diagram below.

::


                 DOMAIN OBJECTS                      |      PLUGIN SYSTEM
                                                     |  +-------------------+         
                 +------------+                      |  |  PluginController |
        +----- |>|DomainObject|<|----------+         |  +-------------------+
        |        +------------+            |         |  | getPlugins()      |
        |              A                   |         |  +-------------------+
        |              |                   |         |  
    +-------+    +----------+    +----------------+  |    +----------------+         
    |Project|<>--|  Service |--<>|  Plugin        |  |    |  PluginBase    |          
    +-------+    |----------|    |----------------|  |    |----------------|          
    | name  |    | name     |    | name           |<------| domainObject   |          
    +-------+    | project  |    |----------------|  |    | register       |          
                 | plugin   |    | getSystem(name)|  |    +----------------+            
                 +----------+    +----------------+  |          A                     
                                                     |          |                     
                                                     | +---------------------------+  
                                                     | | kforge.plugin.name.Plugin |      
                                                     | +---------------------------+
                                                     |
                                                  
The KForge domain model has project, plugin, and service domain objects. The plugin domain
objects "represent" plugged-in software modules. The relationships here are illustrated in the above diagram.

A plugin controller has a getPlugins() method, which uses the getSystem() method of the active plugin domain objects to load plugged-in objects. The name of the plugin domain object is used to locate a similarly named Python module, which will contain a subclass of the PluginBase class.

When model events occur, such as the creation of a new service, the plugin controller propagates the event to every active plugin.

There are different kinds of plugins. Service plugins (e.g. git) adapt plugged-in software applications. Non-service plugins (e.g. apacheconfig) generally do useful work in response to the core model objects.

Todo: Mention apache config fragment generation for service plugins.

Todo: Mention user help generation for service plugins.


Plugin Development
******************

The main way the plugin gets to do things is:
  1. A plugin is notified of **events**
  2. A plugin may insert configuration into apache

You create a plugin by inheriting from kforge.plugin.PluginBase and then overriding methods. The best way to understand how this works and how to use it is:
  1. Read documentation of methods on kforge.plugin.PluginBase to understand what you can override
  2. Look at an existing plugin, many of which already exist in the kforge/plugin/ directory.

The Simplest Possible Plugin
============================

::

    import kforge.plugin

    class Plugin(kforge.plugin.PluginBase):
        """
        Class must be called Plugin
        """
        pass

Well obviously this isn't very exciting because it does *literally* nothing but it will work.

The Example Plugin
==================

The Example plugin is still very simple but it at least does something: it acts on an event. Rather than go through the plugin take a look at the code which is heavily documented.

`Todo: More about each of the plugins.`

Subversion
==========

Mercurial
=========

Git
===

SSH
===

DAV
===

Trac
====

Wordpress
=========

Mailman
=======

MoinMoin
========
