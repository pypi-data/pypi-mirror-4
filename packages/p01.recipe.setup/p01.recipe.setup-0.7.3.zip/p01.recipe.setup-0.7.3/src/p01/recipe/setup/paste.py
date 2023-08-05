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
"""Paste deploy recipes for Zope3 apps

$Id:$
"""

import re
import os
import cStringIO
import ZConfig.schemaless
import zc.buildout
import zc.recipe.egg


class PasteServeSetup:
    """Paste serve setup script without checking zodb part in conf section"""

    def __init__(self, buildout, name, options):
        self.egg = None
        self.buildout = buildout
        self.name = name
        self.options = options
        options['script'] = os.path.join(buildout['buildout']['bin-directory'],
                                         options.get('script', self.name),
                                         )
        # allows to install more then one setup in one parts folder, if not
        # given use script name
        # TODO: Does the newest buildout use a working-directory option?
        #       If so, can we skip them and support our own location given from
        #       parts option?
        self.parts = options.get('parts', self.name)
        if self.parts == self.name:
            self.prefix = ''
        else:
            # use script name as prefix if the location is not the real
            # script parts location
            self.prefix = '%s-' % self.name
        if not options.get('working-directory', ''):
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'], self.parts)

        if options.get('eggs') is None:
            raise zc.buildout.UserError(
                'You have to define at least one egg for setup an application.')
        self.egg = zc.recipe.egg.Egg(buildout, name, options)

    _template_split = re.compile('([@]{[^}]*})').split
    _simple = re.compile('[-a-zA-Z0-9 ._]+$').match
    _valid = re.compile('\@{[-a-zA-Z0-9 ._]+}$').match
    def _sub(self, template, seen):
        value = self._template_split(template)
        subs = []
        for ref in value[1::2]:
            s = tuple(ref[2:-1].split(':'))
            if not self._valid(ref):
                if len(s) < 2:
                    raise zc.buildout.UserError("The substitution, %s,\n"
                                                "doesn't contain a colon."
                                                % ref)
                if len(s) > 2:
                    raise zc.buildout.UserError("The substitution, %s,\n"
                                                "has too many colons."
                                                % ref)
                if not self._simple(s[0]):
                    raise zc.buildout.UserError(
                        "The section name in substitution, %s,\n"
                        "has invalid characters."
                        % ref)
                if not self._simple(s[1]):
                    raise zc.buildout.UserError(
                        "The options name in substitution, %s,\n"
                        "has invalid characters."
                        % ref)

            v = self.options.get(s[1], None, seen)
            if v is None:
                raise zc.buildout.UserError(
                    "Referenced options does not exist in %s:" % self.name, *s)
            subs.append(v)
        subs.append('')
        return ''.join([''.join(v) for v in zip(value[::2], subs)])

    def install(self):
        options = self.options
        location = options['location']
        executable = self.buildout['buildout']['executable']

        # setup path
        dest = []
        if not os.path.exists(location):
            os.mkdir(location)
            dest.append(location)

        # setup config paths
        event_log_path = os.path.join(location, '%serror.log' % self.prefix)
        site_zcml_path = os.path.join(location, '%ssite.zcml' % self.prefix)
        zope_conf_path = os.path.join(location, '%szope.conf' % self.prefix)
        paste_ini_path = os.path.join(location, '%spaste.ini' % self.prefix)

        # append file to dest which will remove it on update
        dest.append(site_zcml_path)
        dest.append(zope_conf_path)
        dest.append(paste_ini_path)

        # setup *-site.zcml
        zcml = site_zcml_template % self.options['zcml']
        # replace options with variables
        zcml = zcml.lstrip()
        template = re.sub(r"\@\{([^:]+?)\}", r"@{options:\1}", zcml)
        zcml = self._sub(template, [])
        open(site_zcml_path, 'w').write(zcml)

        # setup *-paste.ini file
        ini = options.get('ini', '')+'\n'
        ini = ini.lstrip()
        # replace options with variables
        template = re.sub(r"\@\{([^:]+?)\}", r"@{options:\1}", ini)
        ini = self._sub(template, [])
        open(paste_ini_path, 'w').write(str(ini))

        # setup *-zope.conf
        conf = options.get('conf', '')+'\n'
        # replace options with variables
        conf = conf.lstrip()
        template = re.sub(r"\@\{([^:]+?)\}", r"@{options:\1}", conf)
        conf = self._sub(template, [])
        # load ZConfig
        conf = ZConfig.schemaless.loadConfigFile(cStringIO.StringIO(conf))
        conf['site-definition'] = [site_zcml_path]
        if not [s for s in conf.sections if s.type == 'eventlog']:
            conf.sections.append(event_log(event_log_path))
        open(zope_conf_path, 'w').write(str(conf))

        # setup paster script
        if self.egg is not None:
            extra_paths = self.egg.extra_paths
        else:
            extra_paths = []

        # populate working set
        eggs, ws = self.egg.working_set()

        # setup arguments
        defaults = options.get('defaults', '').strip()
        if defaults:
            defaults = '(%s) + ' % defaults
        arguments = defaults + (arg_template % dict(INI_PATH=paste_ini_path,))

        # setup environment
        initialization = initialization_template
        env_section = options.get('environment', '').strip()
        if env_section:
            env = self.buildout[env_section]
            for key, value in env.items():
                initialization += env_template % (key, value)

        dest.extend(zc.buildout.easy_install.scripts(
            [('%s'% self.name, 'paste.script.command', 'run')],
            ws, self.options['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = arguments,
            initialization = initialization
            ))

        return dest

    update = install


# setup helper
arg_template = """[
  'serve', %(INI_PATH)r,
  ]+sys.argv[1:]"""


site_zcml_template = """\
<configure
    xmlns="http://namespaces.zope.org/zope">
%s
</configure>
"""


initialization_template = """import os
sys.argv[0] = os.path.abspath(sys.argv[0])
"""


env_template = """os.environ['%s'] = %r
"""


def event_log(path, *data):
    return ZConfig.schemaless.Section(
        'eventlog', '', None,
        [ZConfig.schemaless.Section(
             'logfile',
             '',
             dict(path=[path])),
         ])
