# Copyright (C) 2012 Xue Can <xuecan@gmail.com> and contributors.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license

from collections import Sequence


class Address(long):
    
    def __new__(cls, address):
        if isinstance(address, basestring):
            value = Address._init_from_seq(address.strip().split('.'))
        elif isinstance(address, Sequence):
            value = Address._init_from_seq(address)
        elif type(address) in [int, long, Address]:
            value = Address._init_from_int(address)
        else:
            raise ValueError('unsupported address type')
        return super(Address, cls).__new__(cls, value)
    
    def __init__(self, address):
        value = long(self)
        v0 = value/2**24
        value = value-v0*2**24
        v1 = value/2**16
        value = value-v1*2**16
        v2 = value/2**8
        v3 = value-v2*2**8
        self._tuple_value = (v0, v1, v2, v3)
            
    @staticmethod
    def _init_from_int(value):
        value = long(value)
        if value<0 or value>2**32-1:
            raise ValueError('value should be in [0, 2**32-1]')
        return value
    
    @staticmethod
    def _init_from_seq(seq):
        if len(seq)!=4:
            raise ValueError('length of seq should be 4')
        v = [int(i) for i in seq]
        for i in v:
            if i<0 or i>2**8-1:
                raise ValueError('each piece in a IPv4 address should be in '
                                 '[0, 255]')
        return v[0]*2**24 + v[1]*2**16 + v[2]*2**8 + v[3]
    
    @property
    def tuple_value(self):
        return self._tuple_value
    
    def __str__(self):
        return '%d.%d.%d.%d' % self.tuple_value
    
    def __repr__(self):
        return 'Address <%s>' % self.__str__()


# Address(MASKS[24]) == Address('255.255.255.0')
MASKS = [long((2**i-1)<<(32-i)) for i in range(0,33)]
COMPS = [long((2**32-1)-i) for i in MASKS]


class Network(Sequence):
    """

    Network('192.168.1.0/24')
    Network('192.168.1.0', '24')
    Network('192.168.1.0', '255.255.255.0')
    Network('192.168.1.0', '192.168.1.255')
    """
    
    def __init__(self, address, extra=None):
        if not extra:
            # '192.168.1.0/24' => '192.168.1.0', '24'
            address, extra = address.split('/')
        address = Address(address)
        try:
            prefix_size = int(extra)
            if prefix_size<0 or prefix_size>32:
                raise ValueError
        except ValueError:
            prefix_size = -1
        if prefix_size >= 0:
            # extra is a prefix size
            mask = MASKS[prefix_size]
        else:
            extra = Address(extra)
            if extra in MASKS:
                # extra is a subnetwork mask 
                mask = long(extra)
            elif extra-address in COMPS:
                # extra is a broadcast address
                mask = MASKS[COMPS.index(extra-address)]
            else:
                mask = -1
        if mask==-1:
            raise ValueError('subnetwork mask not found from <%s/%s>' % (
                str(address), str(extra)))
        index = MASKS.index(mask)
        comp = COMPS[index]
        if address & comp:
            raise ValueError('<%s/%s> is not a valid network prefix' % (
                str(address), str(extra)))
        self._network = address # network prefix
        self._size = index      # prefix size, e.g. 24 means a /24 subnetwork
        self._length = comp+1   # length of the network, for example there
                                #    are 256 addresses in a /24 subnetwork
        self._broadcast = Address(address+comp) # broadcast address
        self._mask = Address(mask)              # subnetwork mask

    @property
    def network(self):
        return self._network

    @property
    def broadcast(self):
        return self._broadcast

    @property
    def size(self):
        return self._size

    @property
    def mask(self):
        return self._mask
    
    def __contains__(self, value):
        if type(value) in [int, long, Address]:
            return value>=self._network and value<=self._broadcast
        elif type(value) in [Network]:
            return self.network<=value.network \
                   and self.broadcast>=value.broadcast
    
    def __len__(self):
        return self._length

    def __getitem__(self, index):
        index = long(index)
        if index<0 and index>=self._length:
            raise IndexError('index out of range')
        return Address(self._network+index)

    def __iter__(self):
        i = 0
        while i<self._length:
            yield self[i]
            i+=1

    def index(self, value):
        if Address(value) in self:
            return value-self._network
        raise ValueError('%s not in this network' % str(value))

    def count(self, value):
        return 1 if Address(value) in self else 0

    def __reversed__(self):
        i = self._length
        while i>0:
            i -=1
            yield self[i]
    
    def __eq__(self, other):
        return self.network==other.network and self.mask==other.mask
    
    def __ne__(self, other):
        return not self==other
    
    def __str__(self):
        return '%s/%d' % (str(self._network), self.size)
    
    def __repr__(self):
        return 'Network <%s>' % self.__str__()
