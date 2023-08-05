==================================================
iiswsgi
==================================================
Serving Python WSGI applications natively from IIS
==================================================

The ``iiswsgi`` module implements a FastCGI to WSGI gateway that is
compatible with IIS's variation of the FastCGI protocol.  It also
provides utilities and helpers for building, packaging and deploying
`Microsoft Web Deploy`_ packages through the `Web Platform
Installer`_.

Sample Package
==============

The `examples\sample.msdeploy` sub-directory can be used to build a
sample MSDeploy package to be used with the `web-pi.xml` file as a
custom `Web Platform Installer feed
<http://blogs.iis.net/kateroh/archive/2009/10/24/web-pi-extensibility-custom-feeds-installing-custom-applications.aspx>`_
to test or as a basis for building your own packages and custom feeds.

  #. Exit the Web Platform Installer

     To make sure it uses the current version of the package and feed.

  #. Build the package
 
     A script is provided to make this easier.  Change to the directory
     containing this file in a `cmd.exe` prompt and run the following
     command::
 
       >C:\Python27\python.exe build_package.py
 
     That will build the package, clear the WebPI caches, and update
     the custom feed.
 
  #. Point WebPI to the local feed

     Skip this if you've already done it before.
   
     Force WebPI to use the modified feed.  Use the WebPI options
     screen to remove any previous Plone installer feeds and adding
     ``file:///C:/.../iiswsgi/examples/web-pi.xml`` replacing ``...``
     with the appropriate path.

  #. Install the package in WebPI

     Use the search box in WebPI to search for `iiswsgi`, click `Add`
     then click the `Install` button below and follow the
     instructions.

IIS FastCGI
===========

IIS' implementation of the FastCGI protocol is not fully compliant.
Most significantly, what is passed in on `STDIN_FILENO`_ is not a
handle to an open socket but rather to a `Windows named pipe`_.  This
names pipe does not support socket-like behavior, at least under
Python.  As such, the `iiswsgi.server` module extends `flup's WSGI to
FCGI gateway` to support using ``STDIN_FILENO`` opened twice, once
each approximating the `recv` and `send` end of a socket as is
specified in FastCGI.

IIS FastCGI Applications
------------------------

Use IIS's `AppCmd.exe
<http://learn.iis.net/page.aspx/114/getting-started-with-appcmdexe/>`_
to install a new FastCGI application.  You can find it at
``%ProgramFiles%\IIS Express\appcmd.exe`` for WebMatrix/IIS Express or
``%systemroot%\system32\inetsrv\AppCmd.exe`` for IIS.  Note that you
need to replace ``%SystemDrive%\Python27\Scripts\test.ini`` with the
full path to a `Paste Deploy INI configuration file
<http://pythonpaste.org/deploy/index.html?highlight=loadapp#introduction>`_
that defines the WSGI app and ``IISWSGI-Test`` with the name of your
app as IIS will see it::

    > appcmd.exe set config -section:system.webServer/fastCgi /+"[fullPath='%SystemDrive%\Python27\python.exe',arguments='-u %SystemDrive%\Python27\Scripts\iiswsgi-script.py -c %SystemDrive%\Python27\Scripts\test.ini',maxInstances='%NUMBER_OF_PROCESSORS%',monitorChangesTo='C:\Python27\Scripts\test.ini']" /commit:apphost
    > appcmd.exe set config -section:system.webServer/handlers /+"[name='IISWSGI-Test',path='iiswsgi-test.fcgi',verb='*',modules='FastCgiModule',scriptProcessor='%SystemDrive%\Python27\python.exe|-u %SystemDrive%\Python27\Scripts\iiswsgi-script.py -c %SystemDrive%\Python27\Scripts\test.ini']" /commit:apphost

See the `IIS FastCGI Reference
<http://www.iis.net/ConfigReference/system.webServer/fastCgi>`_ for
more details on how to configure IIS for FastCGI.  Note that you
cannot use environment variable in the `monitorChangesTo` argument,
IIS will return an opaque 500 error.

Known Issues
============

`System.IO.FileNotFoundException: Could not find file '\\?\C:\...`

    I've run into this error on Windows 7 on two different machines
    and multiple installs, one OEM and one vanilla Windows 7 Extreme.
    When this happens, it seems to happen when the "Web Platform
    Installer" has been run, then exited, and then run again without
    rebooting the machine in between.  To workaround this, you may
    have to reboot the machine.  See the stack overflow question `MS
    WebPI package runCommand not working in Manifest.xml`_ for more
    information.

TODO building a MSDeploy package from an existing project

.. _MS WebPI package runCommand not working in Manifest.xml: http://stackoverflow.com/questions/12485887/ms-webpi-package-runcommand-not-working-in-manifest-xml/12820574#12820574
.. _Windows named pipe: http://msdn.microsoft.com/en-us/library/windows/desktop/aa365590(v=vs.85).aspx
.. _STDIN_FILENO: http://www.fastcgi.com/drupal/node/6?q=node/22#S2.2
.. _Microsoft Web Deploy: http://www.iis.net/downloads/microsoft/web-deploy
.. _Web Platform Installer: http://www.microsoft.com/web/downloads/platform.aspx
