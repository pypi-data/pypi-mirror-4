.. contents::

Overview
========

Nagios data
-----------

- uptime
- main database size
- total reference count
- errors in the root error log

Munin data
----------

graphs provided by zeo_munin.py
```````````````````````````````

clients
  nr of zeo clients connected to zeo server

verifying
  XXX help document

loadstores
  nr of object loads and stores of the database


graphs provided by munin_client.py
``````````````````````````````````

uptime
  uptime of the zope instance in days (1 hour is 0.041)

refcount
  XXX help document

errors
  total number of errors, conflicts and unresolved conflicts

activity
  total number of object loads, stores and
  total number of database connections

cacheconnections
  number of active and total objects for each connection

cachetotals
  number of active objects of all connections
  (see cacheconnections above)

dbsize
  size of the database in megabyte


Configure Nagios
----------------

Put a line like this in your nagios plugin configuration to make the plugin
available::

  command[check_zope]=/path/to/check_zope.py -H $ARG1$ -p $ARG2$ -d $ARG3$
  -r $ARG4$ -a $ARG5$

Put a line like this in your nagios host configuration to use the::

  service[maggie]=Zope;0;24x7;10;5;5;gocept;10;24x7;1;1;1;;check_zope!localhost!8080!50000000!10000!admin:password

Configure Nagios
----------------

To get the correct command configuration for "check_zope", copy the zope.cfg
into your plugin config directory (debian: /usr/share/nagios/pluginconfig) or
the commands.cfg in /etc/nagios/.

Then you can make use of the check_zope command for services::

  define service{
              use                     generic-service
              host_name               thezopehost
              service_description     Zope
              check_command           check_zope!thezopehost!8080!1000000000!500000!admin:password
  }

Configure Munin
---------------

Symlink Plugins
```````````````

Create symlinks in ``/etc/munin/plugins/``

plugins using munin_client.py are named like::

  /etc/munin/plugins/zope_<graph>_<server-index>[_<dbname>]

  eg:
  /etc/munin/plugins/zope_uptime_instance1
  /etc/munin/plugins/zope_uptime_instance2
  /etc/munin/plugins/zope_activity_instance1_db2

plugins using zeo_munin.py are named like::

  /etc/munin/plugins/zeo_<graph>_<server-index>[_<storage>]

graph
  see `Munin data`_ for a list of available graphs

server-index
  host and port are looked up in the configuration
  MUNIN_ZEO_HOST|PORT_<server-index>

storage
  name of the storage, optional, defaults to 1


examples::

  /etc/munin/plugins/zeo_clients_ZEO1
  /etc/munin/plugins/zeo_clients_ZEO1_1
  /etc/munin/plugins/zeo_loadstores_ZEO1_temp



Configure Plugins
`````````````````

Add a configuration file to ``vim /etc/munin/plugin-conf.d/zope``
to tell the plugins how to connect to zeo server/clients::

  [zope_*]
  user root
  env.MUNIN_ZOPE_HOST_instance1 http://localhost:8401/Control_Panel/munin
  env.MUNIN_ZOPE_AUTHENTICATE_instance1 admin:admin
  env.MUNIN_ZOPE_HOST_instance2 http://localhost:8402/Control_Panel/munin
  env.MUNIN_ZOPE_AUTHENTICATE_instance2 admin:admin

  [zeo_*]
  user root
  env.MUNIN_ZEO_HOST_ZEO1 localhost
  env.MUNIN_ZEO_PORT_ZEO1 8502


Credits
-------

Originally written by Christian Theune <ct at gocept dot com>.

Thanks for contributing ideas and code to:

- Robrecht van Valkenburg (Pareto)
- Martijn Pieters (Pareto)
- Florian Schulze (independent)
- Hanno Schlichting (Jarn)
- Harald Friessnegger (Webmeisterei)
- David Glick (Groundwire)
