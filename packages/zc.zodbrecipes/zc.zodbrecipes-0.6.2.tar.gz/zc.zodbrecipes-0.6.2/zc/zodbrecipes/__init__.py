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

import logging, os, shutil
import zc.recipe.egg
import zc.buildout
import ZConfig.schemaless
import cStringIO

from ZConfig import ConfigurationSyntaxError

logger = logging.getLogger('zc.zodbrecipes')

class StorageServer:

    def __init__(self, buildout, name, options):
        self.name, self.options = options.get('name', name), options

        deployment = self.deployment = options.get('deployment')
        if deployment:
            options['deployment-name'] = buildout[deployment].get(
                'name', deployment)
            options['rc-directory'] = buildout[deployment]['rc-directory']
            options['run-directory'] = buildout[deployment]['run-directory']
            options['log-directory'] = buildout[deployment]['log-directory']
            options['etc-directory'] = buildout[deployment]['etc-directory']
            logrotate = options.get('logrotate',
                                    buildout[deployment].get('logrotate',''))
            if logrotate.lower()=='false':
                options['logrotate'] = ''
            else:
                options['logrotate'] = os.path.join(
                    buildout[deployment]['logrotate-directory'],
                    options['deployment-name'] + '-' + self.name)
            options['crontab-directory'] = buildout[
                deployment]['crontab-directory']
            options['user'] = buildout[deployment]['user']
        else:
            options['rc-directory'] = buildout['buildout']['bin-directory']
            options['run-directory'] = os.path.join(
                buildout['buildout']['parts-directory'],
                self.name,
                )

        options['scripts'] = ''
        options['eggs'] = options.get('eggs','') + '\nzdaemon\nsetuptools'
        self.egg = zc.recipe.egg.Egg(buildout, name, options)

        options['runzeo'] = os.path.join(
            buildout['buildout']['bin-directory'],
            options.get('runzeo', 'runzeo'),
            )

        options['zdaemon'] = os.path.join(
            buildout['buildout']['bin-directory'],
            options.get('zdaemon', 'zdaemon'),
            )

        options['zeopack'] = os.path.join(
            buildout['buildout']['bin-directory'],
            options.get('zeopack', 'zeopack'),
            )

        if options.get('shell-script', '') not in ('true', 'false', ''):
            raise zc.buildout.UserError(
                'The shell-script option value must be "true", "false" or "".')

    def install(self):
        options = self.options

        if not os.path.exists(options['runzeo']):
            logger.warn(no_runzeo % options['runzeo'])

        run_directory = options['run-directory']
        deployment = self.deployment
        if deployment:
            zeo_conf_path = os.path.join(options['etc-directory'],
                                         self.name+'-zeo.conf')
            zdaemon_conf_path = os.path.join(options['etc-directory'],
                                             self.name+'-zdaemon.conf')
            event_log_path = os.path.join(options['log-directory'],
                                          self.name+'-zeo.log')
            socket_path = os.path.join(run_directory,
                                       self.name+'-zdaemon.sock')
            rc = options['deployment-name'] + '-' + self.name

            options.created(
                zeo_conf_path,
                zdaemon_conf_path,
                os.path.join(options['rc-directory'], rc),
                )

            logrotate = options['logrotate']
            if logrotate:
                open(logrotate, 'w').write(logrotate_template % dict(
                    logfile=event_log_path,
                    rc=os.path.join(options['rc-directory'], rc),
                    conf=zdaemon_conf_path,
                    ))
                options.created(logrotate)

            pack = options.get('pack')
            if pack:
                pack = pack.split()
                if len(pack) < 5:
                    raise zc.buildout.UserError(
                        'Too few crontab fields in pack specification')
                if len(pack) > 7:
                    raise zc.buildout.UserError(
                        'Too many values in pack option')
                pack_path = os.path.join(
                    options['crontab-directory'],
                    "pack-%s-%s" % (options['deployment-name'], self.name),
                    )
                if not os.path.exists(options['zeopack']):
                    logger.warn("Couln'e find zeopack script, %r",
                                options['zeopack'])
        else:
            zeo_conf_path = os.path.join(run_directory, 'zeo.conf')
            zdaemon_conf_path = os.path.join(run_directory, 'zdaemon.conf')
            event_log_path = os.path.join(run_directory, 'zeo.log')
            socket_path = os.path.join(run_directory, 'zdaemon.sock')
            rc = self.name
            options.created(run_directory,
                            os.path.join(options['rc-directory'], rc),
                            )
            if not os.path.exists(run_directory):
                os.mkdir(run_directory)
            pack = pack_path = None

        zeo_conf = options.get('zeo.conf', '')+'\n'
        try:
            zeo_conf = ZConfig.schemaless.loadConfigFile(
                cStringIO.StringIO(zeo_conf))
        except ConfigurationSyntaxError,e:
            raise zc.buildout.UserError(
                '%s in:\n%s' % (e,zeo_conf)
                )

        zeo_section = [s for s in zeo_conf.sections if s.type == 'zeo']
        if not zeo_section:
            raise zc.buildout.UserError('No zeo section was defined.')
        if len(zeo_section) > 1:
            raise zc.buildout.UserError('Too many zeo sections.')
        zeo_section = zeo_section[0]
        if not 'address' in zeo_section:
            raise zc.buildout.UserError('No ZEO address was specified.')

        storages = [s.name or '1' for s in zeo_conf.sections
                    if s.type not in ('zeo', 'eventlog', 'runner')
                    ]

        if not storages:
            raise zc.buildout.UserError('No storages were defined.')

        if not [s for s in zeo_conf.sections if s.type == 'eventlog']:
            zeo_conf.sections.append(event_log('STDOUT'))

        zdaemon_conf = options.get('zdaemon.conf', '')+'\n'
        zdaemon_conf = ZConfig.schemaless.loadConfigFile(
            cStringIO.StringIO(zdaemon_conf))

        defaults = {
            'program': "%s -C %s" % (options['runzeo'], zeo_conf_path),
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

        zdaemon_conf = str(zdaemon_conf)

        self.egg.install()
        requirements, ws = self.egg.working_set()

        open(zeo_conf_path, 'w').write(str(zeo_conf))
        open(zdaemon_conf_path, 'w').write(str(zdaemon_conf))

        if options.get('shell-script') == 'true':
            if not os.path.exists(options['zdaemon']):
                logger.warn(no_zdaemon % options['zdaemon'])

            contents = "%(zdaemon)s -C '%(conf)s' $*" % dict(
                zdaemon = options['zdaemon'],
                conf = zdaemon_conf_path,
                )
            if options.get('user'):
                contents = 'su %(user)s -c \\\n  "%(contents)s"' % dict(
                    user = options['user'],
                    contents = contents,
                    )
            contents = "#!/bin/sh\n%s\n" % contents

            dest = os.path.join(options['rc-directory'], rc)
            if not (os.path.exists(dest) and open(dest).read() == contents):
                open(dest, 'w').write(contents)
                os.chmod(dest, 0755)
                logger.info("Generated shell script %r.", dest)

        else:
            self.egg.install()
            requirements, ws = self.egg.working_set()
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

        if pack:
            address, = zeo_section['address']
            if ':' in address:
                host, port = address.split(':')
                address = '-h %s -p %s' % (host, port)
            else:
                try:
                    port = int(address)
                except:
                    address = '-U '+address
                else:
                    address = '-p '+address
            f = open(pack_path, 'w')
            if len(pack) == 7:
                assert '@' in pack[6]
                f.write("MAILTO=%s\n" % pack.pop())

            if len(pack) == 6:
                days = pack.pop()
            else:
                days = 1

            for storage in storages:
                f.write("%s %s %s %s -S %s -d %s\n" % (
                        ' '.join(pack), options['user'],
                        options['zeopack'], address, storage, days,
                        ))
            f.close()
            options.created(pack_path)

        return options.created()

    update = install

no_runzeo = """
A runzeo script couldn't be found at:

  %r

You may need to generate a runzeo script using the
zc.recipe.eggs:script recipe and the ZODB3 egg, or you may need
to specify the location of a script using the runzeo option.
"""

no_zdaemon = """
A zdaemon script couldn't be found at:

  %r

You may need to generate a zdaemon script using the
zc.recipe.eggs:script recipe and the zdaemon egg.
"""

def event_log(path, *data):
    return ZConfig.schemaless.Section(
        'eventlog', '', None,
        [ZConfig.schemaless.Section('logfile', '', dict(path=[path]))])

logrotate_template = """%(logfile)s {
  rotate 5
  weekly
  postrotate
    %(rc)s -C %(conf)s reopen_transcript
  endscript
}
"""
