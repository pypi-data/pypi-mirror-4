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
"""Collected Zope 3 recipes
"""

import cStringIO
import logging
import os
import pkg_resources
import pprint
import re
import shutil
import sys
import zc.buildout
import ZConfig.schemaless
import zc.recipe.egg

this_loc = pkg_resources.working_set.find(
    pkg_resources.Requirement.parse('zc.zope3recipes')).location

server_types = {
    # name     (module,                  http-name)
    'twisted': ('zope.app.twisted.main', 'HTTP'),
    'zserver': ('zope.app.server.main',  'WSGI-HTTP'),
    'paste': ('zope.app.server.main',  ''),
    }

WIN = False
if sys.platform[:3].lower() == "win":
    WIN = True


def get_executable(section):
    # Support older multi-python buildouts, and newer mono-python buildouts.
    return section.get("executable") or sys.executable


class Application(object):

    def __init__(self, buildout, name, options):
        self.options = options
        self.name = name

        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            name,
            )

        options['servers'] = options.get('servers', 'twisted')
        if options['servers'] not in server_types:
            raise ValueError(
                'servers setting must be one of %s' %
                repr(sorted(server_types))[1:-1]
                )
        if options['servers'] == 'paste':
            options['eggs'] += '\n  PasteScript\n'

        options['scripts'] = ''
        self.egg = zc.recipe.egg.Egg(buildout, name, options)

    def install(self):
        options = self.options

        dest = options['location']
        if not os.path.exists(dest):
            os.mkdir(dest)
            created = True
        else:
            created = False

        try:
            open(os.path.join(dest, 'site.zcml'), 'w').write(
                site_zcml_template % self.options['site.zcml']
                )

            self.egg.install()
            requirements, ws = self.egg.working_set()

            server_module = server_types[options['servers']][0]

            # install subprograms and ctl scripts
            if options['servers'] == 'paste':
                reqs = ['PasteScript']
                scripts = dict(paster='runzope')
                arguments = "['serve']+sys.argv[1:]"
            else:
                reqs = [('runzope', server_module, 'main')]
                scripts = None
                arguments = ''

            extra_paths = options.get('extra-paths', '')
            initialization = options.get('initialization') or ''

            zc.buildout.easy_install.scripts(
                reqs,
                ws, get_executable(options), dest,
                scripts=scripts,
                extra_paths=extra_paths.split(),
                arguments=arguments,
                initialization=initialization,
                relative_paths=self.egg._relative_paths,
                )

            options['extra-paths'] = extra_paths + '\n' + this_loc

            initialization = options.get('debug-initialization')
            if initialization is None:
                initialization = options.get('initialization')
            if initialization:
                initialization += '\n'
            else:
                initialization = ''
            initialization += 'import %s\n' % server_module
            arguments = 'main_module=%s' % server_module
            zc.buildout.easy_install.scripts(
                [('debugzope', 'zc.zope3recipes.debugzope', 'debug')],
                ws, get_executable(options), dest,
                extra_paths = options['extra-paths'].split(),
                initialization = initialization,
                arguments = arguments,
                relative_paths=self.egg._relative_paths,
                )

            ftesting_zcml = options.get('ftesting.zcml')
            if ftesting_zcml:
                open(os.path.join(dest, 'ftesting.zcml'), 'w'
                     ).write(site_zcml_template % ftesting_zcml)
                open(os.path.join(dest, 'ftesting-base.zcml'), 'w'
                     ).write(ftesting_base)

            return dest

        except:
            if created:
                shutil.rmtree(dest)
            raise

        return dest

    def update(self):
        self.install()

class App(Application):

    def __init__(self, buildout, name, options):
        super(App, self).__init__(buildout, name, options)

        location = buildout[options.get('zope3', 'zope3')]['location']
        if location:
            options['zope3-location'] = os.path.join(
                buildout['buildout']['directory'],
                location,
                )

    def install(self):
        options = self.options
        z3path = options.get('zope3-location')
        logger = logging.getLogger(self.name)
        if z3path is not None:
            if not os.path.exists(z3path):
                logger.error("The directory, %r, doesn't exist." % z3path)
                raise zc.buildout.UserError("No directory:", z3path)

            path = os.path.join(z3path, 'lib', 'python')
            if not os.path.exists(path):
                path = os.path.join(z3path, 'src')
                if not os.path.exists(path):
                    logger.error(
                        "The directory, %r, isn't a valid checkout or release."
                        % z3path)
                    raise zc.buildout.UserError(
                        "Invalid Zope 3 installation:", z3path)

            extra = options.get('extra-paths')
            if extra:
                extra += '\n' + path
            else:
                extra = path
            options['extra-paths'] = extra

        return super(App, self).install()

