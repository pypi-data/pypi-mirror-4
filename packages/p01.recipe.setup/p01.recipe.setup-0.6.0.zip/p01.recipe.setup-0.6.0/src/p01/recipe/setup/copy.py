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
import shutil
import zc.buildout

from p01.recipe.setup import CHMODMixin

TRUE_VALUES = ('yes', 'true', '1', 'on')
FALSE_VALUES = ('no', 'false', '0', 'off')


class COPYRecipe(CHMODMixin):
    """Copy source directory or file to a given location using shutil."""

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.options = options
        self.name = name
        self.mode = int(options.get('mode', '0644'), 8)
        self.source = options['source']
        self.target = options['target']

        removeExisting = self.options.get('remove-existing')
        if removeExisting is not None:
            removeExisting = removeExisting.lower()

        if removeExisting in TRUE_VALUES:
            self.removeExisting = True
        elif removeExisting in FALSE_VALUES:
            self.removeExisting = False
        else:
            if removeExisting is None:
                msg = "Missing 'remove-existing' (%s) or (%s)" % (
                    ', '.join(TRUE_VALUES), ', '.join(FALSE_VALUES))
            else:
                msg = "Invalid remove-existing value '%s' (%s) or (%s)" % (
                    removeExisting, ', '.join(TRUE_VALUES), ', '.join(FALSE_VALUES))
            self.logger.error(msg)
            raise zc.buildout.UserError(msg)

    def install(self):
        """Copy directory structure."""
        # error handling
        if not os.path.exists(self.source):
            self.logger.error(
                'Source folder or file %s is missing', self.source)
            raise zc.buildout.UserError('Missing source folder or file')

        isDir = False
        if os.path.isdir(self.source):
            isDir = True

        # remove existing:
        if self.removeExisting:
            if os.path.isdir(self.target):
                shutil.rmtree(self.target)
                self.logger.info("Remove old folder '%s'" % self.target)
            elif os.path.isfile(self.target):
                os.remove(self.target)
                self.logger.info("Remove old file '%s'" % self.target)
            
        # copy source to target if the target does not exist
        if not os.path.exists(self.target):
            self.logger.info("Copy source '%s' to '%s'" % (
                self.source, self.target))
            if isDir:
                shutil.copytree(self.source, self.target)
            else:
                shutil.copy(self.source, self.target)

            self.doChmod(self.target, self.mode)
            return (self.target,)

    update = install
