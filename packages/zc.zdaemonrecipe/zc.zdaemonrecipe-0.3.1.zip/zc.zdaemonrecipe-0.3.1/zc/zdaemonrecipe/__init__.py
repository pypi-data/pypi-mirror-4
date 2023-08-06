##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""zdaemon -- a package to manage a daemon application."""

import ZConfig.schemaless
import cStringIO
import logging
import os
import zc.buildout.easy_install
import zc.recipe.egg


logger = logging.getLogger("zc.zdaemonrecipe")


class Recipe:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        self.buildout = buildout

        deployment = self.deployment = options.get('deployment')
        if deployment:
            # Note we use get below to work with old zc.recipe.deployment eggs.
            self.deployment = buildout[deployment].get('name', deployment)

            options['rc-directory'] = buildout[deployment]['rc-directory']
            options['run-directory'] = buildout[deployment]['run-directory']
            options['log-directory'] = buildout[deployment]['log-directory']
            options['etc-directory'] = buildout[deployment]['etc-directory']
            options['logrotate'] = os.path.join(
                buildout[deployment]['logrotate-directory'],
                self.deployment + '-' + name)
            options['user'] = buildout[deployment]['user']
        else:
            options['rc-directory'] = buildout['buildout']['bin-directory']
            options['run-directory'] = os.path.join(
                buildout['buildout']['parts-directory'],
                self.name,
                )

        options['eggs'] = options.get('eggs', 'zdaemon')
        self.egg = zc.recipe.egg.Egg(buildout, name, options)

        shell_script = options.get('shell-script', '')
        if shell_script in ('false', ''):
            self.shell_script = False
        elif shell_script == 'true':
            self.shell_script = True
            options['zdaemon'] = os.path.join(
                buildout['buildout']['bin-directory'],
                options.get('zdaemon', 'zdaemon'),
            )
        else:
            raise zc.buildout.UserError(
                'The shell-script option value must be "true", "false" or "".')

    def install(self):
        options = self.options

        run_directory = options['run-directory']
        deployment = self.deployment
        if deployment:
            zdaemon_conf_path = os.path.join(options['etc-directory'],
                                             self.name+'-zdaemon.conf')
            event_log_path = os.path.join(
                options['log-directory'],
                self.name+'.log',
                )
            socket_path = os.path.join(run_directory,
                                       self.name+'-zdaemon.sock')

            rc = deployment + '-' + self.name
            rc=os.path.join(options['rc-directory'], rc)

            logrotate = options['logrotate']
            options.created(logrotate)
            open(logrotate, 'w').write(logrotate_template % dict(
                logfile=event_log_path,
                rc=rc,
                conf=zdaemon_conf_path,
                ))

        else:
            zdaemon_conf_path = os.path.join(run_directory, 'zdaemon.conf')
            event_log_path = os.path.join(
                run_directory,
                'transcript.log',
                )
            socket_path = os.path.join(run_directory, 'zdaemon.sock')
            rc = os.path.join(options['rc-directory'], self.name)
            options.created(run_directory)
            if not os.path.exists(run_directory):
                os.mkdir(run_directory)

        zdaemon_conf = options.get('zdaemon.conf', '')+'\n'
        zdaemon_conf = ZConfig.schemaless.loadConfigFile(
            cStringIO.StringIO(zdaemon_conf))

        defaults = {
            'program': "%s" % ' '.join(options['program'].split()),
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
            zdaemon_conf.sections.append(event_log(event_log_path))

        options.created(zdaemon_conf_path)
        open(zdaemon_conf_path, 'w').write(str(zdaemon_conf))

        self.egg.install()
        requirements, ws = self.egg.working_set()

        rc = os.path.abspath(rc)
        options.created(rc)
        if self.shell_script:
            if not os.path.exists(options['zdaemon']):
                logger.warn(no_zdaemon % options['zdaemon'])

            contents = "%(zdaemon)s -C '%(conf)s' $*" % dict(
                zdaemon=options['zdaemon'],
                conf=os.path.join(self.buildout['buildout']['directory'],
                                  zdaemon_conf_path),
                )
            if options.get('user'):
                contents = 'su %(user)s -c \\\n  "%(contents)s"' % dict(
                    user=options['user'],
                    contents=contents,
                    )
            contents = "#!/bin/sh\n%s\n" % contents

            dest = os.path.join(options['rc-directory'], rc)
            if not (os.path.exists(dest) and open(dest).read() == contents):
                open(dest, 'w').write(contents)
                os.chmod(dest, 0755)
                logger.info("Generated shell script %r.", dest)
        else:
            zc.buildout.easy_install.scripts(
                [(rc, 'zdaemon.zdctl', 'main')],
                ws, options['executable'], options['rc-directory'],
                arguments = ('['
                             '\n        %r, %r,'
                             '\n        ]+sys.argv[1:]'
                             '\n        '
                             % ('-C', zdaemon_conf_path,
                                )
                             ),
                )

        return options.created()


    update = install

def event_log(path, *data):
    return ZConfig.schemaless.Section(
        'eventlog', '', None,
        [ZConfig.schemaless.Section('logfile', '', dict(path=[path]))])

event_log_template = """
<eventlog>
  <logfile>
    path %s
    formatter zope.exceptions.log.Formatter
  </logfile>
</eventlog>
"""

logrotate_template = """%(logfile)s {
  rotate 5
  weekly
  postrotate
    %(rc)s -C %(conf)s reopen_transcript
  endscript
}
"""
