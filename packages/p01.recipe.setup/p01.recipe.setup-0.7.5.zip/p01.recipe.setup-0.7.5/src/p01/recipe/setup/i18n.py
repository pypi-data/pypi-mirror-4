##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
A Buildout recipe for i18n scripts.
"""
__docformat__ = 'restructuredtext'

import os
import sys

import zc.buildout
import zc.recipe.egg

from p01.recipe.setup import LoggerMixin


zcmlTemplate = """<configure xmlns='http://namespaces.zope.org/zope'
           xmlns:meta="http://namespaces.zope.org/meta"
           >

  %s

</configure>
"""

initialization_template = """import os
sys.argv[0] = os.path.abspath(sys.argv[0])
"""


env_template = """os.environ['%s'] = %r
"""


class I18nSetup(LoggerMixin):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        if 'eggs' not in self.options:
            self.options['eggs'] = ''
        self.options['eggs'] = self.options['eggs'] + '\n' + 'p01.recipe.setup[i18n]'
        self.egg = zc.recipe.egg.Egg(buildout, name, self.options)

    def install(self):
        options = self.options
        executable = self.buildout['buildout']['executable']

        # options
        excludeDefaultDomain = options.get('excludeDefaultDomain',
            False)

        pythonOnly = options.get('pythonOnly', False)
        verify_domain = options.get('verify_domain', False)

        # setup configuration file
        zcml = options.get('zcml', None)
        if zcml is None:
            raise zc.buildout.UserError('No zcml configuration defined.')
        zcml = zcmlTemplate % zcml

        # get domain
        domain = options.get('domain', None)
        if domain is None:
            raise zc.buildout.UserError('No domain given.')

        # get output path
        output = options.get('output', None)
        if output is None:
            raise zc.buildout.UserError('No output path given.')
        output = os.path.abspath(output)
        # windows
        output = output.replace('\\', '/')

        dest = []
        partsDir = os.path.join(self.buildout['buildout']['parts-directory'],
            self.name)
        if not os.path.exists(partsDir):
            os.mkdir(partsDir)
            dest.append(partsDir)
        zcmlFilename = os.path.join(partsDir, 'configure.zcml')
        file(zcmlFilename, 'w').write(zcml)
        dest.append(zcmlFilename)
        zcmlFilename = zcmlFilename.replace('\\', '/')

        # Generate i18nextract
        arguments = ['sys.argv[0]']
        def add_reprs(*args):
            args = list(args)
            arguments.append("\n         " + repr(args.pop(0)))
            arguments.extend(repr(arg) for arg in args)
        add_reprs('-d', domain)
        arguments.extend(["\n         " + repr('-s'), "'%s'" % zcmlFilename])
        arguments.extend(["\n         " + repr('-o'), "'%s'" % output])

        if excludeDefaultDomain:
            add_reprs('--exclude-default-domain')

        if pythonOnly:
            add_reprs('--python-only')

        if verify_domain:
            add_reprs('--verify-domain')

        makers = [m for m in options.get('maker', '').split() if m!='']
        for m in makers:
            add_reprs('-m', m)

        # add package names as -p multi option
        packages = [p for p in options.get('packages', '').split()
                    if p!='']
        for p in packages:
            add_reprs('-p', p)

        # This code used to have a typo: the option was exludeDirectoryName
        # instead of excludeDirectoryName.  For backwards compatibility,
        # allow the old value, though prefer the properly-spelled one.
        excludeDirNames_raw = options.get(
            'excludeDirectoryName', options.get('exludeDirectoryName', ''))
        excludeDirNames = [x for x in excludeDirNames_raw.split() if x!='']
        for x in excludeDirNames:
            arguments.extend(
                ["\n         " + repr('-x'), "'%s'" % x])

        header_template = options.get('headerTemplate', None)
        if header_template is not None:
            header_template = os.path.normpath(
                os.path.join(self.buildout['buildout']['directory'],
                             header_template.strip()))
            arguments.extend(
                ["\n         " + repr('-t'), "'%s'" % header_template])

        arguments = '\n        [' + ', '.join(arguments) + '\n        ]'


        # setup environment
        initialization = initialization_template
        env_section = self.options.get('environment', '').strip()
        if env_section:
            env = self.buildout[env_section]
            for key, value in env.items():
                initialization += env_template % (key, value)

        # setup egg path
        # setup additional egg path
        if self.egg:
            extra_paths = self.egg.extra_paths
            eggs, ws = self.egg.working_set()
        else:
            extra_paths = ()
            ws = []

        # Generate i18nextract
        dest.extend(zc.buildout.easy_install.scripts(
            [('%sextract'% self.name, 'p01.recipe.setup.i18nextract', 'main')],
            ws, executable, self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = arguments,
            initialization = initialization,
            ))

        # Generate i18nmergeall
        dest.extend(
            item for item in
            zc.buildout.easy_install.scripts(
                [('%smergeall'% self.name, 'p01.recipe.setup.i18nmergeall', 'main')],
                ws, executable, self.buildout['buildout']['bin-directory'],
                extra_paths = extra_paths,
                arguments = "[sys.argv[0], '-l', '%s']" % output,
                initialization = initialization,
            )
            if item not in dest)

        # Generate i18nstats
        dest.extend(
            item for item in
            zc.buildout.easy_install.scripts(
                [('%sstats'% self.name, 'p01.recipe.setup.i18nstats', 'main')],
                ws, executable, self.buildout['buildout']['bin-directory'],
                extra_paths = extra_paths,
                arguments = "[sys.argv[0], '-l', '%s']" % output,
            )
            if item not in dest)

        # Generate i18ncompile
        dest.extend(
            item for item in
            zc.buildout.easy_install.scripts(
                [('%scompile'% self.name, 'p01.recipe.setup.i18ncompile', 'main')],
                ws, executable, self.buildout['buildout']['bin-directory'],
                extra_paths = extra_paths,
                arguments = "[sys.argv[0], '-l', '%s']" % output,
            )
            if item not in dest)

        return dest

    update = install
