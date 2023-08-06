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
import re
import shutil
import unittest
import doctest
from zope.testing import renormalizing

import zc.buildout.testing


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('p01.recipe.setup', test)
    zc.buildout.testing.install('ZConfig', test)
    zc.buildout.testing.install('ZODB3', test)
    zc.buildout.testing.install('BTrees', test)
    zc.buildout.testing.install('meld3', test)
    zc.buildout.testing.install('persistent', test)
    zc.buildout.testing.install('superlance', test)
    zc.buildout.testing.install('supervisor', test)
    zc.buildout.testing.install('zc.recipe.egg', test)
    zc.buildout.testing.install('zope.app.applicationcontrol', test)
    zc.buildout.testing.install('zope.app.appsetup', test)
    zc.buildout.testing.install('zope.app.locales', test)
    zc.buildout.testing.install('zope.i18nmessageid', test)
    zc.buildout.testing.install('zope.interface', test)
    zc.buildout.testing.install('zope.session', test)
    zc.buildout.testing.install('zope.site', test)
    zc.buildout.testing.install('zc.lockfile', test)
    zc.buildout.testing.install('pytz', test)
    zc.buildout.testing.install('zope.security', test)
    zc.buildout.testing.install('zope.processlifetime', test)
    zc.buildout.testing.install('zope.error', test)
    zc.buildout.testing.install('zope.container', test)
    zc.buildout.testing.install('zope.size', test)
    zc.buildout.testing.install('zope.i18n', test)
    zc.buildout.testing.install('zope.applicationcontrol', test)
    zc.buildout.testing.install('zope.location', test)
    zc.buildout.testing.install('zope.publisher', test)
    zc.buildout.testing.install('zope.proxy', test)
    zc.buildout.testing.install('zope.exceptions', test)
    zc.buildout.testing.install('zope.broken', test)
    zc.buildout.testing.install('zope.dottedname', test)
    zc.buildout.testing.install('zope.browser', test)
    zc.buildout.testing.install('zope.contenttype', test)
    zc.buildout.testing.install('zope.authentication', test)
    zc.buildout.testing.install('zdaemon', test)
    zc.buildout.testing.install('zope.filerepresentation', test)
    zc.buildout.testing.install('transaction', test)
    zc.buildout.testing.install('zope.lifecycleevent', test)
    zc.buildout.testing.install('zope.annotation', test)
    zc.buildout.testing.install('zope.minmax', test)
    zc.buildout.testing.install('zope.schema', test)
    zc.buildout.testing.install('six', test)
    zc.buildout.testing.install('zope.configuration', test)
    zc.buildout.testing.install('zope.app.publication', test)
    zc.buildout.testing.install('zope.component', test)
    zc.buildout.testing.install('zope.event', test)
    zc.buildout.testing.install('zope.tal', test)
    zc.buildout.testing.install('zope.traversing', test)


def empty_download_cache(path):
    """Helper function to clear the download cache directory."""
    for element in (os.path.join(path, filename) for filename in os.listdir(path)):
        if os.path.isdir(element):
            shutil.rmtree(element)
        else:
            os.unlink(element)


checker = renormalizing.RENormalizing([
    zc.buildout.testing.normalize_path,
    zc.buildout.testing.normalize_script,
    (re.compile("\r\n"), '\n'),
    (re.compile(
    "Couldn't find index page for '[a-zA-Z0-9.()\?]+' "
    "\(maybe misspelled\?\)"
    "\n"
    ), ''),
    (re.compile("Not found: [a-zA-Z0-9_.:\/\\\]+"), ''),
    (re.compile("Generated script '/sample-buildout/bin/buildout'."), ''),
    (re.compile(r'http://localhost:\d+'), 'http://test.server'),
    # Use a static MD5 sum for the tests
    (re.compile(r'[a-f0-9]{32}'), 'dfb1e3136ba092f200be0f9c57cf62ec'),
    # START support plain "#!/bin/bash"
    (re.compile('#!/bin/bash'), '#@/bin/bash'),
    (re.compile('#![^\n]+\n'), ''),
    (re.compile('#@/bin/bash'), '#!/bin/bash'),
    # END support plain "#!/bin/bash"
    (re.compile('-\S+-py\d[.]\d(-\S+)?.egg'), '-pyN.N.egg'),
    # only windows have this
    (re.compile('-  .*\.exe\n'), ''),
    (re.compile('-script.py'), ''),
    # workarround if buildout is upgrading
    (re.compile('Upgraded:'), ''),
    (re.compile('  zc.buildout version 1.4.3;'), ''),
    (re.compile('restarting.'), ''),
    zc.buildout.testing.normalize_path,
    zc.buildout.testing.normalize_script,
    zc.buildout.testing.normalize_egg_py,
    ])


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('checker.txt'),
        doctest.DocFileSuite('cmd.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('copy.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('download.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            globs = {'empty_download_cache': empty_download_cache},
            checker=checker),
        doctest.DocFileSuite('i18n.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('importchecker.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('mkdir.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('mkfile.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('paste.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('script.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('supervisor.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('template.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
