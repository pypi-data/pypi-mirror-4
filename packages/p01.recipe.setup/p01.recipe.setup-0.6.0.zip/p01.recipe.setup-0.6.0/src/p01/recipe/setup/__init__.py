# make a package

import os
import sys
import logging

import zc.buildout


class LoggerMixin(object):
    """Logging support."""

    _logger = None

    @property
    def logger(self):
        if self._logger is None:
            self._logger = logging.getLogger(self.name)
        return self._logger


class CHOWNMixin(LoggerMixin):
    """chown support method for linux ignored on windows with info message."""

    def doChown(self, path, owner):
        """Change owner on linux, ignored on windows with info message.
        
        This method will only change the owner if an owner and path is given.
        This your code is responsible for ensure an owner and path or the
        method will do nothing without a message.
        """
        if not owner or not path:
            return

        # log info message and return on windows
        if sys.platform == 'win32':
            msg = "Cannot set owner %s for %s on win32!" % (owner, path)
            self.logger.info(msg)
            return

        # buildout script runner must be root
        if os.getuid() != 0:
            msg = 'Only root can change the owner to %s.' % owner
            self.logger.error(msg)
            raise zc.buildout.UserError(msg)

        uid = None
        try:
            import pwd
            uid = pwd.getpwnam(owner)[2]
            uid = int(uid)
            os.chown(path, uid, -1)
            msg = 'Changed owner for %s to %s!' % (path, owner)
            self.logger.info(msg)
        except KeyError:
            msg = 'The user %s does not exist.' % owner
            self.logger.error(msg)
            raise zc.buildout.UserError(msg)


class CHMODMixin(LoggerMixin):
    """chmode support."""

    def doChmod(self, filename, mode):
        if not filename or not mode:
            return
        os.chmod(filename, self.mode)
        msg = "Change mode %s for %s" % (mode, filename)
        self.logger.info(msg)


class CreatePathMixin(LoggerMixin):
    """Create missing folders based on given path.

    If remember is set (default) each new folder get added to the file list
    using the buildout created method.
    """

    def doCreatePaths(self, path,  remember=True):
        parent = os.path.dirname(path)
        if os.path.exists(path) or parent == path:
            return
        self.doCreatePaths(parent, remember)
        os.mkdir(path)
        if remember is True:
            self.options.created(path)


