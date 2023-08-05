# Copyright (C) 2012 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license

import os
import sys
from shlex import split
from functools import partial
from tempfile import NamedTemporaryFile
from nose.tools import *
from kahgean.options import Options


def setup_module():
    global options
    options = Options()
    options.add_option('--name')
    options.add_option('--gender', choices=['male', 'female', 'unknown'],
                       default='unknown')
    options.add_option('--enabled', type=bool)
    options.add_option('--leader', dest='membership', action='store_const',
                       const='leader', default='member')
    options.add_option('--skills', nargs='*')
    options.add_option('--foo-bar')
    options.add_option('--foo-baz')


@raises(AttributeError)
def test_cli_no_value_no_default():
    options.parse_options([])
    options.get('name')


def test_cli_no_value_w_defalt():
    options.parse_options([])
    eq_(options.get('gender'), 'unknown')


def prepare_unaccptable():
    global stderr
    stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w+')


def cleanup_unaccptable():
    sys.stderr = stderr


@with_setup(prepare_unaccptable, cleanup_unaccptable)
@raises(SystemExit)
def test_cli_unacceptable_value():
    options.parse_options(split('--gender m'))


def test_cli_quoted_value():
    options.parse_options(split('--name "Who Carez"'))
    eq_(options.get('name'), 'Who Carez')


def test_cli_store_const():
    options.parse_options(split('--leader'))
    eq_(options.get('membership'), 'leader')
    options.parse_options([])
    eq_(options.get('membership'), 'member')


def test_cli_bool():
    options.parse_options(split('--enabled on'))
    eq_(options.get('enabled'), True)
    options.parse_options(split('--enabled yes'))
    eq_(options.get('enabled'), True)
    options.parse_options(split('--enabled 1'))
    eq_(options.get('enabled'), True)
    options.parse_options(split('--enabled tRue'))
    eq_(options.get('enabled'), True)
    options.parse_options(split('--enabled off'))
    eq_(options.get('enabled'), False)
    options.parse_options(split('--enabled no'))
    eq_(options.get('enabled'), False)
    options.parse_options(split('--enabled 0'))
    eq_(options.get('enabled'), False)
    options.parse_options(split('--enabled falSE'))
    eq_(options.get('enabled'), False)


def test_cli_nargs():
    skills = ['python', 'c', 'c++', 'php', 'perl', 'ruby']
    options.parse_options(split('--skills ' + ' '.join(skills)))
    result = options.get('skills')
    for skill in skills:
        ok_(skill in result)


def prepare_conf(data):
    global temp_config_file
    temp_config_file = NamedTemporaryFile(suffix='.conf', delete=False)
    temp_config_file.write(data)
    temp_config_file.close()


def cleanup_conf():
    if not temp_config_file.closed:
        temp_config_file.close()
    os.unlink(temp_config_file.name)


CONF_BASIC = """
[main]
name = "Haruhi Suzumiya"
gender = female
enabled = yes
leader
skills: delusion "CRUSH THE WORLD DOWN"
    leadership
"""

@with_setup(partial(prepare_conf, CONF_BASIC), cleanup_conf)
def test_conf_basic():
    options.parse_options(split('-f "%s"' % temp_config_file.name))
    eq_(options.get('name'), 'Haruhi Suzumiya')
    eq_(options.get('gender'), 'female')
    eq_(options.get('enabled'), True)
    eq_(options.get('membership'), 'leader')
    skills = options.get('skills')
    for skill in ['delusion', 'CRUSH THE WORLD DOWN', 'leadership']:
        ok_(skill in skills)


CONF_SECTION_SHORTCUT = """
[foo]
bar = bar
baz = baz
"""

@with_setup(partial(prepare_conf, CONF_SECTION_SHORTCUT), cleanup_conf)
def test_conf_section_shortcut():
    options.parse_options(split('-f "%s"' % temp_config_file.name))
    eq_(options.get('foo-bar'), 'bar')
    eq_(options.get('foo-baz'), 'baz')


CONF_OVERRIDE = """
[main]
enabled: 0
"""

@with_setup(partial(prepare_conf, CONF_OVERRIDE), cleanup_conf)
def test_cli_override_conf():
    options.parse_options(split('-f "%s" --enabled yes' % temp_config_file.name))
    eq_(options.get('enabled'), True)
