#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2013 Krister Hedfors
#

__all__ = (
    'Test_Netmask',
    'Test_IPRangeIterator',
)


import doctest
import unittest

from xnet.net.ipv4 import (
    IP,
    Netmask,
    IPRangeIterator,
)


class Test_Netmask(unittest.TestCase):

    def test_basics(self):
        netmask = Netmask('255.255.255.0')
        self.assertEqual(netmask.bitmask, 0xffffff00)
        self.assertEqual(netmask.bitlen, 24)
        self.assertEqual(
            netmask.get_first_addr('1.2.3.4').__str__(),
            '1.2.3.0')
        self.assertEqual(
            netmask.get_last_addr('1.2.3.4').__str__(),
            '1.2.3.255')


class Test_IPRangeIterator(unittest.TestCase):

    def test_netmask_short_notation(self):
        for i in xrange(22, 32):  # cant run all, to expensive
            it = IPRangeIterator('10.0.0.0/{0}'.format(i))
            lst = list(it)
            #
            # validate number of returned IPs
            #
            assert len(lst) == 2 ** (32 - i)
            prev = IP(0)
            #
            # validate incrementating aspect of range
            #
            for ipnum in lst:
                ip = IP(ipnum)
                assert int(prev) < int(ip)
                prev = ip


def _test():
    print(doctest.testmod())
    unittest.main()

if __name__ == "__main__":
    _test()
