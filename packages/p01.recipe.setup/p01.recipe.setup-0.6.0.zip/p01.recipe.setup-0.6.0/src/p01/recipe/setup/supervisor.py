##############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH and Contributors.
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
"""
$Id:$
"""

import os
import zc.recipe.egg

from p01.recipe.setup import LoggerMixin

TRUE_VALUES = ('yes', 'true', '1', 'on')


# TODO: implement option for copy init.d script to the right location
#       but only if not there  already
class SupervisorRecipe(LoggerMixin):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.options = options
        self.name = name

        if "user" not in options:
            msg = "No user specified in supervisor buildout.cfg."
            self.logger.error(msg)
            raise zc.buildout.UserError(msg)

        if "password" not in options:
            msg = "No password specified in supervisor buildout.cfg."
            self.logger.error(msg)
            raise zc.buildout.UserError(msg)

    def install(self):
        # supervisorctl args
        server = self.options.get('server', '127.0.0.1')
        port = self.options.get('port', '9001')
        user = self.options.get('user', 'admin')
        password = self.options.get('password', 'secret')
        gis = self.options.get('generate-initd-script', None)
        if gis is not None and gis in TRUE_VALUES:
            initScript = True
        else:
            initScript = False

        # conf file path
        if self.options.get('conf', None) is not None:
            confPath = self.options.get('conf')
        else:
            confPath = os.path.join(self.buildout['buildout']['parts-directory'],
                self.name, 'supervisord.conf')

        # check config file path
        if not os.path.exists(confPath):
            msg = "No (conf) supervisord.conf (file path) specified."
            self.logger.error(msg)
            raise zc.buildout.UserError(msg)

        # supervisord script
        dScript = zc.recipe.egg.Egg(self.buildout, self.name,
              {'eggs': 'supervisor',
               'scripts': 'supervisord=%sd' % self.name,
               'initialization': 'import sys; sys.argv.extend(["-c","%s"])' % \
                confPath})
        for f in dScript.install():
            self.options.created(f)

        # superlance memmon script
        memScript = zc.recipe.egg.Egg(self.buildout, self.name,
            {'eggs': 'supervisor',
             'scripts': 'memmon=memmon'})
        for f in memScript.install():
            self.options.created(f)

        # supervisorctl script
        init = '["-c","%s","-u","%s","-p","%s","-s","http://%s:%s"]' % \
                (confPath, user, password, server, port)
        ctlScript = zc.recipe.egg.Egg(self.buildout, self.name,
            {'eggs': 'supervisor',
             'scripts': 'supervisorctl=%sctl' % self.name,
             'initialization': 'import sys; sys.argv[1:1] = %s' % init,
             'arguments': 'sys.argv[1:]'})
        for f in ctlScript.install():
            self.options.created(f)

        # install extra eggs if any
        eggs = self.options.get('plugins', None)       
        if eggs is not None:
            for f in list(zc.recipe.egg.Egg(self.buildout, self.name,
                {'eggs':eggs}).install()):
                self.options.created(f)

        if initScript:
            # setup init.d script
            # you can use the generated file init.d startup script
            # copy the file to /etc/init.d/supervisor and do:
            # chmod +x /etc/init.d/supervisord
            # update-rc.d supervisord defaults
            ini = INITD % {
                'binDir': self.buildout['buildout']['bin-directory'],
                'confPath': confPath}
            iPath = os.path.join(self.buildout['buildout']['parts-directory'],
                self.name, 'supervisord-initd-script')
            iDir = os.path.abspath(os.path.dirname(iPath))
            if not os.path.isdir(iDir):
                os.makedirs(iDir)
            open(iPath, 'w').write(ini)
            self.options.created(iPath)

        return self.options.created()

    update = install


INITD = r"""#!/bin/sh
### BEGIN INIT INFO
# Provides:          supervisor
# Default-Start:     2 3 4 5
# Default-Stop:      S 0 1 6
# Short-Description: Starts/stops the supervisor daemon
# Description:       This starts and stops the supervisor dameon
#                    which is used to run and monitor arbitrary programs as
#                    services, e.g. application servers etc.
### END INIT INFO

PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
DESC="supervisor daemon"
NAME="supervisor"

### GENERATED BY p01.recipe.setup:supervisor recipe
DAEMON="%(binDir)s/${NAME}d"
SUPERVISORCTL="%(binDir)s/${NAME}ctl"
PIDFILE="/var/run/${NAME}d.pid"
SCRIPTNAME="/etc/init.d/$NAME"
CONFFILE="%(confPath)s"
###

test -x "$DAEMON" || exit 0
test -r "$CONFFILE" || exit 0

if [ -r "/etc/default/$NAME" ]; then
    . "/etc/default/$NAME"
fi

set -e

d_start() {
    start-stop-daemon --start --quiet --pidfile "$PIDFILE" \
        --exec "$DAEMON" \
        || echo -n " already running"
}

d_stop() {
    $SUPERVISORCTL shutdown
}

d_reload() {
    $SUPERVISORCTL reload
}

case "$1" in
  start)
    echo -n "Starting $DESC: $NAME"
    d_start
    echo "."
    ;;
  stop)
    echo -n "Stopping $DESC: $NAME"
    d_stop
    echo "."
    ;;
  reload|force-reload)
    echo -n "Reloading $DESC configuration..."
    d_reload
    echo "done."
  ;;
  restart)
    echo -n "Restarting $DESC: $NAME"
    d_stop
    sleep 1
    d_start
    echo "."
    ;;
  *)
    echo "Usage: "$SCRIPTNAME" {start|stop|restart|force-reload}" >&2
    exit 3
    ;;
esac

exit 0

"""

