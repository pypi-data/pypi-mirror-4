##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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

import logging
import os
import shutil
import subprocess
import stat
import zc.buildout

logger = logging.getLogger('zc.recipe.rhrc')

class Recipe:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        deployment = self.deployment = options.get('deployment')
        if deployment:
            options['deployment-name'] = buildout[deployment].get('name',
                                                                  deployment)
            if 'user' not in options:
                options['user'] = buildout[deployment].get('user', '')
            options['dest'] = self.options.get(
                'dest', buildout[deployment]['rc-directory'])
        else:
            options['dest'] = self.options.get('dest', '/etc/init.d')

        options['scripts'] = '\n'.join([buildout[part].get('run-script', '')
                                        for part in options['parts'].split()
                                        ])
        options['envs'] = '\n'.join([buildout[part].get('env', '')
                                     for part in options['parts'].split()
                                     ])
        independent = options.get('independent-processes')
        if independent:
            if independent not in ('true', 'false'):
                logger.error(
                    "Invalid value for independent-processes. "
                    " Use 'true' or 'false'")
                raise zc.buildout.UserError(
                    'Invalid value for independent-processes:', independent)

        if options.get('process-management', 'false') not in (
            'true', 'false'):
            raise zc.buildout.UserError('Invalid process-management option: %r'
                                        % (options['process-management']))

    def install(self):
        options = self.options
        name = options.get('deployment-name', self.name)
        parts = options['parts'].split()
        if not parts:
            return
        scripts = options['scripts'].split('\n')
        chkconfig = self.options.get('chkconfig')
        user = options.get('user', '')
        if user == 'root':
            user = '' # no need to su to root
        envs = options['envs'].split('\n')
        created = []
        start = self.options.get('process-management')
        try:
            if len(scripts) == 1:
                # No mongo script
                script = scripts[0]
                if script:
                    if user:
                        script = 'su %s -c \\\n      "%s $*"' % (user, script)
                    else:
                        script += ' $*'

                    env = envs[0]
                    if env:
                        script = env + ' \\\n      ' + script
                else:
                    script = self.no_script(parts[0])

                if chkconfig:
                    script += ' \\\n      </dev/null'
                self.output(chkconfig, script, name, created,
                            start=start)
            else:
                cooked = []
                for part, env, script in zip(parts, envs, scripts):
                    if script:

                        if user:
                            script = 'su %s -c \\\n      "%s $*"' % (
                                user, script)
                        else:
                            script += ' $*'

                        if env:
                            script = env + ' \\\n      ' + script

                        self.output('', script, name+'-'+part, created)

                    else:
                        script = self.no_script(part)

                    cooked.append(script)

                if chkconfig:
                    cooked = [s + ' \\\n      </dev/null'
                              for s in cooked]

                script = '\n\n    '.join(cooked)
                cooked.reverse()
                rscript = '\n\n    '.join(cooked)
                self.output(
                    chkconfig, script, name, created, rscript,
                    independent=options.get('independent-processes') == 'true',
                    start=start,
                    )
            return created
        except:
            [os.remove(f) for f in created]
            raise

    def no_script(self, part):
        options = self.options
        name = options.get('deployment-name', self.name)
        if self.deployment:
            path = os.path.join(options['dest'], name+'-'+part)
            script = 'echo %s:\n%s' % ( name+'-'+part, path)
        else:
            path = os.path.join(options['dest'], part)
            script = 'echo %s:\n%s' % (part, path)
        if not os.path.exists(path):
            logger.error("Part %s doesn't define run-script "
                         "and %s doesn't exist."
                         % (part, path))
            raise zc.buildout.UserError("No script for", part)

        return script + ' "$@"'

    def output(self, chkconfig, script, ctl, created,
               rscript=None, independent=False, start=False):
        if independent:
            rc = independent_template % dict(
                rootcheck = self.options.get('user') and rootcheck or '',
                CHKCONFIG = (chkconfig
                             and (chkconfig_template % chkconfig)
                             or non_chkconfig_template),
                CTL_SCRIPT = script,
                )
        else:
            rc = rc_template % dict(
                rootcheck = self.options.get('user') and rootcheck or '',
                CHKCONFIG = (chkconfig
                             and (chkconfig_template % chkconfig)
                             or non_chkconfig_template),
                CTL_SCRIPT = script,
                CTL_SCRIPT_R = rscript or script,
                )
        dest = self.options.get('dest', '/etc/init.d')
        ctlpath = os.path.join(dest, ctl)
        open(ctlpath, 'w').write(rc)
        created.append(ctlpath)
        os.chmod(ctlpath,
                 os.stat(ctlpath).st_mode | stat.S_IEXEC | stat.S_IXGRP)
        if chkconfig:
            chkconfigcommand = self.options.get('chkconfigcommand',
                                                '/sbin/chkconfig')
            os.system(chkconfigcommand+' --add '+ctl)

        if start and subprocess.call([ctlpath, 'start']):
            raise RuntimeError("%s start failed" % ctlpath)

    update = install

def uninstall(name, options):
    name = options.get('deployment-name', name)
    if options.get('process-management') == 'true':
        ctlpath = os.path.join(options.get('dest', '/etc/init.d'), name)
        subprocess.call([ctlpath, 'stop'])
    if options.get('chkconfig'):
        chkconfigcommand = options.get('chkconfigcommand', '/sbin/chkconfig')
        os.system(chkconfigcommand+' --del '+name)


chkconfig_template = '''\
# the next line is for chkconfig
# chkconfig: %s
# description: please, please work
'''

non_chkconfig_template = '''\
# This script is for adminstrator convenience.  It should
# NOT be installed as a system startup script!
'''

rootcheck = """
if [ $(whoami) != "root" ]; then
  echo "You must be root."
  exit 1
fi
"""

rc_template = """#!/bin/sh

%(CHKCONFIG)s
%(rootcheck)s
case $1 in
  stop)

    %(CTL_SCRIPT_R)s

    ;;
  restart)

    ${0} stop
    sleep 1
    ${0} start

    ;;
  *)

    %(CTL_SCRIPT)s

    ;;
esac

"""

independent_template = """#!/bin/sh

%(CHKCONFIG)s
%(rootcheck)s
    %(CTL_SCRIPT)s
"""
