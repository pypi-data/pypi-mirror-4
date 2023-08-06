#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2011 Krister Hedfors
#

__all__ = ['SSLInfoTool']


import unittest
import doctest
import sys
import ssl
import socket

import OpenSSL
import gevent

from xnet.tools import Tool


class SSLInfoException(Exception):
    pass


class SSLInfoTool(Tool):

    __description__ = 'get ssl and certificate information'
    __itemname__ = 'host'

    cmdline_options = [
        ('-p', '--port', 'tcp port',
            dict(dest='port')),
        ('', '--cn', 'print common name only',
            dict(dest='cn', action='store_true'))
    ]

    def __parse__(self, line, iterator):
        result = {}
        host = line.strip()
        port = 443
        if '://' in line:
            proto, host = line.split('://', 1)
            if proto != 'https':
                raise SSLInfoException('unknown uri protocol: ' + line)
            if host[-1] == '/':
                host = host[:-1]
        if self.options.port:
            port = int(self.options.port)
        addr = (host, port)
        result['addr'] = addr
        return result

    def __action__(self, parse_result):
        result = {}
        addr = parse_result['addr']
        try:
            cert = ssl.get_server_certificate(addr)
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
            components = dict(x509.get_subject().get_components())
        except socket.error, e:
            #
            # errno numbers differ between platforms,
            # but tests for 'closed' and 'filtered'
            # below should work universally.
            #
            errmsg = e.strerror.lower()
            if 'connection refused' in errmsg:
                errmsg = 'closed {0} {1}'.format(*addr)
            elif 'timed out' in errmsg:
                errmsg = 'filtered {0} {1}'.format(*addr)
            else:
                errmsg = errmsg.replace(' ', '-').replace(',', '-')
            self.set_error(errmsg)
            self.stderr = True
            return None
        except gevent.GreenletExit:
            #
            # happens in BT, not OSX
            #
            self.set_error('TIMEOUT')
            self.stderr = True
            print 'TIMEOUT'
            return None
        except Exception, e:
            errmsg = addr[0] + ' ' + str(e) + '\n'
            sys.stderr.write(errmsg)
        result['cert'] = cert
        result['x509'] = x509
        result['components'] = dict(components)
        return result

    def __format__(self, line, parse_result, action_result):
        output = ''
        host, port = parse_result['addr']
        components = action_result['components']
        if self.options.cn:
            output = '{0} {1}'.format(host, components.get('CN', None))
        else:
            for (name, val) in components.iteritems():
                output += '{0} {1}={2}\n'.format(host, name, val)
            if output[-1] == '\n':
                output = output[:-1]
        return output


def main():
    import xnet.tools
    xnet.tools.run(SSLInfoTool)


if __name__ == "__main__":
    main()
    #doctest.testmod()
    #unittest.main()
