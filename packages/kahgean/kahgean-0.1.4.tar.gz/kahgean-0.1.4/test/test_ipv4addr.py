# Copyright (C) 2012 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license

from kahgean.ipv4addr import Address, Network, MASKS
from nose.tools import *

def test_address():
    a1 = Address('192.168.1.1')
    eq_(a1, 3232235777)
    a2 = Address(a1+1)
    eq_(str(a2), '192.168.1.2')


def test_network():
    n1 = Network('192.168.1.0/24')
    n2 = Network('192.168.1.0', 24)
    n3 = Network('192.168.1.0', '255.255.255.0')
    n4 = Network('192.168.1.0', '192.168.1.255')
    eq_(n1, n2)
    eq_(n1, n3)
    eq_(n1, n4)
    a1 = Address('192.168.1.1')
    ok_(a1 in n1)
    a2 = Address('192.168.0.1')
    ok_(a2 not in n1)


def test_masks():
    for i in range(33):
        base2 = '1'*i+'0'*(32-i)
        ok_(int(base2, base=2) in MASKS)


@raises(ValueError)
def test_invalid_addr():
    Address('192.168.1.256')


@raises(ValueError)
def test_invalid_net1():
    Network('192.168.1.0')


@raises(ValueError)
def test_invalid_net2():
    Network('192.168.1.0/33')


@raises(ValueError)
def test_invalid_net3():
    Network('192.168.1.0', '192.168.1.128')


@raises(ValueError)
def test_invalid_net3():
    Network('192.168.1.1', '192.168.1.128')
