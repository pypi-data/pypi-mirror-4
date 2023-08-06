===============
 Zope3 Recipes
===============

The Zope 3 recipes allow one to define Zope applications and instances
of those applications.  A Zope application is a collection of software
and software configuration, expressed as ZCML.  A Zope instance
invokes the application with a specific instance configuration.  A
single application may have many instances.

Building Zope 3 applications (from eggs)
========================================

The 'application' recipe can be used to define a Zope application.  It
is designed to work with with Zope solely from eggs.  The app recipe
causes a part to be created. The part will contain the scripts runzope
and debugzope and the application's site.zcml.  Both of the scripts
will require providing a -C option and the path to a zope.conf file
when run.  The debugzope script can be run with a script name and
arguments, in which case it will run the script, rather than starting
an interactive session.

The 'application' recipe accepts the following options:

site.zcml
  The contents of site.zcml.

eggs
  The names of one or more eggs, with their dependencies that should
  be included in the Python path of the generated scripts.


Lets define some (bogus) eggs that we can use in our application:

    >>> mkdir('demo1')
    >>> write('demo1', 'setup.py',
    ... '''
    ... from setuptools import setup
    ... setup(name = 'demo1')
    ... ''')

    >>> mkdir('demo2')
    >>> write('demo2', 'setup.py',
    ... '''
    ... from setuptools import setup
    ... setup(name = 'demo2', install_requires='demo1')
    ... ''')

.. Please note that the "newest=false" option is set in the test SetUp to
   prevent upgrades

We'll create a buildout.cfg file that defines our application:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = myapp
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:application
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ... ''' % globals())

Now, Let's run the buildout and see what we get:

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.

The runzope script runs the Web server:

    >>> cat('parts', 'myapp', 'runzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/demo2',
      '/sample-buildout/demo1',
      ]
    <BLANKLINE>
    import zope.app.twisted.main
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zope.app.twisted.main.main())

Here, unlike the above example the location path is not included
in ``sys.path``.  Similarly debugzope script is also changed:

    >>> cat('parts', 'myapp', 'debugzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/demo2',
      '/sample-buildout/demo1',
      '/zope3recipes',
      ]
    <BLANKLINE>
    import zope.app.twisted.main
    <BLANKLINE>
    <BLANKLINE>
    import zc.zope3recipes.debugzope
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zc.zope3recipes.debugzope.debug(main_module=zope.app.twisted.main))

The ``initialization`` setting can be used to provide a bit of
additional code that will be included in the runzope and debugzope
scripts just before the server's main function is called:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = myapp
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:application
    ... site.zcml = <include package="demo2" />
    ... eggs = demo2
    ... initialization =
    ...     print "Starting application server."
    ... ''')

Now, Let's run the buildout and see what we get:

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling myapp.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.

The runzope and debugzope scripts now include the additional code just
before server is started:

    >>> cat('parts', 'myapp', 'runzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/demo2',
      '/sample-buildout/demo1',
      ]
    <BLANKLINE>
    print "Starting application server."
    <BLANKLINE>
    import zope.app.twisted.main
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zope.app.twisted.main.main())

    >>> cat('parts', 'myapp', 'debugzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/demo2',
      '/sample-buildout/demo1',
      '/zope3recipes',
      ]
    <BLANKLINE>
    print "Starting application server."
    import zope.app.twisted.main
    <BLANKLINE>
    <BLANKLINE>
    import zc.zope3recipes.debugzope
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zc.zope3recipes.debugzope.debug(main_module=zope.app.twisted.main))

If the additional initialization for debugzope needs to be different
from that of runzope, the ``debug-initialization`` setting can be used.
If set, that is used for debugzope *instead* of the value of
``initialization``.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = myapp
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:application
    ... site.zcml = <include package="demo2" />
    ... eggs = demo2
    ... initialization =
    ...     print "Starting application server."
    ... debug-initialization =
    ...     print "Starting debugging interaction."
    ... ''')

Now, Let's run the buildout and see what we get:

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling myapp.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.

    >>> cat('parts', 'myapp', 'debugzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/demo2',
      '/sample-buildout/demo1',
      '/zope3recipes',
      ]
    <BLANKLINE>
    print "Starting debugging interaction."
    import zope.app.twisted.main
    <BLANKLINE>
    <BLANKLINE>
    import zc.zope3recipes.debugzope
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zc.zope3recipes.debugzope.debug(main_module=zope.app.twisted.main))

The runzope script still uses the ``initialization`` setting::

    >>> cat('parts', 'myapp', 'runzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/demo2',
      '/sample-buildout/demo1',
      ]
    <BLANKLINE>
    print "Starting application server."
    <BLANKLINE>
    import zope.app.twisted.main
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zope.app.twisted.main.main())

Setting ``debug-initialization`` to an empty string suppresses the
``initialization`` setting for the debugzope script:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = myapp
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:application
    ... site.zcml = <include package="demo2" />
    ... eggs = demo2
    ... initialization =
    ...     print "Starting application server."
    ... debug-initialization =
    ... ''')

Now, Let's run the buildout and see what we get:

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling myapp.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.

    >>> cat('parts', 'myapp', 'debugzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/demo2',
      '/sample-buildout/demo1',
      '/zope3recipes',
      ]
    <BLANKLINE>
    import zope.app.twisted.main
    <BLANKLINE>
    <BLANKLINE>
    import zc.zope3recipes.debugzope
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zc.zope3recipes.debugzope.debug(main_module=zope.app.twisted.main))


Relative paths
--------------

If requested in a buildout configuration, the scripts will be generated
with relative paths instead of absolute.

Let's change a buildout configuration to include ``relative-paths``.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = myapp
    ... relative-paths = true
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:application
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling myapp.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.

We get runzope script with relative paths.

    >>> cat('parts', 'myapp', 'runzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import os
    <BLANKLINE>
    join = os.path.join
    base = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
    base = os.path.dirname(base)
    base = os.path.dirname(base)
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      join(base, 'demo2'),
      join(base, 'demo1'),
      ]
    <BLANKLINE>
    import zope.app.twisted.main
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zope.app.twisted.main.main())

Similarly, debugzope script has relative paths.

    >>> cat('parts', 'myapp', 'debugzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import os
    <BLANKLINE>
    join = os.path.join
    base = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
    base = os.path.dirname(base)
    base = os.path.dirname(base)
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      join(base, 'demo2'),
      join(base, 'demo1'),
      '/zope3recipes',
      ]
    <BLANKLINE>
    import zope.app.twisted.main
    <BLANKLINE>
    <BLANKLINE>
    import zc.zope3recipes.debugzope
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zc.zope3recipes.debugzope.debug(main_module=zope.app.twisted.main))


Building Zope 3 Applications (from Zope 3 checkouts/tarballs)
=============================================================

The 'app' recipe works much like the 'application' recipe.  It takes
the same configuration options plus the following one:

