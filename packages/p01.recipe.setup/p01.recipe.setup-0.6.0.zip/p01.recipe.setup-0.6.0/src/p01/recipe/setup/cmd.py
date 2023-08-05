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

import zc.buildout
from subprocess import call

from p01.recipe.setup import LoggerMixin

TRUE_VALUES = ('yes', 'true', '1', 'on')
FALSE_VALUES = ('no', 'false', '0', 'off')


class CMDRecipe(LoggerMixin):
    """Runs a command when buildout part is installed or updated."""

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.options = options
        self.name = name

        stop_on_error = self.options.get('stop-on-error')
        if stop_on_error is not None:
            stop_on_error = stop_on_error.lower()
        
        if stop_on_error is None:
            self.stop = True
        elif stop_on_error in TRUE_VALUES:
            self.stop = True
        elif stop_on_error in FALSE_VALUES:
            self.stop = False
        else:
            msg = "Invalid value '%s' for 'stop_on_error', use %s %s" % (
                stop_on_error, ', '.join(TRUE_VALUES), ', '.join(FALSE_VALUES))
            self.logger.error(msg)
            raise zc.buildout.UserError(msg)

    def _execute(self, command):
        retcode = call(command, shell=True)
        if self.stop and retcode != 0:
            msg = "Non zero exit code (%s) while running command." % retcode
            self.logger.error(msg)
            raise zc.buildout.UserError(msg)

    def install(self):
        command = self.options.get('command', None)
        if not command:
            msg="No command specified"
            self.logger.error(msg)
            raise zc.buildout.UserError(msg)

        self.logger.info("Running '%s'" % command)
        self._execute(command)
        
        # just touch the update method which will prevent to output:
        # Unused options for cmd: 'update'.
        ignored = self.options.get('update', None)

        location = self.options.get('location')
        if location is not None:
            return location.split()
        else:
            return ()

    def update(self):
        command = self.options.get('update')
        if command is not None:
            self.logger.info("Running %s" % command)
            self._execute(command)