site_zcml_template = """\
<configure xmlns='http://namespaces.zope.org/zope'
           xmlns:meta="http://namespaces.zope.org/meta"
           >
%s
</configure>
"""

class Instance:

    deployment = None

    def __init__(self, buildout, name, options):
        self.name, self.options = options.get('name', name), options

        for section in options.get('extends', '').split():
            options.update(
                [(k, v) for (k, v) in buildout[section].items()
                 if k not in options
                 ])

        options['application-location'] = buildout[options['application']
                                                   ]['location']

        options['scripts'] = ''
        options['servers'] = buildout[options['application']]['servers']
        options['eggs'] = options.get('eggs', 'zdaemon\nsetuptools')
        self.egg = zc.recipe.egg.Egg(buildout, name, options)

        deployment = options.get('deployment')
        if deployment:
            # Note we use get below to work with old zc.recipe.deployment eggs.
            self.deployment = buildout[deployment].get('name', deployment)

            options['bin-directory'] = buildout[deployment]['rc-directory']
            options['run-directory'] = buildout[deployment]['run-directory']
            options['log-directory'] = buildout[deployment]['log-directory']
            options['etc-directory'] = buildout[deployment]['etc-directory']
            options['logrotate-directory'] = buildout[deployment][
                'logrotate-directory']
            options['user'] = buildout[deployment]['user']
        else:
            options['bin-directory'] = buildout['buildout']['bin-directory']
            options['run-directory'] = os.path.join(
                buildout['buildout']['parts-directory'],
                name,
                )

    def install(self):
        options = self.options
        run_directory = options['run-directory']
        deployment = self.deployment
        if deployment:
            zope_conf_path = os.path.join(options['etc-directory'],
                                          self.name+'-zope.conf')
            zdaemon_conf_path = os.path.join(options['etc-directory'],
                                             self.name+'-zdaemon.conf')
            paste_ini_path = os.path.join(options['etc-directory'],
                                             self.name+'-paste.ini')
            event_log_path = os.path.join(options['log-directory'],
                                          self.name+'-z3.log')
            access_log_path = os.path.join(options['log-directory'],
                                           self.name+'-access.log')
            socket_path = os.path.join(run_directory,
                                       self.name+'-zdaemon.sock')
            rc = deployment + '-' + self.name
            logrotate_path = os.path.join(options['logrotate-directory'],
                                          rc)
            creating = [zope_conf_path, zdaemon_conf_path,
                        os.path.join(options['bin-directory'], rc),
                        ]
            logrotate_conf = options.get("logrotate.conf")
            if isinstance(logrotate_conf, basestring):
                if logrotate_conf.strip():
                    creating.append(logrotate_path)
                else:
                    logrotate_conf = None
            else:
                logrotate_conf = logrotate_template % dict(
                    logfile=event_log_path,
                    rc=os.path.join(options['bin-directory'], rc),
                    conf=zdaemon_conf_path,
                )
                creating.append(logrotate_path)
        else:
            zope_conf_path = os.path.join(run_directory, 'zope.conf')
            zdaemon_conf_path = os.path.join(run_directory, 'zdaemon.conf')
            paste_ini_path = os.path.join(run_directory, 'paste.ini')
            event_log_path = os.path.join(run_directory, 'z3.log')
            access_log_path = os.path.join(run_directory, 'access.log')
            socket_path = os.path.join(run_directory, 'zdaemon.sock')
            rc = self.name
            creating = [run_directory,
                        os.path.join(options['bin-directory'], rc),
                        ]
            if not os.path.exists(run_directory):
                os.mkdir(run_directory)

        try:
            app_loc = options['application-location']

            zope_conf = options.get('zope.conf', '')+'\n'
            zope_conf = ZConfig.schemaless.loadConfigFile(
                cStringIO.StringIO(zope_conf))

            if 'site-definition' not in zope_conf:
                zope_conf['site-definition'] = [
                    os.path.join(app_loc, 'site.zcml')
                    ]

            threads = None
            server_type = server_types[options['servers']][1]
            if server_type:
                for address in options.get('address', '').split():
                    zope_conf.sections.append(
                        ZConfig.schemaless.Section(
                            'server',
                            data=dict(type=[server_type], address=[address]))
                        )
                if not [s for s in zope_conf.sections
                        if ('server' in s.type)]:
                    zope_conf.sections.append(
                        ZConfig.schemaless.Section(
                            'server',
                            data=dict(type=[server_type], address=['8080']))
                        )
                program_args = '-C '+zope_conf_path
            else: # paste
                paste_ini = options.get('paste.ini', '')
                if not paste_ini:
                    address = options.get('address', '8080').split()
                    if not len(address) == 1:
                        raise zc.buildout.UserError(
                            "If you don't specify a paste.ini option, "
                            "you must specify exactly one address.")
                    [address] = address
                    if ':' in address:
                        host, port = address.rsplit(':', 1)
                        port = int(port)
                    elif re.match('\d+$', address):
                        host = ''
                        port = int(address)
                    else:
                        host = address
                        port = 8080

                    threads = zope_conf.pop('threads', None)
                    threads = threads and threads[0] or 4

                    paste_ini = (
                        "filter-with = translogger\n"
                        "\n"
                        "[filter:translogger]\n"
                        "use = egg:Paste#translogger\n"
                        "setup_console_handler = False\n"
                        "logger_name = accesslog\n"
                        "\n"
                        ""
                        "[server:main]\n"
                        "use = egg:zope.server\n"
                        "host = %s\n"
                        "port = %s\n"
                        "threads = %s\n"
                        % (host, port, threads)
                        )

                paste_ini = (
                    "[app:main]\n"
                    "use = egg:zope.app.wsgi\n"
                    "config_file = %s\n"
                    % zope_conf_path) + paste_ini

                creating.append(paste_ini_path)
                f = open(paste_ini_path, 'w')
                f.write(paste_ini)
                f.close()

                program_args = paste_ini_path


            if not [s for s in zope_conf.sections if s.type == 'zodb']:
                raise zc.buildout.UserError(
                    'No database sections have been defined.')

            if not [s for s in zope_conf.sections if s.type == 'accesslog']:
                zope_conf.sections.append(access_log(access_log_path))

            if not server_type: # paste
                for s in zope_conf.sections:
                    if s.type != 'accesslog':
                        continue
                    s.type = 'logger'
                    s.name = 'accesslog'
                    s['name'] = [s.name]
                    s['level'] = ['info']
                    s['propagate'] = ['false']
                    for formatter in s.sections:
                        formatter['format'] = ['%(message)s']

            if not [s for s in zope_conf.sections if s.type == 'eventlog']:
                zope_conf.sections.append(event_log('STDOUT'))


            zdaemon_conf = options.get('zdaemon.conf', '')+'\n'
            zdaemon_conf = ZConfig.schemaless.loadConfigFile(
                cStringIO.StringIO(zdaemon_conf))

            defaults = {
                'program': "%s %s" % (os.path.join(app_loc, 'runzope'),
                                      program_args),
                'daemon': 'on',
                'transcript': event_log_path,
                'socket-name': socket_path,
                'directory' : run_directory,
                }
            if deployment:
                defaults['user'] = options['user']
            runner = [s for s in zdaemon_conf.sections
                      if s.type == 'runner']
            if runner:
                runner = runner[0]
            else:
                runner = ZConfig.schemaless.Section('runner')
                zdaemon_conf.sections.insert(0, runner)
            for name, value in defaults.items():
                if name not in runner:
                    runner[name] = [value]

            if not [s for s in zdaemon_conf.sections
                    if s.type == 'eventlog']:
                # No database, specify a default one
                zdaemon_conf.sections.append(event_log2(event_log_path))

            zdaemon_conf = str(zdaemon_conf)

            self.egg.install()
            requirements, ws = self.egg.working_set()

            open(zope_conf_path, 'w').write(str(zope_conf))
            open(zdaemon_conf_path, 'w').write(str(zdaemon_conf))

            if deployment and logrotate_conf:
                open(logrotate_path, 'w').write(logrotate_conf)

            # XXX: We are using a private zc.buildout.easy_install
            # function below.  It would be better if self.egg had a
            # method to install scripts.  All recipe options and
            # relative path information would be available to the egg
            # instance and the recipe would have no need to call
            # zc.buildout.easy_install.scripts directly.  Since that
            # requires changes to zc.recipe.egg/zc.buildout we are
            # fixing our immediate need to generate correct relative
            # paths by using the private API.
            # This should be done "right" in the future.
            if self.egg._relative_paths:
                arg_paths = (
                    os.path.join(app_loc, 'debugzope'),
                    zope_conf_path,
                    zdaemon_conf_path,
                    )
                spath, x = zc.buildout.easy_install._relative_path_and_setup(
                    os.path.join(options['bin-directory'], 'ctl'),
                    arg_paths,
                    self.egg._relative_paths,
                    )
                rpath = spath.split(',\n  ')
                debugzope_loc, zope_conf_path, zdaemon_conf_path = rpath
                arguments = ('['
                             '\n        %s,'
                             '\n        %s,'
                             '\n        %r, %s,'
                             '\n        ]+sys.argv[1:]'
                             '\n        '
                             % (debugzope_loc,
                                zope_conf_path,
                                '-C', zdaemon_conf_path,
                                )
                             )
            else:
                arguments = ('['
                             '\n        %r,'
                             '\n        %r,'
                             '\n        %r, %r,'
                             '\n        ]+sys.argv[1:]'
                             '\n        '
                             % (os.path.join(app_loc, 'debugzope'),
                                zope_conf_path,
                                '-C', zdaemon_conf_path,
                                )
                             )

            if WIN:
                zc.buildout.easy_install.scripts(
                    [(rc, 'zc.zope3recipes.winctl', 'main')],
                    ws, get_executable(options), options['bin-directory'],
                    extra_paths=[this_loc],
                    arguments=arguments,
                    relative_paths=self.egg._relative_paths,
                    )
            else:
                zc.buildout.easy_install.scripts(
                    [(rc, 'zc.zope3recipes.ctl', 'main')],
                    ws, get_executable(options), options['bin-directory'],
                    extra_paths=[this_loc],
                    arguments=arguments,
                    relative_paths=self.egg._relative_paths,
                    )

            return creating

        except:
            for f in creating:
                if os.path.isdir(f):
                    shutil.rmtree(f)
                elif os.path.exists(f):
                    os.remove(f)
            raise


    update = install

