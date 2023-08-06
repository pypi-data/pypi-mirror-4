***********************************************
Zope3 Application, Instance and Offline Recipes
***********************************************

Recipes for creating Zope 3 instances with distinguishing features:

- Don't use a skeleton

- Separates application and instance definition

- Don't support package-includes

- Support offline instance.

Unfortunately, partial Windows support at this time.  It works but it's alpha.

.. contents::


Releases
********

===================
0.18.0 (2013/02/05)
===================

- For the offline recipe, check the effective UID instead of the actual UID.
- Make the tests pass with modern buildouts, including buildout 2.


===================
0.17.0 (2012/02/07)
===================

- Added "location" value as output of the zopeconf recipe to make it
  easier to use in place of ``zc.recipe.deployment:configuration``.


===================
0.16.0 (2012/01/15)
===================

- Added support for using Paste Deployment to specify a WSGI stack
  over a zope.app-based application.


===================
0.15.0 (2011/12/12)
===================

- Added zopeconf recipe to produce decently-formatted zope.conf files,
  without constructing an instance.


===================
0.14.1 (2011/12/08)
===================

- Fixed ReST on pypi page.


===================
0.14.0 (2011/12/08)
===================

- Execute $PYTHONSTARTUP in the environment that the user will interact
  with in zc.zope3recipes.debugzope; this mirrors how $PYTHONSTARTUP is
  used with an interactive interpreter.
- Added a recipe for offline instance.
- Fixed tests to pass with zc.buildout >= v1.5


===================
0.13.0 (2010/11/24)
===================

- Support inserting additional code into the runzope & debugzope scripts
  using ``initialization`` and ``debug-initialization``.


===================
0.12.0 (2010/11/22)
===================

- Provide control for generation of the logrotate configuration, include the
  ability to suppress it when not desired.


===================
0.11.1 (2010/11/12)
===================

- Added an environment hook to enable logging for debugzope


===================
0.11.0 (2009/10/01)
===================

- Added support and tests for relative paths buildout option.
- Changed the dependency requirements to >=1.2.0 for zc.buildout and
  zc.recipe.egg because relative paths are added in these releases.
- Added missing release date for the previous release (0.10.0).


===================
0.10.0 (2009/09/16)
===================

Removed support for creating a logrotate script for the access.log because it
is not possible to reopen the log with ZDaemons ``reopen_transacript``. Note
however that is is possible to declare ``when`` and ``interval`` in a logfile
section to rotate logfiles internally.


==================
0.9.0 (2009/07/21)
==================

Updated tests to work with latest package versions.


==================
0.8.0 (2009/04/03)
==================

Added the "newest=false" option in the SetUp to prevent upgrade during tests

Added support for creating logrotate scripts when using a deployment recipe.


==================
0.7.0 (2008/02/01)
==================

Use the deployment name option (as provided by zc.recipe.deployment
0.6.0 and later) if present when generating instance file names.

You can now specify an instance name option that overrides the part
name for generated files.


==================
0.6.1 (2007/12/17)
==================

Fixed bug: The zope.conf site-definition option could not be overridden.


==================
0.6.0 (2007/11/03)
==================

Final release with Windows support.


==================
0.6b1 (2007/08/21)
==================

Windows support was added.


==================
0.5.5 (2007/07/26)
==================

Now debugzope takes the servers key of the application into account.


==================
0.5.3 (2007/07/14)
==================

Created another recipe called 'application' that installs Zope 3
solely from eggs.  The 'app' recipe is just an extension that also
supports Zope 3 from checkout or tarball.


==================
0.5.2 (2007/06/21)
==================

Use ZConfig's schema-free configuration parsing gain support for
%import.


==================
0.5.1 (2007/05/22)
==================

Support repeated keys in ZConfig sections.


==================
0.5.0 (2007/03/21)
==================

Support building Zope 3 application solely from eggs.
