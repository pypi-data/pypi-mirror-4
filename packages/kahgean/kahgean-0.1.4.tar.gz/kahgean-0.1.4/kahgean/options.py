# Copyright (C) 2012 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license

"""
Options
=======

The ``kahgean.options`` module makes it easy to parse command-line
arguments and configuration file by just one set of defines. It's based
on `argparse`_ and  `ConfigParser`_ in the Python standard library.

.. _argparse: http://docs.python.org/library/argparse.html
.. _ConfigParser: http://docs.python.org/library/configparser.html

The program creates an instance of class ``Options``, then uses its
``add_option()`` method to define what options it requires. The arguments
of ``add_option()`` are same as ``ArgumentParser.add_argument()`` from
module ``argparse``. By default, ``Options`` will add an optional argument
which can be provided by command line ``-f`` or ``--config-file`` for
tell the program where to find the configuration file. After then,
by call the ``parse_options()`` method, ``Options`` will figure out how to
parse those options out of ``sys.argv`` and/or from a given configuration file.

Options in a configuration file are listed under the "main" section. for
example, command line arguments ``--host`` and ``--port`` can looked like
below in a configuration file:

    [main]
    host = 0.0.0.0
    port = 8080

If there are a set of options with same prefix, then they can be grouped by
a section which name is the prefix, for example, command line arguments
``--log-level`` and ``--log-filename`` can be grouped in the "log" section:

    [log]
    level = info
    filename = /path/to/logfile

If an option's type is ``bool``, then we can use '1', 'on', 'yes', and
'true' for ``True``, and '0', 'off', 'no', and 'false' for ``False``.

If both the configuration file and command-line define a same option, then
the one comes from command-line will win. In order to check whether or not
an option is provided by command-line, ``Options`` uses ``SUPPRESS`` as its
default value internal, thus we cannot use ``nargs='*'`` or ``N``.

Once ``parse_options()`` has been called, the program can use ``get()``
to fetch an option value, for example:

    options = Options()
    options.add_option('--host', default='0.0.0.0')
    options.add_option('--port', type=int)
    options.parse_options()
    host = options.get('host')
    port = options.get('port', 8080) # if neither config file nor command-line
                                     # provide this, use 8080

For more information, read the code please :-)
"""

import sys
import warnings
from argparse import ArgumentParser, HelpFormatter, SUPPRESS
from ConfigParser import SafeConfigParser
import shlex

__all__ = ['SUPPRESS', 'Options']


def _bool(value):
    value = str(value).lower()
    if value in ['0', 'off', 'no', 'false']:
        return False
    elif value in ['1', 'on', 'yes', 'true']:
        return True
    else:
        raise ValueError('unsupport boolean value')


class Options(object):
    """the Options class
    """
    
    def __init__(self, prog=None, description=None, epilog=None,
                 argument_default=SUPPRESS, formatter_class=HelpFormatter,
                 config_argument=None, config_file_dest='config_file',
                 main_section='main'):
        self.config_argument = config_argument or ['-f', '--config-file']
        self.config_file_dest = config_file_dest
        self.main_section = main_section
        self._defaults = dict()
        self._namespace = None
        self._arg_parser = ArgumentParser(prog, None, description, epilog,
                                          argument_default=argument_default,
                                          formatter_class=formatter_class)
        self.add_option(*self.config_argument, dest=self.config_file_dest,
                          metavar='filename', type=file, default=SUPPRESS,
                          help='path to the configuration file')

    def add_option(self, *args, **kwargs):
        """add option define
        
        For more information, please read the `argparse`_ document.
        
        .. _argparse:http://docs.python.org/library/argparse.html#\
the-add-argument-method
        """
        action = self._arg_parser.add_argument(*args, **kwargs)
    
    def parse_options(self, args=None):
        """parse options from command-line and/or configuration file"""
        # preparing...
        for action in self._arg_parser._actions:
            # make bool support 'on', 'off', etc.
            if action.type == bool:
                action.type = _bool
            # use SUPPRESS as default, so we can check whether or not
            # an option is given by command-line
            if action.default != SUPPRESS:
                self._defaults[action.dest] = action.default
                action.default = SUPPRESS
            # there is a side effect, we cannot support nargs="+" or N
            # use nargs="*" instead
            if action.nargs=='+' or (isinstance(action.nargs, int)
                                     and action.nargs>0):
                warnings.warn('not support nargs="+" or N, use "*" instead',
                              Warning)
                action.nargs = '*'
        # parsing the command-line...
        ns_a = self._arg_parser.parse_args(args)
        if hasattr(ns_a, self.config_file_dest):
            # parsing the configuration file...
            ns_c = self._load_options(getattr(ns_a, self.config_file_dest))
            for key in ns_c.__dict__:
                # use values in the configuration file if they are not
                # given in the command-line
                if not hasattr(ns_a, key):
                    setattr(ns_a, key, ns_c.__dict__[key])
        # fetch back defaults
        for dest in self._defaults:
            if not hasattr(ns_a, dest):
                setattr(ns_a, dest, self._defaults[dest])
        self._namespace = ns_a

    def _option_to_arg(self, section, option, value):
        # convert option = value under [section] to --section-option value
        # convert option under [section] to --section-option (if allow_no_value
        # is True)
        if section == self.main_section:
            argument = '--%s' % option
        else:
            argument = '--%s-%s' % (section, option)
        return '%s %s' % (argument, value) if value else argument

    def _load_options(self, file_):
        # generate a '--section-option value' sequence
        args = list()
        if sys.version_info >= (2, 7):
            parser = SafeConfigParser(allow_no_value=True)
        else:
            warnings.warn('not "allow_no_value" supprt when '
                          'parsing configuration files', Warning)
            parser = SafeConfigParser()
        parser.optionxform = str
        parser.readfp(file_)
        sections = parser.sections()
        for section in sections:
            options = parser.options(section)
            for option in options:
                value = parser.get(section, option)
                args.append(self._option_to_arg(section, option, value))
        file_.close()
        # list -> str
        args = ' '.join(args)
        # str -> list again, by shlex.split(), so that it can parse quotes
        args = shlex.split(args)
        # configuration file may provide options for other program
        # so we use parse_known_args
        namespace, _ = self._arg_parser.parse_known_args(args)
        return namespace

    def get(self, option, *args):
        """get an option's value"""
        if not self._namespace:
            raise RuntimeError("parse_options() has not been call")
        option = option.replace('-', '_')
        return getattr(self._namespace, option, *args)
