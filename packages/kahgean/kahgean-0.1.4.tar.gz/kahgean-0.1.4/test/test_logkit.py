# Copyright (C) 2012 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license

import os
import sys
import warnings
import logging
from logging.handlers import DEFAULT_TCP_LOGGING_PORT
from tempfile import NamedTemporaryFile
import pickle
import SocketServer
import struct
import thread
import time
from nose.tools import *
from kahgean import logkit
from kahgean.options import Options


TEST_SERVER_PORT = DEFAULT_TCP_LOGGING_PORT + 10000


def setup_module():
    global options
    options = Options()
    logkit.append_options(options)


def test_no_options():
    options.parse_options([])
    logkit.deal_with_options(options)
    sys.stderr.write('\n')
    logging.debug('You should not see this')
    logging.info('this is an info')
    logging.warning('this is a warning')
    logging.error('this is an error')
    logging.critical('this is a critical error')
    sys.stderr.write('You should see 4 log lines above with colors, '
                     'right? (y or N)')
    answer = raw_input() or 'n'
    ok_(answer.lower() in ['y', 'yes'])


def prepare_logfile():
    global temp_file
    temp_file = NamedTemporaryFile(suffix='.log', delete=False)
    temp_file.close()


def cleanup_logfile():
    if not temp_file.closed:
        temp_file.close()
    os.unlink(temp_file.name)


@with_setup(prepare_logfile, cleanup_logfile)
def test_logfile():
    options.parse_options(['--log-level', 'error',
                           '--log-filename', temp_file.name])
    logkit.deal_with_options(options)
    logging.debug('debug')
    logging.info('info')
    logging.error('error')
    try:
        raise RuntimeError('exception')
    except:
        logging.exception('exception')
    logging.critical('critical')
    temp_file.close()
    fp = open(temp_file.name, 'r')
    data = fp.read(4096)
    fp.close()
    ok_('debug' not in data)
    ok_('info' not in data)
    ok_('error' in data)
    ok_('exception' in data)
    ok_('critical' in data)


def prepare_logserver():
    global logserver, registry
    registry = list()
    logserver = SocketServer.TCPServer(
        ('localhost', TEST_SERVER_PORT),
        LogRecordStreamHandler)
    thread.start_new_thread(logserver.serve_forever, ())


@with_setup(prepare_logserver)
def test_logserver():
    options.parse_options(['--log-level', 'warning', '--log-server',
                           'localhost:%d' % TEST_SERVER_PORT])
    logkit.deal_with_options(options)
    logging.debug('debug')
    logging.info('info')
    logging.warning('warning')
    logging.error('error')
    try:
        raise RuntimeError('exception')
    except:
        logging.exception('exception')
    logging.critical('critical')
    time.sleep(.1)
    ok_('debug' not in registry)
    ok_('info' not in registry)
    ok_('warning' in registry)
    ok_('error' in registry)
    ok_('exception' in registry)
    ok_('critical' in registry)


class LogRecordStreamHandler(SocketServer.StreamRequestHandler):
    """Handler for a streaming logging request.

    For more information about this, please visit:
    http://docs.python.org/howto/logging-cookbook.html
    """

    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            record = logging.makeLogRecord(obj)
            self.handleLogRecord(record)


    def unPickle(self, data):
        return pickle.loads(data)

    def handleLogRecord(self, record):
        registry.append(record.msg)
