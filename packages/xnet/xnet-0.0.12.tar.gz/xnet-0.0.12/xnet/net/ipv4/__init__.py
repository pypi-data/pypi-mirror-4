#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2013 Krister Hedfors
#

import re


class IPException(Exception):
    pass


class IP(object):
    '''
        >>> from xnet.testing.exceptions import assert_raises
        >>> IP('1.2.3.4').__str__()
        '1.2.3.4'

        >>> assert_raises(ValueError, lambda: IP(''))
        >>> assert_raises(ValueError, lambda: IP('foo'))
        >>> assert_raises(ValueError, lambda: IP('1.2'))
        >>> assert_raises(ValueError, lambda: IP('1.2.3'))
        >>> assert_raises(ValueError, lambda: IP('1.2.3.4.5'))
        >>> assert_raises(ValueError, lambda: IP(None))

        >>> assert int(IP('0.0.0.1')) == 0x00000001 == 1
        >>> assert int(IP('0.0.1.0')) == 0x00000100 == 256
        >>> assert int(IP('0.1.0.0')) == 0x00010000 == 65536
        >>> assert int(IP('1.0.0.0')) == 0x01000000 == 16777216

        >>> assert IP(1).__str__() == '0.0.0.1'
        >>> assert IP(256).__str__() == '0.0.1.0'
        >>> assert IP(65536).__str__() == '0.1.0.0'
        >>> assert IP(16777216).__str__() == '1.0.0.0'
    '''

    _E_INVALID = 'Invalid IP address: {0}'

    def __init__(self, ip):
        self._octets = self._parse_ip(ip)

    def __str__(self):
        return '{0}.{1}.{2}.{3}'.format(*self._octets)

    def __repr__(self):
        return "<IP('{0}')>".format(self.__str__())

    def _parse_ip(self, ip):
        if isinstance(ip, self.__class__):
            return ip._octets
        ip = str(ip)
        if ip.isdigit():
            ip = int(ip)
            return self._parse_ip_int(ip)
        if not '.' in ip:
            errmsg = self._E_INVALID.format(ip)
            raise ValueError(errmsg)
        w = ip.split('.')
        if not len(w) == 4:
            errmsg = self._E_INVALID.format(ip)
            raise ValueError(errmsg)
        try:
            octets = map(int, w)
        except ValueError:
            errmsg = self._E_INVALID.format(ip)
            raise ValueError(errmsg)
        for octet in octets:
            if not (0 <= octet <= 255):
                errmsg = self._E_INVALID.format(ip)
                raise ValueError(errmsg)
        octets = tuple(octets)
        return octets

    def _parse_ip_int(self, n):
        a = (n >> 24) & 0xff
        b = (n >> 16) & 0xff
        c = (n >> 8) & 0xff
        d = (n >> 0) & 0xff
        return (a, b, c, d)

    def __int__(self):
        n0, n1, n2, n3 = self._octets
        n = (n0 << 24) + (n1 << 16) + (n2 << 8) + n3
        return n


class Netmask(object):
    '''
        >>> netmask = Netmask('255.255.255.0')
        >>> netmask.get_network_part('1.2.3.4')
        <IP('1.2.3.0')>
        >>> netmask.get_host_part('1.2.3.4')
        <IP('0.0.0.4')>
    '''

    _E_INVALID = 'Invalid netmask: {0}'

    _bitlen_to_bitmask = dict([
        (i, 0xffffffffL & (0xffffffffL << (32 - i))) for i in xrange(0, 33)
    ])

    _bitmask_to_bitlen = dict([
        (0xffffffffL & (0xffffffffL << (32 - i)), i) for i in xrange(0, 33)
    ])

    def __init__(self, netmask):
        (self._bitlen, self._bitmask) = self._parse_netmask(netmask)

    def _parse_netmask(self, netmask):
        bitlen = None
        bitmask = None
        if isinstance(netmask, self.__class__):
            return (netmask._bitlen, netmask._bitmask)
        #
        # short netmask syntax
        #
        if netmask.isdigit():
            bitlen = int(netmask)
            if not (0 <= bitlen <= 32):
                raise ValueError(self._E_INVALID.format(netmask))
            bitmask = self._bitlen_to_bitmask[bitlen]
            return (bitlen, bitmask)
        #
        # long netmask syntax
        #
        try:
            addr = IP(netmask)
        except ValueError:
            raise ValueError(self._E_INVALID.format(netmask))
        bitmask = int(addr)
        if not bitmask in self._bitmask_to_bitlen:
            raise ValueError(self._E_INVALID.format(netmask))
        bitlen = self._bitmask_to_bitlen[bitmask]
        return (bitlen, bitmask)

    @property
    def bitlen(self):
        return self._bitlen

    @property
    def bitmask(self):
        return self._bitmask

    def get_first_addr(self, ip):
        return self.get_network_part(ip)

    def get_last_addr(self, ip):
        host_part = self._bitmask ^ 0xffffffff
        addr = int(self.get_network_part(ip)) + host_part
        return IP(addr)

    def get_network_part(self, ip):
        if not isinstance(ip, IP):
            ip = IP(ip)
        network = int(ip) & self._bitmask
        return IP(network)

    def get_host_part(self, ip):
        if not isinstance(ip, IP):
            ip = IP(ip)
        host = int(ip) & ~self._bitmask
        return IP(host)


