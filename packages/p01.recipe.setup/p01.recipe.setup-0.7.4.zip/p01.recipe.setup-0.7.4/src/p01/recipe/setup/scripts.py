##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
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
"""Calls scripts located in buildout bin directory by the given script names

$Id: scripts.py 3091 2012-09-12 01:50:19Z roger.ineichen $
"""

import sys
import os.path
import optparse
import subprocess


def run(options):
    for name in options.names:
        # run the script
        path = os.path.join(options.directory, name)
        subprocess.call("%s" % path)


def get_options(args=None):
    if args is None:
        args = sys.argv
    original_args = args
    parser = optparse.OptionParser("%prog [options] output")
    options, positional = parser.parse_args(args)
    options.original_args = original_args
    if not positional or len(positional) < 2:
        parser.error("No directory and script names")
    options.directory = positional[0]
    options.names = positional[1]
    return options


def main(args=None):
    options = get_options(args)
    try:
        run(options)
    except Exception, err:
        print err
        sys.exit(1)
    sys.exit(0)