def access_log(path):
    return ZConfig.schemaless.Section(
        'accesslog', '',
        sections=[ZConfig.schemaless.Section('logfile', '', dict(path=[path]))]
        )

def event_log(path, *data):
    return ZConfig.schemaless.Section(
        'eventlog', '', None,
        [ZConfig.schemaless.Section(
             'logfile',
             '',
             dict(path=[path], formatter=['zope.exceptions.log.Formatter'])),
         ])

def event_log2(path, *data):
    return ZConfig.schemaless.Section(
        'eventlog', '', None,
        [ZConfig.schemaless.Section(
            'logfile', '', dict(path=[path]))])


logrotate_template = """%(logfile)s {
  rotate 5
  weekly
  postrotate
    %(rc)s reopen_transcript
  endscript
}
"""


ftesting_base = """
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
"""


class SupportingBase(object):

    def __init__(self, buildout, name, options):
        self.options = options
        self.name = name
        deployment = options.get("deployment")
        if deployment:
            deployment = buildout[deployment]
        self.deployment = deployment
        self.app = buildout[options["application"]]
        options["application-location"] = self.app["location"]

    def update(self):
        self.install()


class ZopeConf(SupportingBase):

    def __init__(self, buildout, name, options):
        super(ZopeConf, self).__init__(buildout, name, options)
        if self.deployment:
            options['run-directory'] = self.deployment['run-directory']
            zope_conf_path = os.path.join(
                self.deployment['etc-directory'], self.name)
        else:
            directory = os.path.join(
                buildout['buildout']['parts-directory'])
            options['run-directory'] = directory
            zope_conf_path = os.path.join(directory, self.name)
        options["location"] = zope_conf_path

    def install(self):
        options = self.options
        run_directory = options['run-directory']

        zope_conf = options.get('text', '')+'\n'
        zope_conf = ZConfig.schemaless.loadConfigFile(
            cStringIO.StringIO(zope_conf))

        if "access-log" in options:
            access_log_name = options["access-log"]
            access_log_specified = True
        else:
            basename = os.path.splitext(self.name)[0]
            access_log_name = basename+'-access.log'
            access_log_specified = False

        # access_log_path depends on whether a given name is an absolute
        # path; this (and the windows case) are handled specially so the
        # file can be dumped to /dev/null for offline scripts.
        if (os.path.isabs(access_log_name)
            or (WIN and access_log_name.upper() == "NUL")):
            access_log_path = access_log_name
        elif self.deployment:
            access_log_path = os.path.join(
                self.deployment['log-directory'], access_log_name)
        else:
            access_log_path = os.path.join(run_directory, access_log_name)

        zope_conf_path = options["location"]

        if 'site-definition' not in zope_conf:
            app_loc = options["application-location"]
            zope_conf['site-definition'] = [
                os.path.join(app_loc, 'site.zcml')
                ]

        server_type = server_types[self.app['servers']][1]
        for address in options.get('address', '').split():
            zope_conf.sections.append(
                ZConfig.schemaless.Section(
                    'server',
                    data=dict(type=[server_type], address=[address]))
                )
        if not [s for s in zope_conf.sections
                if ('server' in s.type)]:
            zope_conf.sections.append(
                ZConfig.schemaless.Section(
                    'server',
                    data=dict(type=[server_type], address=['8080']))
                )

        if not [s for s in zope_conf.sections if s.type == 'zodb']:
            raise zc.buildout.UserError(
                'No database sections have been defined.')

        if not [s for s in zope_conf.sections if s.type == 'accesslog']:
            zope_conf.sections.append(access_log(access_log_path))
        elif access_log_specified:
            # Can't include one and specify the path.
            raise zc.buildout.UserError(
                "access log can only be specified once")

        if not [s for s in zope_conf.sections if s.type == 'eventlog']:
            zope_conf.sections.append(event_log('STDOUT'))

        open(zope_conf_path, 'w').write(str(zope_conf))
        return [zope_conf_path]


