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
import zc.recipe.egg

from p01.recipe.setup import CHMODMixin
from p01.recipe.setup import CHOWNMixin
from p01.recipe.setup import doChmod
from p01.recipe.setup import doChown
from p01.recipe.setup import makeBoolString
from p01.recipe.setup import TRUE_VALUES
from p01.recipe.setup import FALSE_VALUES


initialization_template = """import os
sys.argv[0] = os.path.abspath(sys.argv[0])
"""

env_template = """os.environ['%s'] = %r
"""


class COPYRecipe(CHMODMixin, CHOWNMixin):
    """Copy source directory or file to a given location using shutil."""

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.options = options
        self.name = name
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

            # set mode
            self.doChmod(self.target, self.mode)
            # set owner if given
            self.doChown(self.target, self.owner)

            return (self.target,)

    # run install baecause buildout doesn't know if source get changed
    update = install


class COPYScriptRecipe(CHOWNMixin, CHMODMixin):
    """Recipe which installs a script for copy directory to a file to a given
    location using shutil.
    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.options = options
        self.name = name
        self.source = options['source']
        self.target = options['target']
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
        self.removeExisting = options.get('remove-existing')

        if not options.get('working-directory', ''):
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'], name)

        self.options = options
        if 'eggs' not in self.options:
            self.options['eggs'] = ''
        self.options['eggs'] = self.options['eggs'] + '\n' + 'zc.buildout'
        self.options['eggs'] = self.options['eggs'] + '\n' + 'zc.recipe.egg'
        self.options['eggs'] = self.options['eggs'] + '\n' + 'p01.recipe.setup'
        self.egg = zc.recipe.egg.Egg(buildout, name, self.options)

    def install(self):
        """Copy directory structure."""
        dest = []
        options = self.options
        executable = self.buildout['buildout']['executable']
        source = '"%s"' % self.source.replace('\\', '\\\\')
        target = '"%s"' % self.target.replace('\\', '\\\\')
        mode = '%s' % self.mode
        owner = '"%s"' % self.owner and self.owner or 'None'
        removeExisting = makeBoolString(self.removeExisting, False)

        # setup additional egg path
        if self.egg:
            extra_paths = self.egg.extra_paths
            eggs, ws = self.egg.working_set()
        else:
            extra_paths = ()
            ws = []

        # setup environment
        initialization = initialization_template
        env_section = options.get('environment', '').strip()
        if env_section:
            env = self.buildout[env_section]
            for key, value in env.items():
                initialization += env_template % (key, value)

        # setup checker script
        arguments = [source, target, mode, owner, removeExisting]
        dest.extend(zc.buildout.easy_install.scripts(
            [(self.name, 'p01.recipe.setup.copy', 'process')],
            ws, executable, self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = ', '.join(arguments),
            initialization = initialization,
            ))

        return dest

    # run install baecause buildout doesn't know if source get changed
    update = install


def process(source, target, mode, owner, removeExisting):
    """copy source to target and change mode if given"""

    isDir = False
    if os.path.isdir(source):
        isDir = True

    # remove existing:
    if removeExisting:
        if os.path.isdir(target):
            shutil.rmtree(target)
            print "Remove old folder '%s'" % target
        elif os.path.isfile(target):
            os.remove(target)
            print "Remove old file '%s'" % target
        
    # copy source to target if the target does not exist
    if not os.path.exists(target):
        print "Copy source '%s' to '%s'" % (source, target)
        if isDir:
            shutil.copytree(source, target)
        else:
            shutil.copy(source, target)

        doChmod(target, mode)

        doChown(target, owner)
