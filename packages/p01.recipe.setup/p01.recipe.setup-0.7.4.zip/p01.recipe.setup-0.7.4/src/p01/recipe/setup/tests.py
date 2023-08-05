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
    zc.buildout.testing.install('ZConfig', test)
    zc.buildout.testing.install_develop('p01.recipe.setup', test)
    zc.buildout.testing.install_develop('zc.recipe.egg', test)
    zc.buildout.testing.install_develop('supervisor', test)
    zc.buildout.testing.install_develop('superlance', test)
    zc.buildout.testing.install_develop('meld3', test)


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