class IPRangeIterator(object):
    '''
        >>> ipr = IPRangeIterator('1.2.3.4')
        >>> assert ipr._is_ip('1.2.3.4')
        >>> assert not ipr._is_ip('1.2.3.x')

        >>> ipr = IPRangeIterator('1.2.3.*')
        >>> assert '1.2.3.4' in ipr
        >>> assert '1.2.3.9' in ipr
        >>> assert not '1.2.9.4' in ipr
        >>> assert not '1.9.3.4' in ipr
        >>> assert not '9.2.3.4' in ipr

        >>> ipr = IPRangeIterator('5-6.1.1.1')
        >>> assert not '4.1.1.1' in ipr
        >>> assert '5.1.1.1' in ipr
        >>> assert '6.1.1.1' in ipr
        >>> assert not '7.1.1.1' in ipr
    '''

    _E_INVALID = 'Invalid IP-range: {0}'

    def __init__(self, iprange, state=None):
        self._iprange = iprange
        self._state = state
        self._ip = None
        self._netmask = None
        self._octet_ranges = None
        #
        iprange = str(iprange)
        #
        # If netmask, accept only IP and
        # iterate all hosts within that network.
        # Example:  1.2.3.0/24
        #
        if '/' in iprange:
            tmp = iprange.split('/')
            if not len(tmp) == 2:
                raise ValueError(self._E_INVALID.format(iprange))
            self._ip = IP(tmp[0])
            self._netmask = Netmask(tmp[1])
        #
        # If no netmask, handle range and wildcard
        # notations as usual.
        # Examples: 1.2.3.*, 10.0.0-5.*
        #
        else:
            if not '.' in iprange or iprange.split('.').__len__() != 4:
                raise ValueError(self._E_INVALID.format(iprange))
            w = iprange.split('.')
            octet_ranges = map(self._get_octet_range, w)
            self._octet_ranges = octet_ranges

    #
    # broken, never invoked
    #
    def __in__(self, val):
        int_octets = self._get_ip_octets(val)
        for i in xrange(4):
            octet = int_octets[i]
            (lower, upper) = self._octet_ranges[i]
            if not (lower <= octet < upper):
                return False
        return True

    def _is_ip(self, val):
        expr = re.compile(r'^(\d+)\.(\d+)\.(\d+)\.(\d+)$')
        m = expr.match(val)
        if not m:
            return False
        octets = [m.group(i) for i in xrange(1, 5)]
        int_octets = map(lambda d: int(d), octets)
        if False in map(lambda n: (0 <= n <= 255), int_octets):
            return False
        return True

    def _get_ip_octets(self, ipstring):
        expr = re.compile(r'^(\d+)\.(\d+)\.(\d+)\.(\d+)$')
        m = expr.match(ipstring)
        if not m:
            return False
        octets = [m.group(i) for i in xrange(1, 5)]
        int_octets = map(lambda d: int(d), octets)
        if False in map(lambda n: (0 <= n <= 255), int_octets):
            return False
        return int_octets

    def _get_octet_range(self, octet):
        if octet == '*':
            return (1, 256)
        elif octet.isdigit():
            return (int(octet), int(octet) + 1)
        elif '-' in octet:
            (start, end) = octet.split('-', 1)
            if start.isdigit() and end.isdigit():
                return (int(start), int(end) + 1)  # ranges are inclusive
        raise ValueError(self._E_INVALID.format(self._iprange))

    def __iter__(self):
        if not self._octet_ranges is None:
            return self._generate_from_octet_ranges()
        elif not self._netmask is None:
            return self._generate_from_netmask()
        assert not 'Logic error'

    def _generate_from_octet_ranges(self):
        A, B, C, D = self._octet_ranges
        state = self._state
        for a in xrange(*A):
            for b in xrange(*B):
                for c in xrange(*C):
                    for d in xrange(*D):
                        ip = '{0}.{1}.{2}.{3}'.format(a, b, c, d)
                        if not state is None:
                            if ip in state:
                                continue
                            state.add(ip)
                        yield ip

    def _generate_from_netmask(self):
        start = self._netmask.get_first_addr(self._ip).__int__()
        end = self._netmask.get_last_addr(self._ip).__int__()
        i = start
        while i <= end:
            yield IP(i).__str__()
            i += 1


def _test():
    import doctest
    import unittest
    print('doctest: ' + doctest.testmod().__str__())
    unittest.main()

if __name__ == "__main__":
    _test()
