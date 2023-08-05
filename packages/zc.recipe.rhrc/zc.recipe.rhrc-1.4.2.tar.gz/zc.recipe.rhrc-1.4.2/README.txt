*****************************************
ZC Buildout recipe for Redhat RC scripts
*****************************************

This package provides a zc.buildout recipe for creating Red-Hat Linux
compatible run-control scripts.

.. contents::

Changes
*******

1.4.2 (2012-12-20)
==================

Fixed: Errors were raised if stopping a run script failed during
       uninstall.  This could cause a buildout to be wedged, because
       you couldn't uninstall a broken/missing run script.


1.4.1 (2012-08-31)
==================

Fixed: Processes weren't started on update.

       In a perfect world, this wouldn't be necessary, as in the
       update case, the process would already be running, however,
       it's helpful to make sure the process is running by trying to
       start it.

1.4.0 (2012-05-18)
==================

- Added optional process-management support.  If requested, then run
  scripts are run as part of install and uninstall.

- Fixed: missing **test** dependency on ``zope.testing``

1.3.0 (2010/05/26)
==================

New Features
------------

- A new independent-processes option causes multiple processes to be
  restarted independently, rather then stoping all of the and the
  starting all of them.

Bugs Fixed
----------

- Generated run scripts had trailing whitespace.

1.2.0 (2009/04/06)
==================

displays the name of the script being run
for each script when it is started, stopped, or restarted

1.1.0 (2008/02/01)
==================

Use the deployment name option (as provided by zc.recipe.deployment
0.6.0 and later) if present when generating script names.

Use the deployment rc-directory as the destination when a deployment
is used.

Use /sbin/chkconfig rather than chkconfig, as I'm told it is always in
that location and rarely in anyone's path. :)

1.0.0 (2008/01/15)
==================

Initial public release
