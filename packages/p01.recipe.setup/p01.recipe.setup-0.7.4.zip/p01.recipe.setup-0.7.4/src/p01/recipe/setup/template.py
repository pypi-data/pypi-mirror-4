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
import stat
import zc.buildout

from p01.recipe.setup import CHMODMixin
from p01.recipe.setup import CHOWNMixin
from p01.recipe.setup import CreatePathMixin


class TemplateRecipe(CHMODMixin, CHOWNMixin, CreatePathMixin):
    """Recipe for write template based configuration files and scripts.
    
    Note, this recipe does only touch the tempalte source during install method
    call. This allows that other reicpe can create the template source e.g.
    download a package as which contains the template source etc.
    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.options = options
        self.name = name

        if "source" not in options and "content" not in options:
            self.logger.error("No source file template or content specified.")
            raise zc.buildout.UserError(
                "No template file or content specified.")

        if "target" not in options:
            self.logger.error("No target file specified.")
            raise zc.buildout.UserError("No target file specified.")

        self.target = options["target"]
        self.source = options.get("source")
        self.content = options.get("content")

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

    def install(self):
        if self.content:
            source = self.content
        elif os.path.isfile(self.source):
            source = open(self.source).read()
        else:
            msg = "Source file does not exist and no content is given."
            self.logger.error(msg) 
            raise zc.buildout.UserError(msg)

        # replace variable with options
        template = re.sub(r"\$\{([^:]+?)\}", r"${%s:\1}" % self.name, source)
        self.result = self.options._sub(template, [])

        self.doCreatePaths(os.path.dirname(self.target))
        target=open(self.target, "wt")
        target.write(self.result)
        target.close()

        # set mode if given
        self.doChmod(self.target, self.mode)

        # set owner if given
        self.doChown(self.target, self.owner)

        return self.options.created()

    # variables in other parts might have changed so we need to do a
    # full reinstall.
    update = install