zope3
  The name of a section defining a location option that gives the
  location of a Zope installation.  This can be either a checkout or a
  distribution.  If the location has a lib/python subdirectory, it is
  treated as a distribution, otherwise, it must have a src
  subdirectory and will be treated as a checkout. This option defaults
  to "zope3".  And if location is empty, the application will run solely
  from eggs.

Let's look at an example.  We'll make a faux zope installation:

    >>> zope3 = tmpdir('zope3')
    >>> mkdir(zope3, 'src')

Now we'll create a buildout.cfg file that defines our application:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = myapp
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ... ''' % globals())

Note that our site.zcml file is very small.  It expect the application
zcml to define almost everything.  In fact, a site.zcml file will often
include just a single include directive.  We don't need to include the
surrounding configure element, unless we want a namespace other than
the zope namespace.  A configure directive will be included for us.

Let's run the buildout and see what we get:

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling myapp.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.

A directory is created in the parts directory for our application
files. Starting with zc.buildout >= v1.5, and distribute, a "buildout"
directory is created in the parts folder. Since the minimum version we support
for zc.buildout is lower than v1.5, we use a custom "ls" functional called
"ls_optional" to which we pass a list of folders that may be present. These are
ignore by the function.

    >>> from zc.zope3recipes.tests import ls_optional
    >>> ls_optional('parts', ignore=('buildout',))
    d  myapp

    >>> ls('parts', 'myapp')
    -  debugzope
    -  runzope
    -  site.zcml

We get 3 files, two scripts and a site.zcml file.  The site.zcml file
is just what we had in the buildout configuration:

    >>> cat('parts', 'myapp', 'site.zcml')
    <configure xmlns='http://namespaces.zope.org/zope'
               xmlns:meta="http://namespaces.zope.org/meta"
               >
    <include package="demo2" />
    <principal
    id="zope.manager"
    title="Manager"
    login="jim"
    password_manager="SHA1"
    password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    />
    <grant
    role="zope.Manager"
    principal="zope.manager"
    />
    </configure>

Unfortunately, the leading whitespace is stripped from the
configuration file lines.  This is a consequence of the way
ConfigParser works.

The runzope script runs the Web server:

    >>> cat('parts', 'myapp', 'runzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/demo2',
      '/sample-buildout/demo1',
      '/zope3/src',
      ]
    <BLANKLINE>
    import zope.app.twisted.main
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zope.app.twisted.main.main())

It includes in it's path the eggs we specified in the configuration
file, along with their dependencies. Note that we haven't specified a
configuration file.  When runzope is run, a -C option must be used to
provide a configuration file.  -X options can also be provided to
override configuration file options.

The debugzope script provides access to the object system.  When
debugzope is run, a -C option must be used to provide a configuration
file.  -X options can also be provided to override configuration file
options.  If run without any additional arguments, then an interactive
interpreter will be started with databases specified in the
configuration file opened and with the variable root set to the
application root object.  The debugger variable is set to a Zope 3
debugger.  If additional arguments are provided, then the first
argument should be a script name and the remaining arguments are
script arguments.  The script will be run with the root and debugger
variables available as global variables.

..

    >>> cat('parts', 'myapp', 'debugzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/demo2',
      '/sample-buildout/demo1',
      '/zope3/src',
      '/zope3recipes',
      ]
    <BLANKLINE>
    import zope.app.twisted.main
    <BLANKLINE>
    <BLANKLINE>
    import zc.zope3recipes.debugzope
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zc.zope3recipes.debugzope.debug(main_module=zope.app.twisted.main))

Note that the runzope shown above uses the default, twisted-based
server components.  It's possible to specify which set of server
components is used: the "servers" setting can be set to either
"zserver" or "twisted".  For the application, this affects the runzope
script; we'll see additional differences when we create instances of
the application.

Let's continue to use the twisted servers, but make the selection
explicit:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = myapp
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... servers = twisted
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Updating myapp.

Note that this is recognized as not being a change to the
configuration; the messages say that myapp was updated, not
uninstalled and then re-installed.

The runzope script generated is identical to what we saw before:

    >>> cat('parts', 'myapp', 'runzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/demo2',
      '/sample-buildout/demo1',
      '/zope3/src',
      ]
    <BLANKLINE>
    import zope.app.twisted.main
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zope.app.twisted.main.main())

We can also specify the ZServer servers explicitly:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = myapp
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... servers = zserver
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling myapp.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.

The part has been re-installed, and the runzope script generated is
different now.  Note that the main() function is imported from a
different package this time:

    >>> cat('parts', 'myapp', 'runzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/demo2',
      '/sample-buildout/demo1',
      '/zope3/src',
      ]
    <BLANKLINE>
    import zope.app.server.main
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zope.app.server.main.main())

The debugzope script has also been modified to take this into account.

    >>> cat('parts', 'myapp', 'debugzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/demo2',
      '/sample-buildout/demo1',
      '/zope3/src',
      '/zope3recipes',
      ]
    <BLANKLINE>
    import zope.app.server.main
    <BLANKLINE>
    <BLANKLINE>
    import zc.zope3recipes.debugzope
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zc.zope3recipes.debugzope.debug(main_module=zope.app.server.main))


Relative paths
--------------

We can also request relative paths.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = myapp
    ... relative-paths = true
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... servers = zserver
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling myapp.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.

The runzope script has relative paths.

    >>> cat('parts', 'myapp', 'runzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import os
    <BLANKLINE>
    join = os.path.join
    base = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
    base = os.path.dirname(base)
    base = os.path.dirname(base)
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      join(base, 'demo2'),
      join(base, 'demo1'),
      '/zope3/src',
      ]
    <BLANKLINE>
    import zope.app.server.main
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zope.app.server.main.main())

The debugzope script also has relative paths.

    >>> cat('parts', 'myapp', 'debugzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import os
    <BLANKLINE>
    join = os.path.join
    base = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
    base = os.path.dirname(base)
    base = os.path.dirname(base)
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      join(base, 'demo2'),
      join(base, 'demo1'),
      '/zope3/src',
      '/zope3recipes',
      ]
    <BLANKLINE>
    import zope.app.server.main
    <BLANKLINE>
    <BLANKLINE>
    import zc.zope3recipes.debugzope
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zc.zope3recipes.debugzope.debug(main_module=zope.app.server.main))


Legacy Functional Testing Support
---------------------------------

Zope 3's functional testing support is based on zope.testing test
layers. There is a default functional test layer that older functional
tests use.  This layer loads the default configuration for the Zope
application server.  It exists to provide support for older functional
tests that were written before layers were added to the testing
infrastructure.   The default testing layer has a number of
disadvantages:

- It loads configurations for a large number of packages.  This has
  the potential to introduce testing dependency on all of these
  packages.

- It required a ftesting.zcml file and makes assumptions about where
  that file is.  In particular, it assumes a location relative to the
  current working directory when the test is run.

Newer software and maintained software should use their own functional
testing layers that use test-configuration files defined in packages.

To support older packages that use the default layer, a ftesting.zcml
option is provided.  If it is used, then the contents of the option
are written to a ftesting.zcml file in the application.  In addition,
an ftesting-base.zcml file is written that includes configuration
traditionally found in a Zope 3 ftesting-base.zcml excluding reference
to package-includes.

If we modify our buildout to include an ftesting.zcml option:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = myapp
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... ftesting.zcml =
    ...    <meta:provides feature="devmode" />
    ...    <include file="ftesting-base.zcml" />
    ...    <includeOverrides package="demo2" />
    ... eggs = demo2
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling myapp.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.

We'll get ftesting.zcml files and ftesting-base.zcml files created in
the application:

    >>> cat('parts', 'myapp', 'ftesting.zcml')
    <configure xmlns='http://namespaces.zope.org/zope'
               xmlns:meta="http://namespaces.zope.org/meta"
               >
    <BLANKLINE>
    <meta:provides feature="devmode" />
    <include file="ftesting-base.zcml" />
    <includeOverrides package="demo2" />
    </configure>

    >>> cat('parts', 'myapp', 'ftesting-base.zcml')
    <BLANKLINE>
    <configure
       xmlns="http://namespaces.zope.org/zope"
       i18n_domain="zope"
       >
      <include package="zope.app" />
      <include package="zope.app" file="ftesting.zcml" />
      <include package="zope.app.securitypolicy" file="meta.zcml" />
      <include package="zope.app.securitypolicy" />
      <securityPolicy
        component="zope.app.securitypolicy.zopepolicy.ZopeSecurityPolicy" />
      <role id="zope.Anonymous" title="Everybody"
                     description="All users have this role implicitly" />
      <role id="zope.Manager" title="Site Manager" />
      <role id="zope.Member" title="Site Member" />
      <grant permission="zope.View"
                      role="zope.Anonymous" />
      <grant permission="zope.app.dublincore.view"
                      role="zope.Anonymous" />
      <grantAll role="zope.Manager" />
      <include package="zope.app.securitypolicy.tests"
               file="functional.zcml" />
      <unauthenticatedPrincipal
          id="zope.anybody"
          title="Unauthenticated User"
          />
      <unauthenticatedGroup
        id="zope.Anybody"
        title="Unauthenticated Users"
        />
      <authenticatedGroup
        id="zope.Authenticated"
        title="Authenticated Users"
        />
      <everybodyGroup
        id="zope.Everybody"
        title="All Users"
        />
      <principal
          id="zope.mgr"
          title="Manager"
          login="mgr"
          password="mgrpw" />
      <principal
          id="zope.globalmgr"
          title="Manager"
          login="globalmgr"
          password="globalmgrpw" />
      <grant role="zope.Manager" principal="zope.globalmgr" />
    </configure>

Defining Zope3 instances
========================

Having defined an application, we can define one or more instances of
the application.  We do this using the zc.zope3recipes instance
recipe.  The instance recipe has 2 modes, a development and a
production mode.  We'll start with the development mode.  In
development mode, a part directory will be created for each instance
containing the instance's configuration files. This directory will
also contain run-time files created by the instances, such as log
files or zdaemon socket files.

When defining an instance, we need to specify a zope.conf file.  The
recipe can do most of the work for us.  Let's look at a a basic
example:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ... ''' % globals())

