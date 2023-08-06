#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2011 Krister Hedfors
#


import unittest
import doctest
import socket

import gevent

from xnet.tools import Tool


class ResolvTool(Tool):

    __toolname__ = 'resolv'
    __itemname__ = 'host'
    __description__ = 'resolve hostnames to IPs back and forth'

    cmdline_options = [
        ('-e', '--reverse', 'perform reverse lookup',
            dict(dest='reverse', action='store_true')),
        ('-c', '--deep', 'keep looking up as long as new addresses appear',
            dict(dest='deep', action='store_true')),
    ]

    @classmethod
    def print_source(cls):
        cls._print_source(__file__)

    def __parse__(self, line, iterator):
        self._item = item = line.strip()
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
            #
            # errno numbers differ between platforms,
            # but tests for 'closed' and 'filtered'
            # below should work universally.
            #
            errmsg = e.strerror.lower()
            if 'connection refused' in errmsg:
                errmsg = 'closed'
            elif 'timed out' in errmsg:
                errmsg = 'filtered'
            else:
                errmsg = errmsg.replace(' ', '-').replace(',', '-')
            errmsg = '{0} {1}'.format(host, errmsg)
            self.set_error(errmsg) 
            self.stderr = True
            return None
        #except gevent.GreenletExit:
        #    result['state'] = 'timeout'
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
            #
            # errno numbers differ between platforms,
            # but tests for 'closed' and 'filtered'
            # below should work universally.
            #
            errmsg = e.strerror.lower()
            if 'connection refused' in errmsg:
                errmsg = 'closed'
            elif 'timed out' in errmsg:
                errmsg = 'filtered'
            else:
                errmsg = errmsg.replace(' ', '-').replace(',', '-')
            errmsg = '{0} {1}'.format(ip, errmsg)
            self.set_error(errmsg) 
            self.stderr = True
            return None
        #except gevent.GreenletExit:
        #    result['state'] = 'timeout'
        finally:
            pass
        return result

    def __format__(self, line, parse_result, action_result):
        output = '{0} {1}'.format(
            action_result['ip'],
            action_result['host'],
        )
        return output

    def __timeout__(self):
        output = 'timeout {0}\n'.format(self._item)

    @classmethod
    def __format_help__(cls):
        name = cls.__toolname__
        output = '''
Format variables for %s:

 ip       - IP of host
 host     - host of IP

Default format:
 '{ip} {host}'
        ''' % cls.__toolname__
        return output


def main():
    import xnet.tools.run
    xnet.tools.run.run(ResolvTool)


if __name__ == "__main__":
    main()
    #doctest.testmod()
    #unittest.main()
