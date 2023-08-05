# make a package

import os
import sys
import logging

import zc.buildout

TRUE_VALUES = ('yes', 'true', 'True', '1', 'on')
FALSE_VALUES = ('no', 'false', 'False', '0', 'off')


def makeBoolString(v, default):
    if v in ['True', 'true', 'on', '1']:
        return 'True'
    elif v in ['False', 'false', 'off', '0']:
        return 'False'
    else:
        return '%s' % default


def doChmod(filename, mode, logger=None):
    if not filename or not mode:
        return
    os.chmod(filename, mode)
    if logger is not None:
        msg = "Change mode %s for %s" % (mode, filename)
        logger.info(msg)


def doChown(path, owner, logger=None):
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
        if logger is not None:
            logger.info(msg)
        return

    # buildout script runner must be root
    if os.getuid() != 0:
        if logger is not None:
            msg = 'Only root can change the owner to %s.' % owner
            logger.info(msg)
        raise zc.buildout.UserError(msg)

    uid = None
    try:
        import pwd
        uid = pwd.getpwnam(owner)[2]
        uid = int(uid)
        os.chown(path, uid, -1)
        if logger is not None:
            msg = 'Changed owner for %s to %s!' % (path, owner)
            logger.info(msg)
    except KeyError:
        if logger is not None:
            msg = 'The user %s does not exist.' % owner
            logger.error(msg)
        raise zc.buildout.UserError(msg)


def doCreatePaths(path,  remember=False, options=None, logger=None):
    parent = os.path.dirname(path)
    if os.path.exists(path) or parent == path:
        return
    doCreatePaths(parent, remember)
    if logger is not None:
        msg = 'Create path %s' % path
        logger.error(msg)
    os.mkdir(path)
    if remember and options is not None:
        options.created(path)


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
        doChown(path, owner, self.logger)


class CHMODMixin(LoggerMixin):
    """chmode support."""

    def doChmod(self, filename, mode):
        doChmod(filename, mode, self.logger)


class CreatePathMixin(LoggerMixin):
    """Create missing folders based on given path.

    If remember is set (default) each new folder get added to the file list
    using the buildout created method.
    """

    def doCreatePaths(self, path,  remember=True):
        doCreatePaths(path,  remember=remember, options=self.options,
            logger=self.logger)
