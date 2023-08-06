##############################################################################
#
# Copyright (c) 2006-2009 Zope Corporation and Contributors.
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

import os
import os.path
import sys
import shutil
import setuptools.archive_util

import zc.recipe.egg
import zc.buildout
import zc.buildout.download

from p01.recipe.setup import LoggerMixin


def system(c):
    if os.system(c):
        raise SystemError("Failed", c)


initialization_template = """import os
sys.argv[0] = os.path.abspath(sys.argv[0])
"""

env_template = """os.environ['%s'] = %r
"""


class MakeScriptRecipe(LoggerMixin):
    """This recipe will generate a script which can call configure, make and
    make install. This is the same as p01.recipe.setup.cmmi but not processed
    during buildout.
    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        directory = buildout['buildout']['directory']
        download_cache = buildout['buildout'].get('download-cache')

        parts = buildout['buildout']['parts-directory']
        self.options['location'] = os.path.join(parts, name)

        self.source = options.get('source')
        self.url = self.options.get('url')
        self.target = options["target"].replace('\\', '/')

        extra = self.options.get('extra-options', '')
        # get rid of any newlines that may be in the options so they
        # do not get passed through to the commandline
        self.extra = ' '.join(extra.split())

        self.environ = self.options.get('environment', '').split()
        if self.environ:
            self.environ = dict([x.split('=', 1) for x in self.environ])
        else:
            self.environ = {}

        self.cmdConfigure = self.options.get('configure-command', './configure')

        # path cleanup if \\ is used in configure-options
        optionsConfigure = self.options.get('configure-options', None)
        if optionsConfigure:
            optionsConfigure = ' '.join(optionsConfigure.split())
            # path cleanup for windows based minsys configure call
            # the dest path is probably messed up during an issue in buildout.
            # and configure doesn't like mixed os separators, just replace any
            # duble backslash with a forward slash. this allows us to use:
            # ${buildout:directory}/parts which normaly ends in a path mess like
            # C:\\dir\\subdir/parts
            optionsConfigure = self.optionsConfigure.replace('\\', '/')
        self.optionsConfigure = optionsConfigure

        self.cmdMake = self.options.get('make-command', 'make')
        self.cmdInstall = self.options.get('install-command', 'make install')

        if 'eggs' not in self.options:
            self.options['eggs'] = ''
        self.options['eggs'] = self.options['eggs'] + '\n' + 'zc.buildout'
        self.options['eggs'] = self.options['eggs'] + '\n' + 'p01.recipe.setup'
        self.egg = zc.recipe.egg.Egg(buildout, name, self.options)

    def install(self):
        dest = []
        options = self.options
        executable = self.buildout['buildout']['executable']

        location = options['location']
        # create part directory
        if not os.path.isdir(location):
            os.makedirs(location)

        # setup script properties
        target = "'%s'" % self.target
        cmdConfigure = "'%s'" % self.cmdConfigure
        cmdMake = "'%s'" % self.cmdMake
        cmdInstall = "'%s'" % self.cmdInstall
        if self.optionsConfigure:
            optionsConfigure = "'%s'" % self.optionsConfigure
        else:
            optionsConfigure = '%s' % self.optionsConfigure
        extra = "'%s'" % self.extra

        # path cleanup for windows based minsys configure call
        # the target path is probably messed up during an issue in buildout.
        # and configure doesn't like mixed os separators, just replace any
        # duble backslash with a forward slash. this allows us to use:
        # ${buildout:directory}/parts which normaly ends in a path mess like
        # C:\\dir\\subdir/parts
        location = location.replace('\\', '/')

        if self.url:
            # download from given url
            download = zc.buildout.download.Download(self.buildout['buildout'],
                namespace='cmmi', hash_name=True, logger=self.logger)
            fname, is_temp = download(self.url, md5sum=options.get('md5sum'))
        else:
            # otherwise use source
            fname = self.source
            is_temp = False

        # now unpack source and work as normal
        self.logger.info('Unpacking %s and configuring into %s' % (fname, location))
        try:
            setuptools.archive_util.unpack_archive(fname, location)
        finally:
            if is_temp:
                os.unlink(fname)

        # define new source for cmmi
        source = "'%s'" % options['location'].replace('\\', '\\\\')
        if sys.platform == 'win32':
            source = source.replace('/', '\\\\')

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
        arguments = [source, target, cmdConfigure, cmdMake, cmdInstall,
            optionsConfigure, extra]
        dest.extend(zc.buildout.easy_install.scripts(
            [(self.name, 'p01.recipe.setup.make', 'cmmi')],
            ws, executable, self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = ', '.join(arguments),
            initialization = initialization,
            ))

        return dest

    def update(self):
        pass


def cmmi(source, dest, cmdConfigure, cmdMake, cmdInstall, options, extra):
    """Do the 'configure; make; make install' command sequence.

    When this is called, the current working directory is the
    source directory.  The 'dest' parameter specifies the
    installation prefix.

    """
    # create dest directory
    if not os.path.isdir(dest):
        os.makedirs(dest)

    try:
        os.chdir(source)
        try:
            if not os.path.exists('configure'):
                entries = os.listdir(source)
                if len(entries) == 1:
                    os.chdir(entries[0])
                else:
                    raise ValueError("Couldn't find configure")
            # now as usual offering custom make and make install method hooks
            if not options:
                options = '--prefix=%s' % dest.replace('\\', '/')
            if extra:
                options += ' %s' % extra
            system("%s %s" % (cmdConfigure, options))
            system(cmdMake)
            system(cmdInstall)
        finally:
            os.chdir(source)
    except:
        shutil.rmtree(dest)
        raise
