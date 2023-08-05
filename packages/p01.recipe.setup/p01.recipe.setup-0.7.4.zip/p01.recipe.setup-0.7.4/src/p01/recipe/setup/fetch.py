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
$Id: fetch.py 3629 2013-01-04 14:41:57Z roger.ineichen $
"""

import os.path
import logging
import os
import urllib2
import shutil
import tempfile
import urlparse
import setuptools.archive_util
from ConfigParser import ConfigParser
try:  
   from hashlib import md5 
except ImportError: 
   from md5 import new as md5

import zc.recipe.egg
import zc.buildout
from zc.buildout.download import Download

from p01.recipe.setup import LoggerMixin
from p01.recipe.setup import makeBoolString
from p01.recipe.setup import doChmod
from p01.recipe.setup import doChown
from p01.recipe.setup import TRUE_VALUES


initialization_template = """import os
sys.argv[0] = os.path.abspath(sys.argv[0])
"""

env_template = """os.environ['%s'] = %r
"""


class FetchScriptRecipe(LoggerMixin):
    """Creat a script which is able to download and extract an egg from pypi
    
    NOTE: this recipe will install a script and this could get used later.
    there is also p01.recipe.setup:donaload recipe which will download during 
    the buildout process.
    """

    def __init__(self, buildout, name, options):
        self.egg = None
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

        if not options.get('working-directory', ''):
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'], name)

        if 'eggs' not in self.options:
            self.options['eggs'] = ''
        self.options['eggs'] = self.options['eggs'] + '\n' + 'zc.buildout'
        self.options['eggs'] = self.options['eggs'] + '\n' + 'zc.recipe.egg'
        self.options['eggs'] = self.options['eggs'] + '\n' + 'p01.recipe.setup'
        self.egg = zc.recipe.egg.Egg(buildout, name, self.options)

    def install(self):
        dest = []
        options = self.options
        executable = self.buildout['buildout']['executable']
        url =  '"%s"' % options['url']
        target = '"%s"' % options['target'].replace('\\', '\\\\')
        stripTopLevel = makeBoolString(options.get('strip-top-level-dir'), False)
        stripSubDirs = '"%s"' % options.get('extract-sub-dir', None)
        ignoreExisting = makeBoolString(options.get('ignore-existing'), False)
        overrideExisting = makeBoolString(options.get('override-existing'), False)
        downloadOnly = makeBoolString(options.get('download-only'), False)
        filename =  '"%s"' % options.get('filename', '').strip()
        if options.get('md5sum'):
            md5sum =  '"%s"' % options['md5sum']
        else:
            md5sum =  'None'
        mode = '%s' % self.mode
        owner = '"%s"' % self.owner and self.owner or 'None'

        # validate (note, we have bool strings)
        if ignoreExisting == 'True' and overrideExisting == 'True':
            raise zc.buildout.UserError(
                "Can't set ignoreExisting and overrideExisting")

        # setup egg path
        # setup additional egg path
        if self.egg:
            extra_paths = self.egg.extra_paths
            eggs, ws = self.egg.working_set()
        else:
            extra_paths = ()
            ws = []

        # setup environment
        initialization = initialization_template
        env_section = self.options.get('environment', '').strip()
        if env_section:
            env = self.buildout[env_section]
            for key, value in env.items():
                initialization += env_template % (key, value)

        # setup checker script
        arguments = [url, md5sum, target, stripTopLevel, stripSubDirs,
            ignoreExisting, overrideExisting, downloadOnly, filename, mode,
            owner]
        dest.extend(zc.buildout.easy_install.scripts(
            [(self.name, 'p01.recipe.setup.fetch', 'process')],
            ws, executable, self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = ', '.join(arguments),
            initialization = initialization,
            ))

        return dest

    update = install



###############################################################################
#
# download scripts
#
###############################################################################


def calculateBase(extractDir, stripTopLevel, stripSubDirs):
    """Calculate base"""
    top_level_contents = os.listdir(extractDir)
    top_level_dir = None
    if len(top_level_contents) == 1:
        top_level_dir = top_level_contents[0]

    # extract nested top level directory
    if stripTopLevel:
        if top_level_dir is None:
            print ('Unable to strip top level directory because there are '
                   'more than one element in the root of the package.')
            raise TypeError('Invalid package contents')
        base = os.path.join(extractDir, top_level_dir)

    # extract sub directory
    elif stripSubDirs:
        subdirs = stripSubDirs
        if top_level_dir is None:
            base = os.path.join(extractDir, subdirs)
        else:
            base = os.path.join(extractDir, top_level_dir, subdirs)
        if not os.path.exists(base):
            msg = 'extract-sub-dir %s was not found in %s' % (subdirs, base)
            raise ValueError(msg)

    # extract the source 
    else:
        base = extractDir
    return base


# pypi auth (mypypi)
def getPYPIRCAuth(pypiURL):
    """Returns the relevant username and password for a given pypiURL."""

    rc = os.path.join(os.path.expanduser('~'), '.pypirc')
    if os.path.exists(rc):
        realm = 'pypi'
        username = None
        password = None

        config = ConfigParser()
        config.read(rc)
        sections = config.sections()
        if 'distutils' in sections:
            # let's get the list of servers
            index_servers = config.get('distutils', 'index-servers')
            _servers = [server.strip() for server in index_servers.split('\n')
                        if server.strip() != '']
            for server in _servers:
                repos = config.get(server, 'repository')
                if pypiURL.startswith(server) or pypiURL.startswith(repos):
                    un = config.get(server, 'username')
                    pw = config.get(server, 'password')
                    if un and pw:
                        username= un
                        password = pw
                        if config.has_option(server, 'realm'):
                            realm = config.get(server, 'realm')
                        break

        if not username and not password and 'server-login' in sections:
            # old format
            server = 'server-login'
            username  = config.get(server, 'username')
            password = config.get(server, 'password')

    return realm, username, password


def urlOpener(pypiURL):
    """Open url including auth"""
    realm, username, password = getPYPIRCAuth(pypiURL)
    if username is not None and password is not None:
        hpm = urllib2.HTTPPasswordMgr()
        hpm.add_password(realm, pypiURL, username, password)
        auth = urllib2.HTTPBasicAuthHandler(hpm)
        opener = urllib2.build_opener(auth)
    else:
        opener = urllib2.build_opener()

    request = urllib2.Request(pypiURL)
    return opener.open(request)


def checkMD5(path, md5sum):
    """Tell whether the MD5 checksum of the file at path matches.

    No checksum being given is considered as good.

    """
    if md5sum is None:
        return True

    f = open(path, 'rb')
    checksum = md5()
    try:
        chunk = f.read(2**16)
        while chunk:
            checksum.update(chunk)
            chunk = f.read(2**16)
        return checksum.hexdigest() == md5sum
    finally:
        f.close()


class DownloadError(Exception):
    """Donwload error"""
    pass


def downloadPackage(url, md5sum, filename):
    """Fetches a release file (egg) and check md5 checksum if given."""
    try:
        data = urlOpener(url).read()
    except urllib2.HTTPError, v:
        if '404' in str(v):
            raise DownloadError("404: %s" % url)
        elif '404' in str(v):
            raise DownloadError("401: %s" % url)
        raise DownloadError(
            "Couldn't download (HTTP Error): %s" % url)
    except urllib2.URLError, v:
        raise DownloadError("URL Error: %s " % url)
    except:
        raise DownloadError(
            "Couldn't download (unknown reason): %s" % url)
    if md5sum:
        # check for md5 checksum
        data_md5 = md5(data).hexdigest()
        if md5sum != data_md5:
            raise DownloadError(
                "MD5 sum does not match: %s / %s for release file %s" % (
                    md5sum, data_md5, url))

    # write data to file
    tmpDir = tempfile.mkdtemp('fetch')
    tmpPath =   os.path.join(tmpDir, filename)
    f = open(tmpPath, 'wb')
    f.write(data)
    f.close()

    return tmpPath


def process(url, md5sum, target, stripTopLevel, stripSubDirs, ignoreExisting,
    overrideExisting, downloadOnly, filename, mode=None, owner=None):
    """Process download, extract"""

    if not filename:
        # Use the original filename of the downloaded file 
        # regardless whether download filename hashing is enabled.
        filename = os.path.basename(urlparse.urlparse(url)[2])

    # download from pypi
    path = downloadPackage(url, md5sum, filename)

    try:
        # create target directory
        if not os.path.isdir(target):
            os.makedirs(target)

        if downloadOnly:
            # copy the file to target without extraction
            target_path = os.path.join(target, filename)
            shutil.copy(path, target_path)
        else:
            # Extract the package
            extractDir = tempfile.mkdtemp("buildout-" + filename)
            try:
                setuptools.archive_util.unpack_archive(path, extractDir)
            except setuptools.archive_util.UnrecognizedFormat:
                print 'Unable to extract the package %s. Unknown format.' % path
                raise zc.buildout.UserError('Package extraction error')
            base = calculateBase(extractDir, stripTopLevel, stripSubDirs)
            print 'extracting package to %s' % target
            for filename in os.listdir(base):
                source = os.path.join(base, filename)
                dest = os.path.join(target, filename)
                if os.path.exists(dest):
                    if ignoreExisting:
                        print 'ignoring existing target: %s' % dest
                    elif overrideExisting:
                        print 'override existing target: %s' % dest
                        if os.path.isfile(source):
                            # skip folders
                            data = open(source, 'rb').read()
                            out = open(dest, 'wb')
                            out.write(data)
                            out.close()
                    else:
                        print ('target %s already exists. Either remove '
                               'it or set ``ignore-existing = true`` '
                               'in your buildout.cfg to ignore existing '
                               'files and directories.' % dest)
                        raise ValueError('File or directory already exists.')
                else:
                    # we do not copy, we just move because our base is the
                    # extract dir
                    shutil.move(source, dest)

            # remove extract dir
            shutil.rmtree(extractDir)

    finally:
        os.unlink(path)

    if dest is not None and os.path.exists(dest):
        # set mode
        doChmod(dest, mode)
        # set owner if given
        doChown(dest, owner)
