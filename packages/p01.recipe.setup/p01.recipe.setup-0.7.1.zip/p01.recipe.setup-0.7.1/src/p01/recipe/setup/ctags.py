##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
import optparse
import pkg_resources
import subprocess
import sys

import zc.buildout
import zc.buildout.easy_install
import zc.recipe.egg

from p01.recipe.setup import LoggerMixin


class CTagsRecipe(LoggerMixin):
    """Make directory recipe using os.makedirs(path)."""

    def __init__(self, buildout, name, options):
        self.egg = None
        self.buildout = buildout
        self.name = name
        self.options = options
        options['script'] = os.path.join(buildout['buildout']['bin-directory'],
                                         options.get('script', self.name),
                                         )
        if not options.get('working-directory', ''):
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'], name)

        if 'eggs' not in self.options:
            self.options['eggs'] = ''
        self.options['eggs'] = self.options['eggs'] + '\n' + 'p01.recipe.setup'
        self.egg = zc.recipe.egg.Egg(buildout, name, self.options)

    def install(self):
        options = self.options
        location = options['location']
        executable = self.buildout['buildout']['executable']

        # setup path
        dest = []
        if not os.path.exists(location):
            os.mkdir(location)
            dest.append(location)
            self.logger.info('Creating directory %s', location)

        # setup paster script
        if self.egg is not None:
            extra_paths = self.egg.extra_paths
        else:
            extra_paths = []

        eggs, ws = self.egg.working_set()

        # setup environment
        initialization = initialization_template
        env_section = self.options.get('environment', '').strip()
        if env_section:
            env = self.buildout[env_section]
            for key, value in env.items():
                initialization += env_template % (key, value)

        dest.extend(zc.buildout.easy_install.scripts(
            [('%s'% self.name, 'p01.recipe.setup.ctags', 'ctags')],
            ws, self.options['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = [location],
            initialization = initialization
            ))

        return dest

    update = install


initialization_template = """import os
sys.argv[0] = os.path.abspath(sys.argv[0])
"""

env_template = """os.environ['%s'] = %r
"""


def getpath(candidates):
    paths = os.environ['PATH'].split(os.pathsep)
    for c in candidates:
        for p in paths:
            full = os.path.join(p, c)
            if os.path.exists(full):
                return full
    raise RuntimeError(
        'Can\'t find executable for any of: %s' % candidates)


class Builder(LoggerMixin):

    def __init__(self, target):
        self.target = target
        self.paths = [path for path in sys.path
                      if not path.endswith('.zip')]

    def __call__(self, targets=None, languages=None, langmap=None):
        if not targets:
            targets = ('ctags_vi',) # legacy behavior
        self.languages = languages or 'Python'
        self.langmap = langmap or 'html:+.pt'
        results = {}
        for target in targets:
            tool_candidates, arguments, source, destination = getattr(
                self, '_build_%s' % (target,))()
            arguments[0:0] = [getpath(tool_candidates)]
            print "ctags subprocess called with the following arguments:"
            print "\n".join(arguments)
            res = subprocess.call(arguments, shell=True)
            if res == 0:
                dest = os.path.join(self.target, destination)
                res = subprocess.call(['mv', source, dest])
                print "%s file generated" % dest
            results[target] = res
        return results

    def _build_idutils(self):
        idPath = r'%s' % pkg_resources.resource_filename("p01.recipe.setup", 
            "id-lang.map")
        # XXX: fix method call with path argument, it seems that the mkid.exe
        # hat troubles with a simple path, probably with \t (\trunk\) in it?
        #idPath = idPath.replace('\\\\', '/')
        #idPath = idPath.replace('\\', '/')
        return [['mkid', 'mkid.exe'],
                ['-m', idPath, '-o', 'ID.new'] + self.paths,
                'ID.new',
                'ID']

    def _build_ctags_vi(self):
        res = [['ctags-exuberant', 'ctags', 'ctags.exe'],
               ['-R', '-f', 'tags.new'] + self.paths,
                'tags.new',
                'tags']
        if self.languages:
            res[1][0:0] = ['--languages=%s' % self.languages]
            res[1][0:0] = ['--langmap=%s' % self.langmap]
        return res

    def _build_ctags_emacs(self):
        res = self._build_ctags_vi()
        res[1][0:0] = ['-e']
        res[3] = 'TAGS'
        return res

    def _build_ctags_bbedit(self):
        res = self._build_ctags_vi()
        res[1][0:0] = [
            '--excmd=number', '--tag-relative=no', '--fields=+a+m+n+S']
        return res

def ctags(args = sys.argv):
    try:
        path = os.path.abspath(args.pop(0))
    except IndexError:
        raise ValueError("Must call ctags with path as initial argument")
    parser = optparse.OptionParser()
    parser.add_option('-l', '--languages', dest='languages',
                      default='Python,JavaScript,HTML',
                      help='ctags comma-separated list of languages. '
                      'defaults to ``Python,JavaScript,HTML``')
    parser.add_option('-e', '--ctags-emacs', action='append_const',
                      const=('ctags_emacs',),
                      help='flag to build emacs ctags ``TAGS`` file')
    parser.add_option('-v', '--ctags-vi',  action='append_const',
                      const=('ctags_vi',),
                      help='flag to build vi ctags ``tags`` file')
    parser.add_option('-b', '--ctags-bbedit', action='append_const',
                      const=('ctags_bbedit',),
                      help='flag to build bbedit ctags ``tags`` file')
    parser.add_option('-i', '--idutils', action='append_const',
                      const=('idutils',),
                      help='flag to build idutils ``ID`` file')
    parser.add_option('-m', '--langmap', dest='langmap',
                      default='html:+.pt',
                      help='ctags langmap see ctags options '
                      'defaults to ``html:+.pt`` for include page templates')
    options, args = parser.parse_args(args)
    if args:
        parser.error('no arguments accepted')
    targets = getattr(options, 'targets', None)
    if (targets and 'ctags_bbedit' in targets and 'ctags_vi' in targets):
        parser.error('cannot build both vi and bbedit ctags files (same name)')
    builder = Builder(path)
    builder(targets, options.languages, options.langmap)
