             DOMAIN OBJECTS                      |      PLUGIN SYSTEM
                                                 |
             +------------+                      |
    +----- |>|DomainObject|<|----------+         |
    |        +------------+            |         |
    |         A    A                   |         |
    |     _.--'    |                   |         |
    |     |  +-----------+   +----------------+  |  +------------------+
    |     |  |  Service  |   |     Plugin     |  |  |      Plugin      |
    |     |  |-----------|   |  (dom.Plugin)  |  |  |  plugin.Plugin   |
+-------+ |  |name:    xx|   |----------------|  |  |------------------|
|Project|--<>|project: yy|   |    name: zz    |<----|getDomainObject():|
+-------+ |  |plugin:  zz|<>-|  getSystem():  |  |  |    dom.Plugin    |
          |  +-----------+   |plugin.zz.Plugin|-+|  +------------------+
          |                  +----------------+ ||              A
          |                                     ||              |
          |                                     ||              |
          |                                     ||   +-----------------+
          |                                     +--->|     Plugin      |
+---------+         +-----------------+          |   |plugin.zz.Plugin |
|ZzProject|*       1|ZzProjectRegister|          |   |-----------------|
|---------|---------|-----------------|------------<>|    register:    |
|         |         |                 |          |   |ZzProjectRegister|
+---------+         +-----------------+          |   +-----------------+
                                                 |
                                                 |
                                                 |
-------------------------------------------------|
                        |                        |
                        |                        |
     PERSISTENCE        |                        |
        LAYER           |                        |
     (kforge.db)        |
                        |
                        V  Database/Flat File/...
                    ,-------.
                   (         )
                   |`-------'|
                   |         |
                    `-------'

Notes
=====

1. For brevity many of the class names above have kforge missing at the front. For example dom.plugin should be kforge.dom.plugin.

2. The above shows a complex setup where a plugin needs to persist data of its own. This is the case for the trac plugin which needs to remember which subversion repository it is using. In simpler plugins (for example svn) this is not needed and in that case the lower two items on the left of the figure (ZzProject and ZzProjectRegister) will not exist.

