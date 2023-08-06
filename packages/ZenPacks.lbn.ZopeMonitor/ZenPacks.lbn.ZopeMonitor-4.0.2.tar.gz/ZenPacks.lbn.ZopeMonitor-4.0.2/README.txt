ZopeMonitor
-------------

ZopeMonitor provides a method for pulling performance metrics from a Zope
Application Server (http://www.zope.org/) directly into Zenoss. It is necessary
to first install the munin.zope eggs from pypi.python.org or our own repo at
http://linux.last-bastion.net/LBN/up2date/monitor, and to have wget installed
on this server.

The monitor works by utilising ZenCommand to run wget on the local system - you
do not need to make zope ports available through your firewall.

The munin plugins do require a user with 'View Management Screens' access at
the root however.  This is configured using the zZopeURI zProperty of the device.
This parameter uses Extended HTTP Authentication to specify user credentials, host
and port.  Note that the host is the hostname on the remote instance and should
probably remain 'localhost' unless you've explicitly bound your Zope to a NIC.

Note that the munin plugins expect to be installed on a Unix-like operating
system with a /proc filesystem.

The following metrics will be collected and graphed for the Zope Server.

    * Threads
      o  Free threads
      o  Total threads
    * Cache
      o  Total objects
      o  Total objects in memory
      o  Targe number
    * ZODB Activity
      o  Total connections
      o  Total load count
      o  Total store count
    * Memory Utilisation
      o  VmHWM - peak resident set size ("high water mark")
      o  VmExe - size of text segments
      o  VmStk - size of stack segments
      o  VmPeak - peak virtual memory size
      o  VmData - size of data segments
      o  VmLck - locked memory size
      o  VmPTE - page table entries size
      o  VmLib - shared library code size
      o  VmRSS - resident set size


Once your Zope Server has the munin plugins installed, you can add Zope monitoring 
to the device within Zenoss by simply binding the ZopeMonitor template to the device.

    1. Navigate to the device in the Zenoss web interface.
    2. Click the device menu, choose More then Templates.
    3. Click the templates menu, choose Bind Templates.
    4. Ctrl-click the ZopeMonitor template from /Devices/Server to choose it.
    5. Click OK.

You will now be collecting the Zope Server metrics from this device.

