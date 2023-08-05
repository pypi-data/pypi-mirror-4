=============================
plone.recipe.unifiedinstaller
=============================

This recipe is used by the Unified Installer Buildout to do finishing work like
writing the adminPassword.txt and ZEO control scripts.

Please file bugs to https://dev.plone.org/plone/newticket and specify
the component "Installer (Unified)".

Tests for this recipe are in the Unified Installer.

Options
=======

shell-command
    Full pathname to a POSIX-compliant shell. Used in ZEO start, stop, etc. scripts.
    Default: /bin/sh

sudo-command
    Command -- if needed -- to run process as root. Used only in adminPassword.txt.
    Default: ''

zeoserver
    Name of the ZEO server part if any. If missing, the recipe will scan other
    buildout parts for one using plone.recipe.zope2zeoserver and use its name.
    If a zeoserver is specified or found, ZEO start, stop, etc. scripts will
    be written.
    
clients
    Names of Zope client parts in the buildout. If missing, the recipe will
    scan other buildout parts for one using 
    plone.recipe.plone.recipe.zope2instance and use their names.
    
primary-port
    Port of the primary client instance. Used in the adminPassword.txt file.
    Default: 8080

user
    User name and password for the initial Zope administrator. Use
    the format "user:password"
    Default: None. Must be specified.


