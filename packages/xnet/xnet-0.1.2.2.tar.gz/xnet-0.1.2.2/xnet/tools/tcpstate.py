#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2011 Krister Hedfors
#

__all__ = ['TcpStateTool']


import unittest
import doctest
import socket
import gevent

from xnet.tools import Tool
from xnet.net.ipv4 import IPRangeIterator


class TcpStateTool(Tool):
    '''
        TcpStateTool
            Default format is:
                {addr} {port} {state}
            Output is sent to stderr when state
            is neither 'open', 'closed' nor 'filtered',
            (such as address resolution errors).
    '''

    __toolname__ = 'tcpstate'
    __itemname__ = 'host'
    __description__ = 'test if TCP-ports are open'

    cmdline_options = [
        ('-p', '--port', 'port to state check',
            dict(dest='port')),
        ('-O', '--open', 'print only results for open ports',
            dict(dest='open')),
    ]

    @classmethod
    def print_source(cls):
        cls._print_source(__file__)

    def __repr__(self):
        state = ('x', 'finished')[self.finished]
        if hasattr(self, '_addr'):
            host, port = self._addr
            return '<tcpstate {0}:{1} {2}>'.format(host, port, state)
        return '<tcpstate {0}>'.format(state)

    @classmethod
    def __massage__(self, iterator):
        for item in iterator:
            item = item.strip()
            try:
                iprangeiter = IPRangeIterator(item)
            except ValueError:
                yield item
            else:
                for ip in iprangeiter:
                    yield str(ip)

    def __parse__(self, item, iterator):
        port = 80
        if not self.options.port is None:
            port = int(self.options.port)
        host = item.strip()
        addr = (host, port)
        self._addr = addr  # for __timeout__()
        result = {'addr': addr}
        return result

    def __action__(self, parse_result):
        addr = parse_result['addr']
        state = None
        result = {}
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(addr)
            state = 'open'
        except socket.error, e:
            #
            # errno numbers differ between platforms,
            # but tests for 'closed' and 'filtered'
            # below should work universally.
            #
            errmsg = e.strerror.lower()
            if 'connection refused' in errmsg:
                state = 'closed'
            elif 'timed out' in errmsg:
                state = 'filtered'
            else:
                state = errmsg.replace(' ', '-').replace(',', '-')
        #except gevent.GreenletExit:
        #    #
        #    # happens in BT, not OSX
        #    #
        #    state = 'filtered'
        finally:
            if s:
                s.close()
        result['host'] = addr[0]
        result['port'] = addr[1]
        result['state'] = state
        return result

    def __format__(self, line, parse_result, action_result):
        output = ''
        if action_result:
            output = '{0} {1} {2}'.format(
                action_result['host'],
                action_result['port'],
                action_result['state'],
            )
        return output

    @classmethod
    def __format_help__(cls):
        output = '''
Format variables for %s:

 host    - target host
 port    - target port
 state   - TCP-state or error-message

Default format:
 '{host} {port} {state}'
        ''' % cls.__toolname__
        return output

    def __timeout__(self):
        if hasattr(self, '_addr'):
            host, port = self._addr
            return '{0} {1} timeout\n'.format(host, port)
        return None


def main():
    import xnet.tools.run
    xnet.tools.run.run(TcpStateTool)


if __name__ == "__main__":
    main()
    #doctest.testmod()
    #unittest.main()
