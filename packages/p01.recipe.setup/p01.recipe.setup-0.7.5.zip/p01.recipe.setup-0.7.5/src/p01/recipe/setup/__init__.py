# make a package

import os
import os.path
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


def doChmod(path, mode, logger=None):
    if not path or not mode:
        return

    if not os.path.exists(path):
        if logger is not None:
            msg = 'Path %s does not exist for os.chmod' % path
            logger.info(msg)
        raise zc.buildout.UserError(msg)

    os.chmod(path, mode)
    msg = "Change mode %s for %s" % (mode, path)
    if logger is not None:
        logger.info(msg)
    else:
        print msg


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

    if not os.path.exists(path):
        msg = 'Path %s does not exist for os.chown' % path
        if logger is not None:
            logger.info(msg)
        raise zc.buildout.UserError(msg)

    parts = owner.split(':')
    parts = parts + [None][:2]
    user = parts[0] or None
    group = parts[1] or None

    # determine user id
    uid = -1
    if user:
        try:
            import pwd
            uid = pwd.getpwnam(user)[2]
        except ImportError:
            logger.warn(
                "System does not support `pwd`. Using default user")
        except KeyError:
            msg = 'The user %s does not exist.' % user
            if logger is not None:
                logger.error(msg)
            raise zc.buildout.UserError(msg)

    # determine group id
    gid = -1
    if group:
        try:
            import grp
            gid = grp.getgrnam(group)[2]
        except ImportError:
            logger.warn(
                "System does not support `grp`. Using default group")
        except KeyError:
            msg = 'The group %s does not exist.' % group
            if logger is not None:
                logger.error(msg)
            raise zc.buildout.UserError(msg)

    uid = int(uid)
    gid = int(gid)
    os.chown(path, uid, gid)
    msg = 'Changed owner for %s to %s:%s' % (path, user, group)
    if logger is not None:
        logger.info(msg)
    else:
        print msg


def doCreatePaths(path,  remember=False, options=None, logger=None):
    parent = os.path.dirname(path)
    if os.path.exists(path) or parent == path:
        return
    doCreatePaths(parent, remember)
    
    os.mkdir(path)
    msg = 'Create path %s' % path
    if logger is not None:
        logger.error(msg)
    else:
        print msg

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
