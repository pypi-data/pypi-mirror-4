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

from p01.recipe.setup import CHOWNMixin
from p01.recipe.setup import LoggerMixin


class MKDirRecipe(CHOWNMixin, LoggerMixin):
    """Make directory recipe using os.makedirs(path)."""

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.options = options
        self.name = name

        self.originalPath = options['path']
        options['path'] = os.path.join(buildout['buildout']['directory'],
            self.originalPath)
        self.createPath = options.get('createpath', 'False').lower() in [
            'true', 'on', '1']

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

        # set owner if given
        owner = self.options.get('owner')
        self.doChown(path, owner)

        return ()

    def update(self):
        # do not update, only use install if something has changed
        pass

