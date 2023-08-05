# Copyright (C) 2012 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license

import os
import sys
import subprocess
import time
import xmlrpclib
import signal
from tempfile import NamedTemporaryFile
from nose.tools import *

script_name = 'simple_daemon.py'
script_path = os.path.join(os.path.dirname(__file__), script_name)
default_port = 38080
call_daemon = 'python "%s" --port %d --daemon on' % (script_path, default_port)
call_ps = 'ps aux | grep %s' % script_name


def _fecth_pid_via_ps():
    lines = subprocess.check_output(call_ps, shell=True)
    lines = lines.splitlines()
    info = ''
    for line in lines:
        if script_path in line:
            info = line
            break
    if not info:
        raise RuntimeError('cannot find process via ps')
    info = info.split()
    pid = int(info[1])
    sys.stderr.write('\npid of the test daemon is %d\n' % pid)
    return pid
    

def test_daemon_without_pidfile():
    subprocess.call(call_daemon, shell=True)
    time.sleep(.5)
    server = xmlrpclib.ServerProxy("http://localhost:%d/" % default_port)
    eq_(server.ping(), 'pong')
    pid = _fecth_pid_via_ps()
    eq_(server.getpid(), pid)
    os.kill(pid, signal.SIGTERM)
    time.sleep(.5)
    assert_raises(IOError, server.ping)


def test_daemon_with_pidfile():
    pidfile = NamedTemporaryFile(suffix='.pid', delete=True)
    filename = pidfile.name
    sys.stderr.write('\npid-file of the test daemon is %s\n' % filename)
    pidfile.close()
    call_w_pid = '%s --pidfile "%s"' % (call_daemon, filename)
    subprocess.call(call_w_pid, shell=True)
    time.sleep(.5)
    server = xmlrpclib.ServerProxy("http://localhost:%d/" % default_port)
    eq_(server.ping(), 'pong')
    pid = _fecth_pid_via_ps()
    eq_(server.getpid(), pid)
    with open(filename) as fp:
        pid2 = int(fp.read())
    eq_(pid2, pid)
    os.kill(pid, signal.SIGTERM)
    time.sleep(.5)
    assert_raises(IOError, server.ping)
    ok_(not os.path.exists(filename))
