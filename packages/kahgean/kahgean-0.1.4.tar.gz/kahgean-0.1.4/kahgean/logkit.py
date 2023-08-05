# Copyright (C) 2012 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license

"""\
kahgean.logkit
==============

The ``kahgean.logkit`` is a handy tools for developers to config logging
for their programs written in Python.

It's just a set of command-line and configuration file options definition,
and if a progeam will log to ``stderr``, try to make the result be colorful.
"""


import os
import sys
import logging
import logging.handlers

if os.name=='nt':
    # we need colorama for colored text under Microsoft Windows
    # for more information about colorama, please visit:
    # http://pypi.python.org/pypi/colorama
    try:
        from colorama import AnsiToWin32
    except ImportError:
        AnsiToWin32 = None

# ANSI escape code for colors
# visit http://en.wikipedia.org/wiki/ANSI_escape_code#Colors for more
CSI_PATTERN = u'\033[%dm'
(FORE_BLACK, FORE_RED, FORE_GREEN, FORE_YELLOW, FORE_BLUE, FORE_MAGENTA,
 FORE_CYAN, FORE_WHITE, _, FORE_RESET) = range(30, 40)
(BACK_BLACK, BACK_RED, BACK_GREEN, BACK_YELLOW, BACK_BLUE, BACK_MAGENTA,
 BACK_CYAN, BACK_WHITE, _, BACK_RESET) = range(40, 50)
(RESET_ALL, BRIGHT, DIM, NORMAL) = (0, 1, 2, 22)

CSI = lambda code: CSI_PATTERN % code

# default log and date format
DEFAULT_FORMAT = u'[%(asctime)s %(name)8.8s %(levelname)1.1s] %(message)s'
DEFAULT_DATE_FORMAT = u'%y%m%d %H:%M:%S'


class ColoredFormatter(logging.Formatter):
    
    def __init__(self, colored, fmt=None, datefmt=None):
        logging.Formatter.__init__(self, fmt, datefmt)
        self.colored = bool(colored)
                
    def format(self, record):
        # common log record information
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        s = self._fmt % record.__dict__
        # colors
        if self.colored:
            if record.levelno == logging.DEBUG:
                prefix = CSI(BRIGHT)+CSI(FORE_CYAN)
            elif record.levelno == logging.INFO:
                prefix = CSI(BRIGHT)+CSI(FORE_GREEN)
            elif record.levelno == logging.WARN:
                prefix = CSI(BRIGHT)+CSI(FORE_YELLOW)
            elif record.levelno == logging.ERROR:
                prefix = CSI(BRIGHT)+CSI(FORE_RED)
            elif record.levelno == logging.CRITICAL:
                prefix = CSI(BRIGHT)+CSI(BACK_RED)+CSI(FORE_YELLOW)
            else:
                prefix = CSI(RESET_ALL)
            s = prefix + s + CSI(RESET_ALL)
        # append exception information if needed
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != u"\n":
                s = s + u"\n"
            try:
                s = s + record.exc_text
            except UnicodeError:
                # Sometimes filenames have non-ASCII chars, which can lead
                # to errors when s is Unicode and record.exc_text is str
                # See issue 8924
                s = s + record.exc_text.decode(sys.getfilesystemencoding())
        return s


def append_options(options):
    """work with ``kahgean.options``, append arguments to the given
    ``Options`` object"""
    options.add_option('--log-level', help='logging level (default: info)')
    options.add_option('--log-format', help='')
    options.add_option('--log-date-format', help='')
    options.add_option('--log-to-stderr', type=bool, help='')
    options.add_option('--log-filename', help='log filename')
    options.add_option('--log-server', help='log server')


def deal_with_options(options, clear_handlers=True):
    """work with ``append_options()``, deal with the parsing result of
    the ``options`` object"""
    root_logger = logging.getLogger()
    # remove all hanlers
    if clear_handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
    # setup log level
    level_name = options.get('log-level', 'info')
    root_logger.setLevel(level_name.upper())
    # setup formats
    format = options.get('log-format', DEFAULT_FORMAT)
    date_format = options.get('log-date-format', DEFAULT_DATE_FORMAT)
    # if log_filename is given, use a file-based handler
    log_filename = options.get('log-filename', None)
    if log_filename:
        handler = logging.FileHandler(log_filename, encoding='utf8')
        formatter = ColoredFormatter(False, format, date_format)
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
    # if log_server is given, use a socket-based handler
    log_server = options.get('log-server', None)
    if log_server:
        info = log_server.split(':', 1)
        if len(info) == 2:
            # for ``address:port``
            host, port = info
            port = int(port)
        else:
            host = info[0]
            port = logging.handlers.DEFAULT_TCP_LOGGING_PORT
        handler = logging.handlers.SocketHandler(host, port)
        root_logger.addHandler(handler)
    # if use stderr to log (either log_to_stderr is True, or no any handlers
    # have been registered to the root logger), try to make log text colorful
    log_to_stderr = options.get('log-to-stderr', None)
    if log_to_stderr or (log_to_stderr is None and not root_logger.handlers):
        stderr = sys.stderr
        colored = True
        if not stderr.isatty():
            colored = False
        else:
            if os.name == 'nt':
                if not AnsiToWin32:
                    colored = False
                else:
                    stderr = AnsiToWin32(stderr).stream
        handler = logging.StreamHandler(stderr)
        formatter = ColoredFormatter(colored, format, date_format)
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