class Offline(SupportingBase):

    def __init__(self, buildout, name, options):
        super(Offline, self).__init__(buildout, name, options)
        if "directory" not in options:
            if self.deployment is None:
                directory = buildout["buildout"]["bin-directory"]
            else:
                directory = self.deployment["etc-directory"]
            options["directory"] = directory
        if self.deployment is not None and "user" not in options:
            options["user"] = self.deployment["user"]
        options["dest"] = os.path.join(options["directory"], name)
        env = options.get("environment")
        if env:
            self.environment = dict(buildout[env])
        else:
            self.environment = {}
        options["executable"] = get_executable(self.app)
        zope_conf = buildout[options["zope.conf"]]
        options["zope.conf-location"] =  zope_conf["location"]
        script = options.get("script")
        if script:
            script = os.path.join(buildout["buildout"]["directory"], script)
            options["script"] = script

    def install(self):
        options = self.options

        debugzope = os.path.join(
            options["application-location"], "debugzope")
        config = options["zope.conf-location"]
        script = options.get("script") or ""
        if script:
            script = repr(script)

        initialization = options.get("initialization", "").strip()

        script_content = template % dict(
            config=config,
            debugzope=debugzope,
            executable=options["executable"],
            environment=pprint.pformat(self.environment),
            initialization=initialization,
            script=script,
            user=options.get("user"),
            )

        dest = options["dest"]
        f = open(dest, "w")
        f.write(script_content)
        f.close()
        os.chmod(dest, 0775)
        return [dest]

template = '''\
#!%(executable)s

import os
import sys
import logging

argv = list(sys.argv)
env = %(environment)s
restart = False

if %(user)r:
    import pwd
    if pwd.getpwnam(%(user)r).pw_uid != os.geteuid():
        restart = True
        argv[:0] = ["sudo", "-u", %(user)r]
        # print "switching to user", %(user)r
    del pwd

for k in env:
    if os.environ.get(k) != env[k]:
        os.environ[k] = env[k]
        restart = True
    del k

if restart:
    # print "restarting"
    os.execvpe(argv[0], argv, dict(os.environ))

del argv
del env
del restart

sys.argv[1:1] = [
    "-C",
    %(config)r,
    %(script)s
    ]

debugzope = %(debugzope)r
globals()["__file__"] = debugzope

zeo_logger = logging.getLogger('ZEO.zrpc')
zeo_logger.addHandler(logging.StreamHandler())

%(initialization)s

# print "starting debugzope..."
execfile(debugzope)
'''
