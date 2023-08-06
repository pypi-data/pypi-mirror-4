#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2013 Krister Hedfors
#
# iterera ranges och spara varje output
# i set foer att stoppa dubletter.
# Skit i performance.


import unittest
import doctest

from xnet.tools import Tool
from xnet.net.ipv4 import IPRangeIterator


class IPRangeTool(Tool):

    __description__ = 'generate list of IPs from IP ranges'
    __itemname__ = 'iprange'

    cmdline_options = [
        ('', '--print-duplicates', 'stateless, faster',
            dict(dest='print_duplicates', action='store_true')),
    ]

    @classmethod
    def print_source(cls):
        cls._print_source(__file__)

    def __init__(self, *args, **kw):
        super(IPRangeTool, self).__init__(*args, **kw)
        #
        # Use shared state of printed IPs between all
        # IPRangeTool instances.
        #
        if not self.options.print_duplicates and \
                not hasattr(self.__class__, '_iprange_state'):
            self.__class__._iprange_state = set()

    def __parse__(self, line, iterator):
        iprange = line.strip()
        return {'iprange': iprange}

    def __action__(self, parse_result):
        iprange = parse_result['iprange']
        iprangeiter = None
        if not self.options.print_duplicates:
            iprangeiter = IPRangeIterator(iprange, self._get_iprange_state())
        else:
            iprangeiter = IPRangeIterator(iprange)
        return {'iprangeiter': iprangeiter}

    def _get_iprange_state(self):
        return self.__class__._iprange_state

    def _set_iprange_state(self, iprange_state):
        self.__class__._iprange_state = iprange_state

    def __format__(self, line, parse_result, action_result):
        output = ''
        iprangeiter = action_result['iprangeiter']
        iplist = list(iprangeiter)
        output += '\n'.join(iplist)
        return output

    def __format_help__(self):
        return 'No customized formatting available\n'


def main():
    import xnet.tools.run
    xnet.tools.run.run(IPRangeTool)


if __name__ == "__main__":
    main()
    #doctest.testmod()
    #unittest.main()
