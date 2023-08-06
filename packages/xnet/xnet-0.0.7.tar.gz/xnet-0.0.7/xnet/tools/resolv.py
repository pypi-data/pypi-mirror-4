#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2011 Krister Hedfors
#


import unittest
import doctest
import socket

import gevent

from xnet.debug import pdb
from xnet.tools import Tool


class ResolvTool(Tool):

    __description__ = 'resolve hostnames to IPs back and forth'
    __itemname__ = 'host'

    cmdline_options = [
        ('-e', '--reverse', 'perform reverse lookup',
            dict(dest='reverse', action='store_true')),
        ('-c', '--deep', 'keep looking up as long as new addresses appear',
            dict(dest='deep', action='store_true')),
    ]

    def __parse__(self, line, iterator):
        item = line.strip()
        result = {}
        if self.options.reverse:
            result['ip'] = item
        else:
            result['host'] = item
        return result

    def __action__(self, parse_result):
        if self.options.reverse:
            return self._reverse_lookup(parse_result)
        else:
            return self._lookup(parse_result)

    def _lookup(self, parse_result):
        host = parse_result['host']
        result = {'host': host}
        try:
            ip = socket.gethostbyname(host)
            result['ip'] = ip
        except socket.error, e:
            pdb.set_trace()
        except gevent.GreenletExit:
            result['state'] = 'timeout'
        finally:
            pass
        return result

    def _reverse_lookup(self, parse_result):
        ip = parse_result['ip']
        result = {'ip': ip}
        try:
            addrlist = socket.gethostbyaddr(ip)
            result['host'] = addrlist[0]
            result['hostlist'] = addrlist
        except socket.error, e:
            pdb.set_trace()
        except gevent.GreenletExit:
            result['state'] = 'timeout'
        finally:
            pass
        return result

    def __format__(self, line, parse_result, action_result):
        output = '{0} {1}'.format(
            action_result['ip'],
            action_result['host'],
        )
        return output


def main():
    import xnet.tools
    xnet.tools.run(ResolvTool)


if __name__ == "__main__":
    main()
    #doctest.testmod()
    #unittest.main()
