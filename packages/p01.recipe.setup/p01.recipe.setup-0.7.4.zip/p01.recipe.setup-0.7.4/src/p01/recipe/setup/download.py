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

import os.path
import setuptools.archive_util
import shutil
import tempfile
import urlparse
import zc.buildout

from zc.buildout.download import Download

from p01.recipe.setup import CHMODMixin
from p01.recipe.setup import CHOWNMixin
from p01.recipe.setup import LoggerMixin
from p01.recipe.setup import TRUE_VALUES


class DownloadRecipe(CHMODMixin, CHOWNMixin, LoggerMixin):
    """Recipe for downloading packages from the net and extracting them on
    the filesystem.
    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.options = options
        self.name = name
        buildout['buildout'].setdefault(
            'download-cache',
            os.path.join(buildout['buildout']['directory'], 'downloads'))
        # mode
        self.mode = options.get('mode', None)
        if self.mode is not None:
            try:
                self.mode = int(self.mode, 8)
            except ValueError:
                raise zc.buildout.UserError(
                    "'mode' must be an octal number: " % self.mode)
        # owner
        self.owner = options.get('owner')

        options.setdefault('destination', os.path.join(
                buildout['buildout']['parts-directory'],
                self.name))
        options['location'] = options['destination']
        options.setdefault('strip-top-level-dir', 'false')
        options.setdefault('ignore-existing', 'false')
        options.setdefault('override-existing', 'false')
        options.setdefault('download-only', 'false')
        options['filename'] = options.get('filename', '').strip()

    def calculate_base(self, extract_dir):
        """Recipe authors inheriting from this recipe can override this method
        to set a different base directory.
        """
        # Move the contents of the package in to the correct destination
        top_level_contents = os.listdir(extract_dir)
        top_level_dir = None
        if len(top_level_contents) == 1:
            top_level_dir = top_level_contents[0]

        # extract nested top level directory
        if self.options['strip-top-level-dir'].lower() in TRUE_VALUES:
            if top_level_dir is None:
                self.logger.error(
                    'Unable to strip top level directory because there are '
                    'more than one element in the root of the package.')
                raise zc.buildout.UserError('Invalid package contents')
            base = os.path.join(extract_dir, top_level_dir)

        # extract sub directory
        elif self.options.get('extract-sub-dir'):
            subdirs = self.options['extract-sub-dir']
            if top_level_dir is None:
                base = os.path.join(extract_dir, subdirs)
            else:
                base = os.path.join(extract_dir, top_level_dir, subdirs)
            if not os.path.exists(base):
                msg = 'extract-sub-dir %s was not found in %s' % (subdirs, base)
                self.logger.error(msg)
                raise zc.buildout.UserError(msg)

        # extract the source 
        else:
            base = extract_dir
        return base

    def install(self):
        if not os.path.exists(self.buildout['buildout']['download-cache']):
            os.makedirs(self.buildout['buildout']['download-cache'])

        destination = self.options.get('destination')
        download = Download(self.buildout['buildout'])
        path, is_temp = download(self.options['url'], md5sum=self.options.get(
            'md5sum'))

        dest = None
        parts = []
        try:
            # Create destination directory
            if not os.path.isdir(destination):
                os.makedirs(destination)
                parts.append(destination)

            download_only = self.options['download-only'].strip().lower() in \
                TRUE_VALUES
            if download_only:
                if self.options['filename']:
                    # Use an explicit filename from the section configuration
                    filename = self.options['filename']
                else:
                    # Use the original filename of the downloaded file 
                    # regardless whether download filename hashing is enabled.
                    filename = os.path.basename(urlparse.urlparse(
                        self.options['url'])[2])

                # Copy the file to destination without extraction
                target_path = os.path.join(destination, filename)
                shutil.copy(path, target_path)
                if not destination in parts:
                    parts.append(target_path)
            else:
                # Extract the package
                extract_dir = tempfile.mkdtemp("buildout-" + self.name)
                try:
                    setuptools.archive_util.unpack_archive(path, extract_dir)
                except setuptools.archive_util.UnrecognizedFormat:
                    self.logger.error(
                        'Unable to extract the package %s. Unknown format.',
                        path)
                    raise zc.buildout.UserError('Package extraction error')

                base = self.calculate_base(extract_dir)

                self.logger.info('Extracting package to %s' % destination)

                ignore_existing = self.options['ignore-existing'].strip().lower(
                    ) in TRUE_VALUES
                override_existing = self.options['override-existing'].strip().lower(
                    ) in TRUE_VALUES

                # validate (note, we have bool strings)
                if ignore_existing and override_existing:
                    raise zc.buildout.UserError(
                        "Can't set ignore-existing and override-existing")
                for filename in os.listdir(base):
                    source = os.path.join(base, filename)
                    dest = os.path.join(destination, filename)
                    if os.path.exists(dest):
                        if ignore_existing:
                            self.logger.info(
                                'Ignoring existing target: %s' % dest)
                        elif override_existing:
                            print 'Override existing target: %s' % dest
                            if os.path.isfile(source):
                                # only files, skip existing folders
                                data = open(source, 'rb').read()
                                out = open(dest, 'wb')
                                out.write(data)
                                out.close()
                        else:
                            self.logger.error('Target %s already exists. Either remove '
                                      'it or set ``ignore-existing = true`` '
                                      'in your buildout.cfg to ignore existing '
                                      'files and directories.', dest)
                            raise zc.buildout.UserError(
                                'File or directory already exists.')
                    else:
                        # Only add the file/directory to the list of installed
                        # parts if it does not already exist. This way it does
                        # not get accidentally removed when uninstalling.
                        parts.append(dest)

                        # we do not copy, we just move because our base is the
                        # extract dir
                        shutil.move(source, dest)

                # remove extract dir
                shutil.rmtree(extract_dir)

        finally:
            if is_temp:
                os.unlink(path)

        if dest is not None and os.path.exists(dest):
            # set mode
            self.doChmod(dest, self.mode)
            # set owner if given
            self.doChown(dest, self.owner)

        return parts

    def update(self):
        # do not update, only use install if something has changed
        pass
