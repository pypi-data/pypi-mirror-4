.. contents::

Introduction
============

This package enable to monitoring of Zope 2 instance from the command line. It plugs zc.monitor (http://pypi.python.org/pypi/zc.monitor) and zc.z3monitor (http://pypi.python.org/pypi/zc.z3monitor) in Zope 2.
zc.monitor use zc.ngi server and define another thread to handle monitoring. This way you should still be able to monitor your application even if the
HTTPServer is hanging.

Probes
======

This package has been tested with probes coming from different packages:

  - zc.z3monitor
  - Products.ZNagios
  - zc.monitorcache
  - zc.monitorlogstats
  - ztfy.monitor

To register your own probe, just define a new utility providing the ``zc.z3monitor.interfaces.IZ3MonitorPlugin`` interface. Like this::

  <utility
     component=".zc_uptime"
     provides="zc.z3monitor.interfaces.IZ3MonitorPlugin"
     name="uptime" />

and the component should look like this::

  def zc_uptime(connection, database='main'):
      """uptime of the zope instance in seconds"""
      app = App()
      elapsed = time.time() - app.Control_Panel.process_start
      print >> connection, elapsed
      app._p_jar.close()

ZODB connection is always the first parameter. You can add your own parameters after.

Once you start your instance you should see something like::

  INFO zc.ngi.async.server listening on ('127.0.0.1', 8888)

The ngi server is started and you can look up values with netcat for example::

  echo 'uptime' | nc -i 1 localhost 8888
