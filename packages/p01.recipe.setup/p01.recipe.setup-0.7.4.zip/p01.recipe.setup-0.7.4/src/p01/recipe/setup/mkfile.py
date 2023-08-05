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
import zc.buildout

from p01.recipe.setup import CHMODMixin
from p01.recipe.setup import CHOWNMixin
from p01.recipe.setup import LoggerMixin


class MKFileRecipe(CHMODMixin, CHOWNMixin, LoggerMixin):
    """Make file recipe based on file path using file(path, 'w')."""

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.options = options
        self.name = name

        # touch content, raises error if missing
        options['content']
        self.originalPath = options['target']
        options['target'] = os.path.join(buildout['buildout']['directory'],
            self.originalPath)
        self.createPath = options.get('createpath', 'False').lower() in [
            'true', 'on', '1']
        # mode
        self.mode = options.get('mode', '0644')
        if self.mode is not None:
            try:
                self.mode = int(self.mode, 8)
            except ValueError:
                raise zc.buildout.UserError(
                    "'mode' must be an octal number: " % self.mode)
        # owner
        self.owner = options.get('owner')

    def install(self):
        target = self.options['target']
        if (not self.createPath and not os.path.isdir(os.path.dirname(target))):
            self.logger.error('Cannot create file %s. %s is not a directory.',
                target, os.path.dirname(target))
            raise zc.buildout.UserError(
                'Invalid path in p01.recipe.setup:mkfile recipe')

        if self.createPath:
            dirname = os.path.dirname(target)
            if not os.path.isdir(dirname):
                self.logger.info('Creating directory %s', dirname)
                os.makedirs(dirname)
        f = file(target, 'w')
        self.logger.info('Writing file %s', target)
        f.write(self.options['content'])
        f.close()

        # set mode if given
        self.doChmod(target, self.mode)

        # set owner if given
        self.doChown(target, self.owner)

        return target

    def update(self):
        # do not update, only use install if something has changed
        pass

