##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import re, sys, os

import zc.buildout.testing

import unittest
from zope.testing import doctest, renormalizing

def ls_optional(dir, ignore=(), *subs):
    if subs:
        dir = os.path.join(dir, *subs)
    names = os.listdir(dir)
    names.sort()
    for name in names:
        if name in ignore:
            continue
        if os.path.isdir(os.path.join(dir, name)):
            print 'd ',
        elif os.path.islink(os.path.join(dir, name)):
            print 'l ',
        else:
            print '- ',
        print name

def test_ctl():
    """
The ctl script is an extended version of zdaemon that provides an
extra command, run.  Let's create a buildout that installs it as an
ordinary script:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = ctl
    ...
    ... [ctl]
    ... recipe = zc.recipe.egg
    ... eggs = zc.zope3recipes
    ...        zdaemon
    ... entry-points = ctl=zc.zope3recipes.ctl:main
    ... scripts = ctl
    ... ''')

    >>> print system(join('bin', 'buildout')),
    Installing ctl...
    Generated script '/sample-buildout/bin/ctl'.

We'll create a configuration file:

    >>> write('conf',
    ... '''
    ... <runner>
    ...   program echo hi
    ... </runner>
    ... ''')

The configuration doesn't matter much. :)

Unlike a normal zdaemon script, we have to pass two extra arguments, a
script to run the zope debugger with, and the name of a zope
configuration file. For demonstration purposes, we'll just use echo.

    >>> print system(join('bin', 'ctl')+' echo zope.conf -Cconf fg there'),
    echo hi there
    hi there

Notice:

  - The first 2 arguments were ignored.

  - It got the program, 'echo hi', from the configuration file.

  - We ran the program in the foreground, passing the extra argument, there.

Now, if we use the run command, it will run the script we passed as
the first argument:

    >>> print system(join('bin', 'ctl')+' echo zope.conf -Cconf run there'),
    -C zope.conf there

debug is another name for run:

    >>> print system(join('bin', 'ctl')+' echo zope.conf -Cconf debug there'),
    -C zope.conf there


"""

def test_sane_errors_from_recipe():
    """
There was a bug in the recipe error handling that caused errors to be hidden

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = instance
    ...
    ... [myapp]
    ... location = foo
    ... ;; Note that 'servers' has a default value when the
    ... ;; application recipe is involved.
    ... servers = twisted
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf =
    ... ''')

    >>> print system(join('bin', 'buildout')),
    Couldn't find index page for 'zc.recipe.egg' (maybe misspelled?)
    Installing instance.
    While:
      Installing instance.
    Error: No database sections have been defined.
    """

def work_with_old_zc_deployment():
    """

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
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ... address = 8081
    ... deployment = myapp-run
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ...
    ... [myapp-run]
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
    Installing database.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.
    Installing instance.
    Generated script '/root/etc/init.d/myapp-run-instance'.

    """

def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('zc.zope3recipes', test)
    zc.buildout.testing.install('zope.exceptions', test)
    zc.buildout.testing.install('zope.interface', test)
    zc.buildout.testing.install('PasteScript', test)
    zc.buildout.testing.install('PasteDeploy', test)
    zc.buildout.testing.install('Paste', test)
    zc.buildout.testing.install('zope.testing', test)
    zc.buildout.testing.install('zc.recipe.egg', test)
    zc.buildout.testing.install('zdaemon', test)
    zc.buildout.testing.install('ZConfig', test)
    zc.buildout.testing.install('zc.recipe.filestorage', test)
    # prevent upgrade during test
    conf_dir = os.path.join(os.path.expanduser('~'), '.buildout')
    conf_file = os.path.join(conf_dir, 'default.cfg')
    if not os.path.exists(conf_dir):
        os.makedirs(conf_dir)
    if not os.path.exists(conf_file):
        open(conf_file, 'w').write("[buildout]\n"
                                   "newest = false")
    else:
        raise RuntimeWarning('Unable to set "newest=false" for tests')


checker = renormalizing.RENormalizing([
    zc.buildout.testing.normalize_path,
    (re.compile(
    "Couldn't find index page for '[a-zA-Z0-9.]+' "
    "\(maybe misspelled\?\)"
    "\n"
    ), ''),
    (re.compile("""['"][^\n"']+zope3recipes[^\n"']*['"],"""),
     "'/zope3recipes',"),
    (re.compile('#![^\n]+\n'), ''),
    (re.compile('-\S+-py\d[.]\d(-\S+)?.egg'),
     '-pyN.N.egg',
    ),
    # Turn "distribute" into "setuptools" so the tests can pass with either:
    (re.compile(r'\bdistribute-pyN\.N\.egg'),
     'setuptools-pyN.N.egg',
    ),
    ])


def test_suite():
    suite = unittest.TestSuite()
    if sys.platform[:3].lower() == "win":
        suite.addTest(doctest.DocFileSuite('WINDOWS.txt',
                 setUp=setUp,
                 tearDown=zc.buildout.testing.buildoutTearDown,
                 checker=checker,
                 optionflags = doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS))
    else:
        suite.addTest(doctest.DocTestSuite(
            setUp=setUp,
            tearDown=zc.buildout.testing.buildoutTearDown,
            checker=checker,
            optionflags = doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS))
        suite.addTest(doctest.DocFileSuite('README.txt',
            setUp=setUp,
            tearDown=zc.buildout.testing.buildoutTearDown,
            checker=checker,
            optionflags = doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
