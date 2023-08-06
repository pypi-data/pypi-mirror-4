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
from p01.recipe.setup import TRUE_VALUES


class MKDirRecipe(CHOWNMixin, CHMODMixin, LoggerMixin):
    """Make directory recipe using os.makedirs(path)."""

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.options = options
        self.name = name

        self.originalPath = options['path']
        options['path'] = os.path.join(buildout['buildout']['directory'],
            self.originalPath)
        self.createPath = options.get('createpath', 'false') in TRUE_VALUES
        # mode
        self.mode = options.get('mode', None)
        if self.mode is not None:
            try:
                self.mode = int(self.mode, 8)
            except ValueError:
                raise zc.buildout.UserError(
                    "'mode' must be an octal number: " % self.mode)
        # owner
        self.owner = options.get('owner')

    def install(self):
        path = self.options['path']
        if (not self.createPath and not os.path.isdir(os.path.dirname(path))):
            self.logger.error('Cannot create %s. %s is not a directory.',
                path, os.path.dirname(path))
            raise zc.buildout.UserError(
                'Invalid path in p01.recipe.setup:mkdir recipe')

        if not os.path.isdir(path):
            self.logger.info('Creating directory %s', self.originalPath)
            os.makedirs(path)

        # set mode if given
        self.doChmod(path, self.mode)

        # set owner if given
        self.doChown(path, self.owner)

        return ()

    def update(self):
        # do not update, only use install if something has changed
        pass

