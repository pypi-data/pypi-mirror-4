#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2011 Krister Hedfors
#

__all__ = ['NetcatsTool']


import unittest
import doctest
import os
import socket
import fcntl
import gevent
from gevent import select
#from gevent.socket import wait_read

from xnet.tools import Tool
from xnet.net.ipv4 import IPRangeIterator


class NetcatsTool(Tool):
    '''
        NetcatsTool
            Default format is:
                {addr} {port} [data received from remote host...]

            Input from stdin is sent to all hosts. Each line of
            output from remote host is prefixed by what __format__()
            returns.
    '''

    __description__ = 'multi-peer netcat-like tool'
    __itemname__ = 'host'

    cmdline_options = [
        ('-p', '--port', 'port to connect to check',
            dict(dest='port')),
        #('-O', '--open', 'print only results for open ports',
        #    dict(dest='open')),
    ]

    def __init__(self, options, stdin_data='', *args, **kw):
        super(NetcatsTool, self).__init__(options, *args, **kw)
        self._stdin_queue = []
        self._stdin_pipe = self._nonblocking_pipe()
        self._addr = None
        self._port = 80
        if not self.options.port is None:
            self._port = int(self.options.port)
        self._send_buffer = stdin_data
        self._recv_buffer = ''

    def __del__(self):
        os.close(self._stdin_pipe[0])
        os.close(self._stdin_pipe[1])

    def _nonblocking_pipe(self):
        pipe = os.pipe()
        fcntl.fcntl(pipe[0], fcntl.F_SETFL, os.O_NONBLOCK)
        fcntl.fcntl(pipe[1], fcntl.F_SETFL, os.O_NONBLOCK)
        return pipe

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
        host = item.strip()
        addr = (host, self._port)
        self._addr = addr  # for __timeout__()
        result = {'addr': addr}
        return result

    def __action__(self, parse_result):
        addr = parse_result['addr']
        sock = None
        socket_error = None
        state = None
        result = {}
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(addr)
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
                state = 'FIXME-' + errmsg.replace(' ', '-')
        #except gevent.GreenletExit:
        #    state = 'filtered'

        done = False
        stdin = self._stdin_pipe[0]
        while not done and not sock is None:
            rfds = [stdin, sock]
            rlist, _, _ = select.select(rfds, [], [])
            if stdin in rlist:
                data = os.read(stdin, 4096)
                if len(data) > 0:
                    sock.send(data)
                else:
                    done = True
            if sock in rlist:
                data = sock.recv(4096)
                if len(data) > 0:
                    print 'sock:', data
                else:
                    done = True

            if 0:
                wait_read(self._stdin_pipe[0])
                data = self._stdin_pipe[0]
                if len(data) > 0:
                    sock.send(data)
                else:
                    done = True

        if 0 and not sock is None:
            done = False
            while not done:
                while len(self._stdin_queue):
                    data = self._stdin_queue[0]
                    if len(data) > 0:
                        sock.send(data)
                    else:
                        done = True
                    del self._stdin_queue[0]
                try:
                    data = sock.recv(1024)
                    if len(data) > 0:
                        self._recv_buffer += data
                    else:
                        done = True
                except socket.error, e:
                    socket_error = 'FIXME2-' + errmsg.replace(' ', '-')
                    sys.stderr.write(socket_error + '\n')
                    done = True

        if 0:
            if not sock is None:
                sock.send(self._send_buffer)
                done = False
                while not done:
                    print 'poop loop'
                    import sys
                    sys.stdout.flush()
                    try:
                        data = sock.recv(1024)
                        if len(data):
                            self._recv_buffer += data
                        else:
                            done = True
                    except socket.error, e:
                        socket_error = 'FIXME2-' + errmsg.replace(' ', '-')
                        sys.stderr.write(socket_error + '\n')
                        done = True
        result['host'] = self._addr[0]
        result['port'] = self._addr[1]
        result['received'] = self._recv_buffer
        result['socket_error'] = socket_error
        return result

    def __format__(self, line, parse_result, action_result):
        output = ''
        if action_result:
            output = '{0} {1} {2}'.format(
                action_result['host'],
                action_result['port'],
                action_result['received'],
            )
        return output

    def __timeout__(self):
        if hasattr(self, '_addr'):
            host, port = self._addr
            return 'timeout {0} {1}\n'.format(host, port)
        return None

    def feed_stdin(self, data):
        self._stdin_queue.append(data)



def main():
    import xnet.tools
    #xnet.tools.run(NetcatsTool, stdin_data_arg='stdin_data')
    xnet.tools.run(NetcatsTool, tool_reads_stdin=True)


if __name__ == "__main__":
    main()
    #doctest.testmod()
    #unittest.main()
