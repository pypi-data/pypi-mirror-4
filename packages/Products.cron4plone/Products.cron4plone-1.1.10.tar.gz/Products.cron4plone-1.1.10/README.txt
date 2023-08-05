Product description
===================
Cron4Plone can do scheduled tasks in Plone, in a syntax very like \*NIX
systems' cron daemon. It plugs into Zope's ClockServer machinery.

Optionally cron4plone also uses unimr.memcachedlock to make sure that
only one task is running at a time, even when using a distributed environment
like multiple zeo clients on multiple machines.

Rationale
=========
Cron4plone uses the clockserver and allows advanced task scheduling:

* Scheduled tasks at scheduled times. E.g. I want to perform a certain task at 
  3 AM on the first day of the month.
* Single thread running the task: We don't want 2 threads running the same task
  at the same time. When using clock server only this might happen if a task 
  takes longer than the tick period.


Installation
============

1. Configure the ticker in the buildout (or zope.conf)
------------------------------------------------------

`buildout.cfg`::

    [instance]
    ...
    eggs = 
        Products.cron4plone

    zope-conf-additional = 
      <clock-server>
          method /<your-plone-site>/@@cron-tick
          period 60
          user admin
          password admin_password
      </clock-server>

The `user` and `password` variables can be omitted, but are required if you
want to call a view that requires special permissions, for example when trying 
to create content.

1.1 Multiple instances
~~~~~~~~~~~~~~~~~~~~~~

If you have multiple Zope instances in your buildout, it makes sense to add the
`zope-conf-additional` to one instance only. This will ensure only one instance
will try to run the `@@cron-tick` method. 

`Products.cron4plone` should be present in all instances, or else the instance
won't have the software for CronTool object. This will cause errors on startup
and you won't be able to change the cron jobs.

1.2 Optionally use memcached server(s) to share locks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You would use memcached_ if your Zope instance runs on multiple machines. In
this case, all machines would run `@@cron-tick` at the same time, which is not
what you want, especially when creating content. Memcached will share a lock
between multiple machine, so only one machine will run the cron job.

A memcached server is a standalone server process which you can either
get via your favourite package manager (for Debian / Ubuntu:
`apt-get install memcached`)

Install and configure `memcached`, and add unimr.memcachedlock_ to 
`buildout.cfg`::

    [instance]
    ...
    eggs =
        Products.cron4plone
        unimr.memcachedlock

You can specify where you are running your memcached servers in the 
MEMCACHEDLOCK_SERVERS environment variable, e.g.::
    
    zope-conf-additional =
      <environment>
          MEMCACHEDLOCK_SERVERS <ip/hostname of host1>:<port>,<ip/hostname of host2>:<port>
      </environment>

The default port for memcached is 11211.

1.3 Optionally install memcached from buildout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can also build `memcached` from a buildout::

    parts +=
        memcached
        memcached-ctl
        supervisor

    [memcached]
    recipe = zc.recipe.cmmi
    url = http://memcached.googlecode.com/files/memcached-1.4.0.tar.gz
    extra_options = --with-libevent=${libevent:location}

    [memcached-ctl]
    recipe = ore.recipe.fs:mkfile
    path = ${buildout:bin-directory}/memcached
    mode = 0755
    content =
     #!/bin/sh
     PIDFILE=${memcached:location}/memcached.pid
        case "$1" in
          start)
           ${memcached:location}/bin/memcached -d -P $PIDFILE
            ;;
          stop)
            kill `cat $PIDFILE`
            ;;
          restart|force-reload)
            $0 stop
            sleep 1
            $0 start
            ;;
          *)
            echo "Usage: $SCRIPTNAME {start|stop|restart}" >&2
            exit 1
            ;;
        esac


You need to have the libevent development libraries
(apt-get install libevent-dev)
or in buildout::

    [libevent]
    recipe = zc.recipe.cmmi
    url = http://www.monkey.org/~provos/libevent-1.3b.tar.gz

Make sure that the libevent.so (shared object) file is in your
LD_LIBRARY_PATH before you start the memcached server if you build
the libevent library from the buildout.


If you use supervisor, you can add a line like this to start the
memcached server::

    10 memcached ${buildout:directory}/parts/memcached/bin/memcached

2. Configure the scheduled tasks
--------------------------------

In the Plone site setup, go to the cron4plone configuration. This form can 
be used to enter cron-like jobs. 

The cron job should have 5 elements: minute, hour, day_of_month, month and 
command expression. For `command`, a TAL expression can be used (including
'python: '). The variable `portal` is the Plone site root.

Examples::

    * 11 * * portal/@@run_me
    15,30 * * * python: portal.my_tool.runThis()

3. Wait and see
---------------

In the ZMI, go to the CronTool. If a cronjob has run the history is shown.


TODO
====
- Day of week is missing in cron-like syntax, add it.
- Send mail report each time a job run, or only when one fail.
- Improve doc test, currently test has basic coverage.
- Perhaps make a configuration form that allows users without cron syntax
  knowledge to enter jobs.

License and credits
===================

Authors: `Huub Bouma`_ and `Kim Chee Leong`_

License: This product is licensed under the GNU Public License version 2.
See the file docs/LICENSE.txt included in this product.

Parts of the code were taken from plonemaintenance_ by Ingeniweb_.

.. _plonemaintenance: http://plone.org/products/plonemaintenance 
.. _memcached: http://memcached.org/
.. _Ingeniweb: http://www.ingeniweb.com/
.. _unimr.memcachedlock: http://pypi.python.org/pypi/unimr.memcachedlock/
.. _Huub Bouma: mailto:bouma@gw20e.com
.. _Kim Chee Leong: mailto:leong@gw20e.com
