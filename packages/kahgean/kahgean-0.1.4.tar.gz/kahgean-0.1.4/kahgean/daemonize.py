# Copyright (C) 2012 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license

"""\
kahgean.daemonize
=================

This module help developers make a program can be run as a daemon. For more
information, please visit http://code.activestate.com/recipes/278731/ .
"""

import logging
logger = logging.getLogger('daemonkit')

import os
import sys
import signal
import errno
import atexit
import warnings

__all__ = ['daemonize']


def _daemonize():
    """detach a process from the shell and run it as a daemon"""
    # fork the first child process
    try:
        pid = os.fork()
    except OSError, e:
        logger.critical('fail to fork the first child')
        sys.exit(1)
    if pid:
        # exit parent of the first child
        os._exit(0)
    else:
        # the first child
        os.setsid()
        # fork the second child
        try:
            pid = os.fork()
        except OSError, e:
            logger.critical('fail to fork the second child')
            sys.exit(1)
        if pid:
            # exit the first child
            os._exit(0)


def _check_pidfile(pidfile):
    """check the pid-file"""
    if not pidfile or not os.path.exists(pidfile):
        return
    try:
        fp = open(pidfile)
        data = fp.read(32)
        fp.close()
    except:
        logger.critical('cannot open the pid-file')
        sys.exit(1)
    try:
        pid = int(data)
    except ValueError:
        logger.critical('data in the pid-file is not a pid')
        sys.exit(1)
    try:
        # kill -0 for check if the process exists
        os.kill(pid, 0)
    except OSError, e:
        if e.args[0] == errno.ESRCH:
            # not exists
            logger.info('remove the outdated pid-file')
            os.unlink(pidfile)
        else:
            logger.critical('fail to check status of the process')
            sys.exit(1)
    else:
        logger.critical('another process is running')
        sys.exit(1)


def _write_pidfile(pidfile):
    """write the process id to the pid-file"""
    if not pidfile: return
    try:
        with open(pidfile, 'w') as fp:
            fp.write(str(os.getpid()))
    except:
        logger.info('cannot write to the pid-file')
        sys.exit(1)
    if not os.path.exists(pidfile):
        logger.info('the pid-file "%s" lost' % pidfile)
        sys.exit(1)
    atexit.register(_remove_pidfile, pidfile)


def _remove_pidfile(pidfile):
    """remove the pid-file"""
    if pidfile and os.path.exists(pidfile):
        os.unlink(pidfile)


def daemonize(pidfile):
    """daemonize"""
    if hasattr(os, 'fork'):
        _check_pidfile(pidfile)
        _daemonize()
        _write_pidfile(pidfile)
    else:
        warnings.warn('Your platform does not support fork() so that '
                      'daemonizing has been skipped, the process will '
                      'run as normal.')


def append_options(options):
    """work with ``kahgean.options``, append arguments to the given
    ``Options`` object"""
    options.add_option('--daemon', type=bool, default=False,
                       help='should the %(prog)s run as a daemon')
    options.add_option('--pidfile', default=None,
                       help='filename of the pid-file, only take effect '
                            'when the %(prog)s run as a daemon')


def deal_with_options(options):
    """work with ``append_options()``, deal with the parsing result of
    the ``options`` object"""
    if options.get('daemon'):
        pidfile = options.get('pidfile')
        daemonize(pidfile)