The application option names an application part.  The application
part will be used to determine the location of the site.zcml file and
the name of the control script to run.

We specified a zope.conf option which contains a start at our final
zope.conf file.  The recipe will add some bits we leave out.  The one
thing we really need to have is a database definition.  We simply
include the zconfig option from the database section, which we provide
as a file storage part using the zc.recipe.filestorage recipe.  The
filestorage recipe will create a directory to hold our database and
compute a zconfig option that we can use in our instance section.

Note that we've replaced the myapp part with the instance part.  The
myapp part will be included by virtue of the reference from the
instance part.

Let's run the buildout, and see what we get:

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling myapp.
    Installing database.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.
    Installing instance.
    Generated script '/sample-buildout/bin/instance'.

We see that the database and myapp parts were included by virtue of
being referenced from the instance part.

We get new directories for our database and instance:

    >>> ls_optional('parts', ignore=('buildout',))
    d  database
    d  instance
    d  myapp

The instance directory contains zdaemon.conf and zope.conf files:

    >>> ls('parts', 'instance')
    -  zdaemon.conf
    -  zope.conf

Let's look at the zope.conf file that was generated:

    >>> cat('parts', 'instance', 'zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    </zodb>
    <BLANKLINE>
    <server>
      address 8080
      type HTTP
    </server>
    <BLANKLINE>
    <accesslog>
      <logfile>
        path /sample-buildout/parts/instance/access.log
      </logfile>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>

This uses the twisted server types, since that's the default
configuration for Zope 3.  If we specify use of the ZServer servers,
the names of the server types are adjusted appropriately:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... servers = zserver
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Uninstalling myapp.
    Updating database.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.
    Installing instance.
    Generated script '/sample-buildout/bin/instance'.

The generated zope.conf file now uses the ZServer server components
instead:

    >>> cat('parts', 'instance', 'zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    </zodb>
    <BLANKLINE>
    <server>
      address 8080
      type WSGI-HTTP
    </server>
    <BLANKLINE>
    <accesslog>
      <logfile>
        path /sample-buildout/parts/instance/access.log
      </logfile>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>

The Twisted-based servers can also be specified explicitly:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... servers = twisted
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Uninstalling myapp.
    Updating database.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.
    Installing instance.
    Generated script '/sample-buildout/bin/instance'.

The generated zope.conf file now uses the Twisted server components
once more:

    >>> cat('parts', 'instance', 'zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    </zodb>
    <BLANKLINE>
    <server>
      address 8080
      type HTTP
    </server>
    <BLANKLINE>
    <accesslog>
      <logfile>
        path /sample-buildout/parts/instance/access.log
      </logfile>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>

It includes the database definition that we provided in the zope.conf
option.  It has a site-definition option that names the site.zcml file
from our application directory.

We didn't specify any server or logging ZConfig sections, so some were
generated for us.

Note that, by default, the event-log output goes to standard output.
We'll say more about that when we talk about the zdaemon
configuration later.

If we specify a server section ourselves:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ...    <server>
    ...        type PostmortemDebuggingHTTP
    ...        address 8080
    ...    </server>
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Updating database.
    Updating myapp.
    Installing instance.
    Generated script '/sample-buildout/bin/instance'.

Then the section (or sections) we provide will be used and new ones
won't be added:

    >>> cat('parts', 'instance', 'zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    </zodb>
    <BLANKLINE>
    <server>
      address 8080
      type PostmortemDebuggingHTTP
    </server>
    <BLANKLINE>
    <accesslog>
      <logfile>
        path /sample-buildout/parts/instance/access.log
      </logfile>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>

If we just want to specify alternate ports or addresses, we can use
the address option which accepts zero or more address specifications:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ... address = 8081 foo.com:8082
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Updating database.
    Updating myapp.
    Installing instance.
    Generated script '/sample-buildout/bin/instance'.

    >>> cat('parts', 'instance', 'zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    </zodb>
    <BLANKLINE>
    <server>
      address 8081
      type HTTP
    </server>
    <BLANKLINE>
    <server>
      address foo.com:8082
      type HTTP
    </server>
    <BLANKLINE>
    <accesslog>
      <logfile>
        path /sample-buildout/parts/instance/access.log
      </logfile>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>

We can specify our own accesslog and eventlog configuration.  For
example, to send the event-log output to a file and suppress the
access log:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ...    <eventlog>
    ...      <logfile>
    ...        path ${buildout:parts-directory}/instance/event.log
    ...        formatter zope.exceptions.log.Formatter
    ...      </logfile>
    ...    </eventlog>
    ...    <accesslog>
    ...    </accesslog>
    ...
    ... address = 8081
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Updating database.
    Updating myapp.
    Installing instance.
    Generated script '/sample-buildout/bin/instance'.

    >>> cat('parts', 'instance', 'zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    </zodb>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path /sample-buildout/parts/instance/event.log
      </logfile>
    </eventlog>
    <BLANKLINE>
    <accesslog>
    </accesslog>
    <BLANKLINE>
    <server>
      address 8081
      type HTTP
    </server>

Let's look at the zdaemon.conf file:

    >>> cat('parts', 'instance', 'zdaemon.conf')
    <runner>
      daemon on
      directory /sample-buildout/parts/instance
      program /sample-buildout/parts/myapp/runzope -C /sample-buildout/parts/instance/zope.conf
      socket-name /sample-buildout/parts/instance/zdaemon.sock
      transcript /sample-buildout/parts/instance/z3.log
    </runner>
    <BLANKLINE>
    <eventlog>
      <logfile>
        path /sample-buildout/parts/instance/z3.log
      </logfile>
    </eventlog>

Here we see a fairly ordinary zdaemon.conf file.  The program option
refers to the runzope script in our application directory.  The socket
file, used for communication between the zdaemon command-line script
and the zademon manager is placed in the instance directory.

If you want to override any part of the generated zdaemon output,
simply provide a zdaemon.conf option in your instance section:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ... address = 8081
    ... zdaemon.conf =
    ...     <runner>
    ...       daemon off
    ...       socket-name /sample-buildout/parts/instance/sock
    ...       transcript /dev/null
    ...     </runner>
    ...     <eventlog>
    ...     </eventlog>
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Updating database.
    Updating myapp.
    Installing instance.
    Generated script '/sample-buildout/bin/instance'.

    >>> cat('parts', 'instance', 'zdaemon.conf')
    <runner>
      daemon off
      directory /sample-buildout/parts/instance
      program /sample-buildout/parts/myapp/runzope -C /sample-buildout/parts/instance/zope.conf
      socket-name /sample-buildout/parts/instance/sock
      transcript /dev/null
    </runner>
    <BLANKLINE>
    <eventlog>
    </eventlog>

In addition to the configuration files, a control script is generated
in the buildout bin directory:

    >>> ls('bin')
    -  buildout
    -  instance

..

    >>> cat('bin', 'instance')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/eggs/zdaemon-2.0-py2.4.egg',
      '/sample-buildout/eggs/setuptools-0.6-py2.4.egg',
      '/sample-buildout/eggs/ZConfig-2.3-py2.4.egg',
      '/zope3recipes',
      ]
    <BLANKLINE>
    import zc.zope3recipes.ctl
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zc.zope3recipes.ctl.main([
            '/sample-buildout/parts/myapp/debugzope',
            '/sample-buildout/parts/instance/zope.conf',
            '-C', '/sample-buildout/parts/instance/zdaemon.conf',
            ]+sys.argv[1:]
            ))

Some configuration sections can include a key multiple times; the ZEO
client section works this way.  When a key is given multiple times,
all values are included in the resulting configuration in the order in
which they're give in the input::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf =
    ...     <zodb>
    ...       <zeoclient>
    ...         server 127.0.0.1:8001
    ...         server 127.0.0.1:8002
    ...       </zeoclient>
    ...     </zodb>
    ... address = 8081
    ... zdaemon.conf =
    ...     <runner>
    ...       daemon off
    ...       socket-name /sample-buildout/parts/instance/sock
    ...       transcript /dev/null
    ...     </runner>
    ...     <eventlog>
    ...     </eventlog>
    ...
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Uninstalling database.
    Updating myapp.
    Installing instance.
    Generated script '/sample-buildout/bin/instance'.

    >>> cat('parts', 'instance', 'zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <zeoclient>
        server 127.0.0.1:8001
        server 127.0.0.1:8002
      </zeoclient>
    </zodb>
    <BLANKLINE>
    <server>
      address 8081
      type HTTP
    </server>
    <BLANKLINE>
    <accesslog>
      <logfile>
        path /sample-buildout/parts/instance/access.log
      </logfile>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>

Instance names
--------------

The instance recipe generates files or directories based on its name,
which defaults to the part name.  We can specify a different name
using the name option.  This doesn't effect which parts directory is
used, but it does affect the name of the run script in bin:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... name = server
    ... application = myapp
    ... zope.conf =
    ...     <zodb>
    ...       <zeoclient>
    ...         server 127.0.0.1:8001
    ...         server 127.0.0.1:8002
    ...       </zeoclient>
    ...     </zodb>
    ... address = 8081
    ... zdaemon.conf =
    ...     <runner>
    ...       daemon off
    ...       socket-name /sample-buildout/parts/instance/sock
    ...       transcript /dev/null
    ...     </runner>
    ...     <eventlog>
    ...     </eventlog>
    ...
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Updating myapp.
    Installing instance.
    Generated script '/sample-buildout/bin/server'.


Specifying an alternate site definition
---------------------------------------

Ideally, ZCML is used to configure the software used by an application
and zope.conf is used to provide instance-specific configuration.  For
historical reasons, there are ZCML directives that provide process
configuration.  A good example of this is the smtpMailer directive
provided by the zope.sendmail package.  We can override the
site-definition option in the zope.conf file to specify an alternate
zcml file.  Here, we'll update out instance configuration to use an
alternate site definition:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf =
    ...     site-definition ${buildout:directory}/site.zcml
    ...     <zodb>
    ...       <zeoclient>
    ...         server 127.0.0.1:8001
    ...         server 127.0.0.1:8002
    ...       </zeoclient>
    ...     </zodb>
    ... address = 8081
    ... zdaemon.conf =
    ...     <runner>
    ...       daemon off
    ...       socket-name /sample-buildout/parts/instance/sock
    ...       transcript /dev/null
    ...     </runner>
    ...     <eventlog>
    ...     </eventlog>
    ...
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Updating myapp.
    Installing instance.
    Generated script '/sample-buildout/bin/instance'.

    >>> cat('parts', 'instance', 'zope.conf')
    site-definition /sample-buildout/site.zcml
    <BLANKLINE>
    <zodb>
      <zeoclient>
        server 127.0.0.1:8001
        server 127.0.0.1:8002
      </zeoclient>
    </zodb>
    <BLANKLINE>
    <server>
      address 8081
      type HTTP
    </server>
    <BLANKLINE>
    <accesslog>
      <logfile>
        path /sample-buildout/parts/instance/access.log
      </logfile>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>

(Note that, in practice, you'll often use the
zc.recipe.deployment:configuration recipe,
http://pypi.python.org/pypi/zc.recipe.deployment#configuration-files,
to define a site.zcml file using the buildout.)

Log files
---------

The log file settings deserver some explanation.  The Zope event log
only captures output from logging calls.  In particular, it doesn't
capture startup errors written to standard error.  The zdaemon
transcript log is very useful for capturing this output.  Without it,
error written to standard error are lost when running as a daemon.
The default Zope 3 configuration in the past was to write the Zope
access and event log output to both files and standard output and to
define a transcript log.  This had the effect that the transcript
duplicated the contents of the event log and access logs, in addition
to capturing other output.  This was space inefficient.

This recipe's approach is to combine the zope and zdaemon event-log
information as well as Zope error output into a single log file.  We
do this by directing Zope's event log to standard output, where it is
useful when running Zope in foreground mode and where it can be
captured by the zdaemon transcript log.

Unix Deployments
----------------

The instance recipe provides support for Unix deployments, as provided
by the zc.recipe.deployment recipe.  A deployment part defines a number of
options used by the instance recipe:

etc-directory
    The name of the directory where configuration files should be
    placed.  This defaults to /etc/NAME, where NAME is the deployment
    name.

log-directory
    The name of the directory where application instances should write
    their log files.  This defaults to /var/log/NAME, where NAME is
    the deployment name.

run-directory
    The name of the directory where application instances should put
    their run-time files such as pid files and inter-process
    communication socket files.  This defaults to /var/run/NAME, where
    NAME is the deployment name.

rc-directory
    The name of the directory where run-control scripts should be
    installed.

logrotate-directory
    The name ot the directory where logrotate configuration files should be
    installed.

user
    The name of a user that processes should run as.

The deployment recipe has to be run as root for various reasons, but
we can create a faux deployment by providing a section with the needed
data. Let's update our configuration to use a deployment.  We'll first
create a faux installation root:

    >>> root = tmpdir('root')
    >>> mkdir(root, 'etc')
    >>> mkdir(root, 'etc', 'myapp-run')
    >>> mkdir(root, 'etc', 'init.d')
    >>> mkdir(root, 'etc', 'logrotate.d')

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ... address = 8081
    ... deployment = myapp-deployment
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ...
    ... [myapp-deployment]
    ... name = myapp-run
    ... etc-directory = %(root)s/etc/myapp-run
    ... rc-directory = %(root)s/etc/init.d
    ... logrotate-directory = %(root)s/etc/logrotate.d
    ... log-directory = %(root)s/var/log/myapp-run
    ... run-directory = %(root)s/var/run/myapp-run
    ... user = zope
    ... ''' % globals())

Here we've added a deployment section, myapp-deployment, and added a
deployment option to our instance part telling the instance recipe to
use the deployment.  If we rerun the buildout:

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Installing database.
    Updating myapp.
    Installing instance.
    Generated script '/root/etc/init.d/myapp-run-instance'.

The installer files will move.  We'll no-longer have the instance part:

    >>> ls_optional('parts', ignore=('buildout',))
    d  database
    d  myapp

or the control script:

    >>> ls('bin')
    -  buildout

Rather, we'll get our configuration files in the /etc/myapp-run directory:

    >>> ls(root, 'etc', 'myapp-run')
    -  instance-zdaemon.conf
    -  instance-zope.conf

Note that the instance name was added as a prefix to the file names,
since we'll typically have additional instances in the deployment.

The control script is in the init.d directory:

    >>> ls(root, 'etc', 'init.d')
    -  myapp-run-instance

Note that the deployment name is added as a prefix of the control
script name.

The logrotate file is in the logrotate.d directory:

    >>> ls(root, 'etc', 'logrotate.d')
    -  myapp-run-instance


The configuration files have changed to reflect the deployment
locations:

    >>> cat(root, 'etc', 'myapp-run', 'instance-zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    </zodb>
    <BLANKLINE>
    <server>
      address 8081
      type HTTP
    </server>
    <BLANKLINE>
    <accesslog>
      <logfile>
        path /root/var/log/myapp-run/instance-access.log
      </logfile>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>

    >>> cat(root, 'etc', 'myapp-run', 'instance-zdaemon.conf')
    <runner>
      daemon on
      directory /root/var/run/myapp-run
      program /sample-buildout/parts/myapp/runzope -C /root/etc/myapp-run/instance-zope.conf
      socket-name /root/var/run/myapp-run/instance-zdaemon.sock
      transcript /root/var/log/myapp-run/instance-z3.log
      user zope
    </runner>
    <BLANKLINE>
    <eventlog>
      <logfile>
        path /root/var/log/myapp-run/instance-z3.log
      </logfile>
    </eventlog>

    >>> cat(root, 'etc', 'logrotate.d', 'myapp-run-instance')
    /root/var/log/myapp-run/instance-z3.log {
      rotate 5
      weekly
      postrotate
        /root/etc/init.d/myapp-run-instance reopen_transcript
      endscript
    }


If we provide an alternate instance name, that will be reflected in
the generated files:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... name = server
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ... address = 8081
    ... deployment = myapp-deployment
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ...
    ... [myapp-deployment]
    ... name = myapp-run
    ... etc-directory = %(root)s/etc/myapp-run
    ... rc-directory = %(root)s/etc/init.d
    ... logrotate-directory = %(root)s/etc/logrotate.d
    ... log-directory = %(root)s/var/log/myapp-run
    ... run-directory = %(root)s/var/run/myapp-run
    ... user = zope
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Updating database.
    Updating myapp.
    Installing instance.
    Generated script '/root/etc/init.d/myapp-run-server'.

    >>> cat(root, 'etc', 'myapp-run', 'server-zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    </zodb>
    <BLANKLINE>
    <server>
      address 8081
      type HTTP
    </server>
    <BLANKLINE>
    <accesslog>
      <logfile>
        path /root/var/log/myapp-run/server-access.log
      </logfile>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>

    >>> cat(root, 'etc', 'myapp-run', 'server-zdaemon.conf')
    <runner>
      daemon on
      directory /root/var/run/myapp-run
      program /sample-buildout/parts/myapp/runzope -C /root/etc/myapp-run/server-zope.conf
      socket-name /root/var/run/myapp-run/server-zdaemon.sock
      transcript /root/var/log/myapp-run/server-z3.log
      user zope
    </runner>
    <BLANKLINE>
    <eventlog>
      <logfile>
        path /root/var/log/myapp-run/server-z3.log
      </logfile>
    </eventlog>


Controlling logrotate configuration
-----------------------------------

Some applications control their own log rotation policies.  In these
cases, we don't want the logrotate configuration to be generated.

Setting the logrotate.conf setting affects the configuration.  Setting
it explicitly controls the content of the logrotate file for the
instance; setting it to an empty string causes it not to be generated at
all.

Let's take a look at setting the content to a non-empty value directly:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ... address = 8081
    ... deployment = myapp-deployment
    ... logrotate.conf =
    ...       /root/var/log/myapp-run/instance-z3.log {
    ...         rotate 10
    ...         daily
    ...         postrotate
    ...           /root/etc/init.d/myapp-run-instance reopen_transcript
    ...         endscript
    ...       }
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ...
    ... [myapp-deployment]
    ... name = myapp-run
    ... etc-directory = %(root)s/etc/myapp-run
    ... rc-directory = %(root)s/etc/init.d
    ... logrotate-directory = %(root)s/etc/logrotate.d
    ... log-directory = %(root)s/var/log/myapp-run
    ... run-directory = %(root)s/var/run/myapp-run
    ... user = zope
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Uninstalling myapp.
    Updating database.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.
    Installing instance.
    Generated script '/root/etc/init.d/myapp-run-instance'.

    >>> cat(root, 'etc', 'logrotate.d', 'myapp-run-instance')
    /root/var/log/myapp-run/instance-z3.log {
      rotate 10
      daily
      postrotate
        /root/etc/init.d/myapp-run-instance reopen_transcript
      endscript
    }

If we set ``logrotate.conf`` to an empty string, the file is not generated:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ... address = 8081
    ... deployment = myapp-deployment
    ... logrotate.conf =
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ...
    ... [myapp-deployment]
    ... name = myapp-run
    ... etc-directory = %(root)s/etc/myapp-run
    ... rc-directory = %(root)s/etc/init.d
    ... logrotate-directory = %(root)s/etc/logrotate.d
    ... log-directory = %(root)s/var/log/myapp-run
    ... run-directory = %(root)s/var/run/myapp-run
    ... user = zope
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Updating database.
    Updating myapp.
    Installing instance.
    Generated script '/root/etc/init.d/myapp-run-instance'.

    >>> ls(root, 'etc', 'logrotate.d')


Defining multiple similar instances
-----------------------------------

Often you want to define multiple instances that differ only by one or
two options (e.g. an address).  The extends option lets you name a
section from which default options should be loaded.  Any options in
the source section not defined in the extending section are added to
the extending section.

Let's update our buildout to add a new instance:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance instance2
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ... address = 8081
    ... deployment = myapp-deployment
    ...
    ... [instance2]
    ... recipe = zc.zope3recipes:instance
    ... extends = instance
    ... address = 8082
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ...
    ... [myapp-deployment]
    ... name = myapp-run
    ... etc-directory = %(root)s/etc/myapp-run
    ... rc-directory = %(root)s/etc/init.d
    ... logrotate-directory = %(root)s/etc/logrotate.d
    ... log-directory = %(root)s/var/log/myapp-run
    ... run-directory = %(root)s/var/run/myapp-run
    ... user = zope
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Uninstalling myapp.
    Updating database.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.
    Installing instance.
    Generated script '/root/etc/init.d/myapp-run-instance'.
    Installing instance2.
    Generated script '/root/etc/init.d/myapp-run-instance2'.

Now, we have the new instance configuration files:

    >>> ls(root, 'etc', 'myapp-run')
    -  instance-zdaemon.conf
    -  instance-zope.conf
    -  instance2-zdaemon.conf
    -  instance2-zope.conf

    >>> cat(root, 'etc', 'myapp-run', 'instance2-zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    </zodb>
    <BLANKLINE>
    <server>
      address 8082
      type HTTP
    </server>
    <BLANKLINE>
    <accesslog>
      <logfile>
        path /root/var/log/myapp-run/instance2-access.log
      </logfile>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>


Relative paths
--------------

Relative paths will be used in the control script if they are requested
in a buildout configuration.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ... relative-paths = true
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance2.
    Uninstalling instance.
    Uninstalling myapp.
    Updating database.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.
    Installing instance.
    Generated script '/sample-buildout/bin/instance'.

    Both ``sys.path`` and arguments to the `ctl` are using relative
    paths now.

    >>> cat('bin', 'instance')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import os
    <BLANKLINE>
    join = os.path.join
    base = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
    base = os.path.dirname(base)
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      join(base, 'eggs/zdaemon-pyN.N.egg'),
      join(base, 'eggs/setuptools-pyN.N.egg'),
      join(base, 'eggs/ZConfig-pyN.N.egg'),
      '/zope3recipes',
      ]
    <BLANKLINE>
    import zc.zope3recipes.ctl
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zc.zope3recipes.ctl.main([
            join(base, 'parts/myapp/debugzope'),
            join(base, 'parts/instance/zope.conf'),
            '-C', join(base, 'parts/instance/zdaemon.conf'),
            ]+sys.argv[1:]
            ))


zope.conf recipe
================

The zope.conf recipe handles filling in the implied bits of a zope.conf
file that the instance recipe performs, without creating the rest of an
instance.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1
    ... parts = some.conf
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:application
    ... site.zcml = <include package="demo1" />
    ... eggs = demo1
    ...
    ... [some.conf]
    ... recipe = zc.zope3recipes:zopeconf
    ... application = myapp
    ... text =
    ...     <zodb>
    ...       <zeoclient>
    ...         server 127.0.0.1:8001
    ...       </zeoclient>
    ...     </zodb>
    ...
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Uninstalling instance.
    Uninstalling myapp.
    Uninstalling database.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.
    Installing some.conf.

    >>> cat('parts', 'some.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <zeoclient>
        server 127.0.0.1:8001
      </zeoclient>
    </zodb>
    <BLANKLINE>
    <server>
      address 8080
      type HTTP
    </server>
    <BLANKLINE>
    <accesslog>
      <logfile>
        path /sample-buildout/parts/some-access.log
      </logfile>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>

We can specify the location of the access log directly in the part:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1
    ... parts = some.conf
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:application
    ... site.zcml = <include package="demo1" />
    ... eggs = demo1
    ...
    ... [some.conf]
    ... recipe = zc.zope3recipes:zopeconf
    ... application = myapp
    ... access-log = ${buildout:directory}/access.log
    ... text =
    ...     <zodb>
    ...       <zeoclient>
    ...         server 127.0.0.1:8001
    ...       </zeoclient>
    ...     </zodb>
    ...
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/tmp/tmp2eRRw1buildoutSetUp/_TEST_/sample-buildout/demo1'
    Uninstalling some.conf.
    Updating myapp.
    Installing some.conf.

    >>> cat('parts', 'some.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <zeoclient>
        server 127.0.0.1:8001
      </zeoclient>
    </zodb>
    <BLANKLINE>
    <server>
      address 8080
      type HTTP
    </server>
    <BLANKLINE>
    <accesslog>
      <logfile>
        path /sample-buildout/access.log
      </logfile>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>

The address of the server can be set using the "address" setting:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1
    ... parts = some.conf
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:application
    ... site.zcml = <include package="demo1" />
    ... eggs = demo1
    ...
    ... [some.conf]
    ... recipe = zc.zope3recipes:zopeconf
    ... address = 4242
    ... application = myapp
    ... text =
    ...     <zodb>
    ...       <zeoclient>
    ...         server 127.0.0.1:8001
    ...       </zeoclient>
    ...     </zodb>
    ...
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/tmp/tmp2eRRw1buildoutSetUp/_TEST_/sample-buildout/demo1'
    Uninstalling some.conf.
    Updating myapp.
    Installing some.conf.

    >>> cat('parts', 'some.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <zeoclient>
        server 127.0.0.1:8001
      </zeoclient>
    </zodb>
    <BLANKLINE>
    <server>
      address 4242
      type HTTP
    </server>
    <BLANKLINE>
    <accesslog>
      <logfile>
        path /sample-buildout/parts/some-access.log
      </logfile>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>

The location of the file is made available as the "location" setting.
This parallels the zc.recipe.deployment:configuration recipe, making
this a possible replacement for that recipe where appropriate.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1
    ... parts = another.conf
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:application
    ... site.zcml = <include package="demo1" />
    ... eggs = demo1
    ...
    ... [some.conf]
    ... recipe = zc.zope3recipes:zopeconf
    ... application = myapp
    ... text =
    ...     <zodb>
    ...       <zeoclient>
    ...         server 127.0.0.1:8001
    ...       </zeoclient>
    ...     </zodb>
    ...
    ... [another.conf]
    ... recipe = zc.zope3recipes:zopeconf
    ... application = myapp
    ... text =
    ...     ${some.conf:text}
    ...     <product-config reference>
    ...       config ${some.conf:location}
    ...     </product-config>
    ...
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/tmp/tmp2eRRw1buildoutSetUp/_TEST_/sample-buildout/demo1'
    Uninstalling some.conf.
    Updating myapp.
    Installing some.conf.
    Installing another.conf.

    >>> cat('parts', 'another.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    ...
    <product-config reference>
      config /sample-buildout/parts/some.conf
    </product-config>
    ...


Offline recipe
==============

The offline recipe creates a script that in some ways is a syntactic sugar for
"bin/instance debug" or "bin/instance run <script>". With the offline script,
all you do is "bin/offline" or "bin/offline </script>". This script doesn't
create additional folders like the ``Instance`` recipe; it expects two options:
"application" and "zope.conf" that must be sections for a Zope3 application and
a configuration file (that supports a "location" option) to exist.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance offline
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... name = server
    ... application = myapp
    ... zope.conf =
    ...     <zodb>
    ...       <zeoclient>
    ...         server 127.0.0.1:8001
    ...         server 127.0.0.1:8002
    ...       </zeoclient>
    ...     </zodb>
    ... address = 8081
    ... zdaemon.conf =
    ...     <runner>
    ...       daemon off
    ...       socket-name /sample-buildout/parts/instance/sock
    ...       transcript /dev/null
    ...     </runner>
    ...     <eventlog>
    ...     </eventlog>
    ...
    ... [offline.conf]
    ... location = %(zope3)s
    ...
    ... [offline]
    ... recipe = zc.zope3recipes:offline
    ... application = myapp
    ... zope.conf = offline.conf
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling another.conf.
    Uninstalling some.conf.
    Uninstalling myapp.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.
    Installing instance.
    Generated script '/sample-buildout/bin/server'.
    Installing offline.

    >>> cat('bin', 'offline')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import os
    import sys
    import logging
    <BLANKLINE>
    argv = list(sys.argv)
    env = {}
    restart = False
    <BLANKLINE>
    if None:
        import pwd
        if pwd.getpwnam(None).pw_uid != os.geteuid():
            restart = True
            argv[:0] = ["sudo", "-u", None]
            # print "switching to user", None
        del pwd
    <BLANKLINE>
    for k in env:
        if os.environ.get(k) != env[k]:
            os.environ[k] = env[k]
            restart = True
        del k
    <BLANKLINE>
    if restart:
        # print "restarting"
        os.execvpe(argv[0], argv, dict(os.environ))
    <BLANKLINE>
    del argv
    del env
    del restart
    <BLANKLINE>
    sys.argv[1:1] = [
        "-C",
        '/zope3',
    <BLANKLINE>
        ]
    <BLANKLINE>
    debugzope = '/sample-buildout/parts/myapp/debugzope'
    globals()["__file__"] = debugzope
    <BLANKLINE>
    zeo_logger = logging.getLogger('ZEO.zrpc')
    zeo_logger.addHandler(logging.StreamHandler())
    <BLANKLINE>
    <BLANKLINE>
    # print "starting debugzope..."
    execfile(debugzope)


initialization option
---------------------

The recipe also accepts an "initialization" option:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance offline
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... name = server
    ... application = myapp
    ... zope.conf =
    ...     <zodb>
    ...       <zeoclient>
    ...         server 127.0.0.1:8001
    ...         server 127.0.0.1:8002
    ...       </zeoclient>
    ...     </zodb>
    ... address = 8081
    ... zdaemon.conf =
    ...     <runner>
    ...       daemon off
    ...       socket-name /sample-buildout/parts/instance/sock
    ...       transcript /dev/null
    ...     </runner>
    ...     <eventlog>
    ...     </eventlog>
    ...
    ... [offline.conf]
    ... location = %(zope3)s
    ...
    ... [offline]
    ... recipe = zc.zope3recipes:offline
    ... initialization =
    ...     os.environ['ZC_DEBUG_LOGGING'] = 'on'
    ... application = myapp
    ... zope.conf = offline.conf
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling offline.
    Updating myapp.
    Updating instance.
    Installing offline.

    >>> cat('bin', 'offline')
    <BLANKLINE>
    import os
    import sys
    import logging
    <BLANKLINE>
    argv = list(sys.argv)
    env = {}
    restart = False
    <BLANKLINE>
    if None:
        import pwd
        if pwd.getpwnam(None).pw_uid != os.geteuid():
            restart = True
            argv[:0] = ["sudo", "-u", None]
            # print "switching to user", None
        del pwd
    <BLANKLINE>
    for k in env:
        if os.environ.get(k) != env[k]:
            os.environ[k] = env[k]
            restart = True
        del k
    <BLANKLINE>
    if restart:
        # print "restarting"
        os.execvpe(argv[0], argv, dict(os.environ))
    <BLANKLINE>
    del argv
    del env
    del restart
    <BLANKLINE>
    sys.argv[1:1] = [
        "-C",
        '/zope3',
    <BLANKLINE>
        ]
    <BLANKLINE>
    debugzope = '/sample-buildout/parts/myapp/debugzope'
    globals()["__file__"] = debugzope
    <BLANKLINE>
    zeo_logger = logging.getLogger('ZEO.zrpc')
    zeo_logger.addHandler(logging.StreamHandler())
    <BLANKLINE>
    os.environ['ZC_DEBUG_LOGGING'] = 'on'
    <BLANKLINE>
    # print "starting debugzope..."
    execfile(debugzope)


script option
-------------

as well as a "script" option.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance run-foo
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... name = server
    ... application = myapp
    ... zope.conf =
    ...     <zodb>
    ...       <zeoclient>
    ...         server 127.0.0.1:8001
    ...         server 127.0.0.1:8002
    ...       </zeoclient>
    ...     </zodb>
    ... address = 8081
    ... zdaemon.conf =
    ...     <runner>
    ...       daemon off
    ...       socket-name /sample-buildout/parts/instance/sock
    ...       transcript /dev/null
    ...     </runner>
    ...     <eventlog>
    ...     </eventlog>
    ...
    ... [offline.conf]
    ... location = %(zope3)s
    ...
    ... [run-foo]
    ... recipe = zc.zope3recipes:offline
    ... initialization =
    ...     os.environ['ZC_DEBUG_LOGGING'] = 'on'
    ... application = myapp
    ... zope.conf = offline.conf
    ... script = %(zope3)s/foo.py
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ... ''' % globals())

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling offline.
    Updating myapp.
    Updating instance.
    Installing run-foo.

    >>> cat('bin', 'run-foo')
    <BLANKLINE>
    import os
    import sys
    import logging
    <BLANKLINE>
    argv = list(sys.argv)
    env = {}
    restart = False
    <BLANKLINE>
    if None:
        import pwd
        if pwd.getpwnam(None).pw_uid != os.geteuid():
            restart = True
            argv[:0] = ["sudo", "-u", None]
            # print "switching to user", None
        del pwd
    <BLANKLINE>
    for k in env:
        if os.environ.get(k) != env[k]:
            os.environ[k] = env[k]
            restart = True
        del k
    <BLANKLINE>
    if restart:
        # print "restarting"
        os.execvpe(argv[0], argv, dict(os.environ))
    <BLANKLINE>
    del argv
    del env
    del restart
    <BLANKLINE>
    sys.argv[1:1] = [
        "-C",
        '/zope3',
        '/zope3/foo.py'
    <BLANKLINE>
        ]
    <BLANKLINE>
    debugzope = '/sample-buildout/parts/myapp/debugzope'
    globals()["__file__"] = debugzope
    <BLANKLINE>
    zeo_logger = logging.getLogger('ZEO.zrpc')
    zeo_logger.addHandler(logging.StreamHandler())
    <BLANKLINE>
    os.environ['ZC_DEBUG_LOGGING'] = 'on'
    <BLANKLINE>
    # print "starting debugzope..."
    execfile(debugzope)

Paste-deployment support
========================

You can use paste-deployment to control WSGI servers and middleware.
You indicate this by specifying ``paste`` in the ``servers`` option:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:application
    ... servers = paste
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf =
    ...    threads 1
    ...    ${database:zconfig}
    ...
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ... ''' % globals())

When we run the buildout, we'll get a paste-based runzope script and
paste-based instance start scripts.

.. test

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling run-foo.
    Uninstalling instance.
    Uninstalling myapp.
    Installing database.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.
    Installing instance.
    Generated script '/sample-buildout/bin/instance'.


    >>> cat('parts', 'myapp', 'runzope')
    #!/usr/local/python/2.6/bin/python2.6
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
        '/sample-buildout/demo2',
        '/sample-buildout/eggs/PasteScript-1.7.4.2-py2.6.egg',
        '/sample-buildout/eggs/setuptools-0.6c12dev_r88846-py2.6.egg',
        '/sample-buildout/eggs/PasteDeploy-1.5.0-py2.6.egg',
        '/sample-buildout/eggs/Paste-1.7.5.1-py2.6.egg',
        '/sample-buildout/demo1',
        ]
    <BLANKLINE>
    <BLANKLINE>
    import paste.script.command
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(paste.script.command.run(['serve']+sys.argv[1:]))


    >>> cat('parts', 'instance', 'zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    </zodb>
    <BLANKLINE>
    <logger accesslog>
      level info
      name accesslog
      propagate false
    <BLANKLINE>
      <logfile>
        format %(message)s
        path /sample-buildout/parts/instance/access.log
      </logfile>
    </logger>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>

    >>> cat('parts', 'instance', 'zdaemon.conf')
    <runner>
      daemon on
      directory /sample-buildout/parts/instance
      program /sample-buildout/parts/myapp/runzope /sample-buildout/parts/instance/paste.ini
      socket-name /sample-buildout/parts/instance/zdaemon.sock
      transcript /sample-buildout/parts/instance/z3.log
    </runner>
    <BLANKLINE>
    <eventlog>
      <logfile>
        path /sample-buildout/parts/instance/z3.log
      </logfile>
    </eventlog>

We also get a paste.ini file in the instance directory, which defines
the application and server and is used when running paste::

    >>> cat('parts', 'instance', 'paste.ini')
    [app:main]
    use = egg:zope.app.wsgi
    config_file = /sample-buildout/parts/instance/zope.conf
    filter-with = translogger
    <BLANKLINE>
    [filter:translogger]
    use = egg:Paste#translogger
    setup_console_handler = False
    logger_name = accesslog
    <BLANKLINE>
    [server:main]
    use = egg:zope.server
    host = 
    port = 8080
    threads = 1

Note that the threads setting made in zope.conf was moved to paste.ini

Note too that past:translogger was used to provide an access log.

If you don't want to use zope.server, or if you want to control the
server configuration yourself, you can provide a paste.init option::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:application
    ... servers = paste
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf =
    ...    threads 1
    ...    ${database:zconfig}
    ... paste.ini = test and not working :)
    ...
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ... ''' % globals())

.. test

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Updating database.
    Updating myapp.
    Installing instance.
    Generated script '/sample-buildout/bin/instance'.

In this example, we gave useless text in the paste.ini option and we
got a nonsense paste.ini file::

    >>> cat('parts', 'instance', 'paste.ini')
    [app:main]
    use = egg:zope.app.wsgi
    config_file = /sample-buildout/parts/instance/zope.conf
    <BLANKLINE>
    test and not working :)

This illustrates that the recipe doesn't care what you provide.  It
uses it with the application definition instead of supplying
zope.server and paste.translogger definition.
