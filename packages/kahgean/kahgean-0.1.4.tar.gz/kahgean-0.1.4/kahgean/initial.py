# Copyright (C) 2012 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license

"""\
kahgean.initial
===============

Functions from the ``kahgean.initial`` modules should be call as soon as
possible before doing any meaningful processing.
"""

import os
import sys
try:
    import resource, grp, pwd
except ImportError:
    resource = grp = pwd = None
import signal

__all__ = ['SCRIPT_NAME', 'SCRIPT_PATH', 'INTERPRETER',
           'change_group', 'change_user', 'change_rlimit_nofile',
           'change_workdir', 'change_umask']


SCRIPT_NAME = os.path.basename(sys.argv[0])
SCRIPT_PATH = os.path.dirname(sys.argv[0]) or os.getcwd()
INTERPRETER = sys.executable or 'python'


def change_group(groupname):
    """change the group"""
    if not grp or not groupname: return
    os.setgid(grp.getgrnam(groupname).gr_gid)


def change_user(username):
    """change the user"""
    if not pwd or not username: return
    os.setuid(pwd.getpwnam(username).pw_uid)


def change_rlimit_nofile(limit):
    """change the maximum number of open file descriptors for the
    current process."""
    if not resource or not limit: return
    resource.setrlimit(resource.RLIMIT_NOFILE, (limit, limit))


def change_workdir(workdir):
    if not workdir: return
    os.chdir(workdir)


def change_umask(umask):
    if umask is None: return
    os.umask(umask)


def append_options(options):
    """work with ``kahgean.options``, append arguments to the given
    ``Options`` object"""
    options.add_option('--user', default=None,
                       help='name of the user to run %(prog)s as')
    options.add_option('--group', default=None,
                       help='name of the group to run %(prog)s as')
    options.add_option('--rlimit-nofile', default=None, type=int,
                       help='maximum number of open file descriptors')
    options.add_option('--workdir', default=None,
                       help='change current directory to')
    options.add_option('--umask', type=int, default=None,
                       help='umask of the %(prog)s process(es)')


def _sys_exit(*args):
    sys.exit()


def deal_with_options(options):
    """work with ``append_options()``, deal with the parsing result of
    the ``options`` object"""
    change_rlimit_nofile(options.get('rlimit-nofile'))
    change_group(options.get('group'))
    change_user(options.get('user'))
    change_workdir(options.get('workdir'))
    change_umask(options.get('umask'))
    for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGQUIT,
                signal.SIGHUP, signal.SIGABRT]:
        signal.signal(sig, _sys_exit)
