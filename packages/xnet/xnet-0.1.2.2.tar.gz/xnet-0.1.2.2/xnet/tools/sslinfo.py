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
from xnet.net.ipv4 import IPRangeIterator

from xnet.debug import pdb


class SSLInfoException(Exception):
    pass


class SSLInfoTool(Tool):

    __toolname__ = 'sslinfo'
    __itemname__ = 'host'
    __description__ = 'get ssl and certificate information'

    cmdline_options = [
        ('-p', '--port', 'tcp port',
            dict(dest='port')),
        ('', '--cn', 'print common name only',
            dict(dest='cn', action='store_true'))
    ]

    @classmethod
    def print_source(cls):
        cls._print_source(__file__)

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
        self._addr = addr = parse_result['addr']
        try:
            cert = ssl.get_server_certificate(addr)
            cert = self._fix_cert(cert)
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
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
        except Exception, e:
            errmsg = addr[0] + ' ' + str(e) + '\n'
            self.set_error(errmsg)
            self.stderr = True
            return None
        result['host'] = addr[0]
        result['port'] = addr[1]
        result['cert'] = cert
        result['x509'] = x509
        result['notbefore'] = x509.get_notBefore()
        result['notafter'] = x509.get_notAfter()
        result['serial'] = str(x509.get_serial_number()).replace('L', '')
        issuer = x509.get_issuer().get_components()
        result['issuer'] = ''.join('/' + n + '=' + v for (n, v) in issuer)
        subject = x509.get_subject().get_components()
        result['subject'] = ''.join('/' + n + '=' + v for (n, v) in subject)
        subject = dict(subject)
        result['C'] = subject.get('C', '-')
        result['ST'] = subject.get('ST', '-')
        result['O'] = subject.get('O', '-')
        result['OU'] = subject.get('OU', '-')
        result['CN'] = subject.get('CN', '-')
        result['email'] = subject.get('emailAddress', '-')
        return result

    def _fix_cert(self, cert):
        '''
            fix bug which appears on BT5R3 but not OSX Lion
        '''
        assert '-----END CERTIFICATE' in cert
        if not '\n-----END CERTIFICATE' in cert:
            cert = cert.replace('-----END CERTIFICATE',
                                '\n-----END CERTIFICATE')
        return cert

    def __format__(self, line, parse_result, action_result):
        output = ''
        host, port = parse_result['addr']
        x509 = action_result['x509']
        cd = dict(x509.get_subject().get_components())
        #cd = action_result['components_dict']
        if self.options.cn:
            output = '{0} {1}'.format(host, cd.get('CN', None))
        else:
            for (name, val) in cd.iteritems():
                output += '{0} {1}={2}\n'.format(host, name, val)
            if output[-1] == '\n':
                output = output[:-1]
        return output

    def __timeout__(self):
        return 'timeout {0} {1}\n'.format(*self._addr)

    @classmethod
    def __format_help__(cls):
        name = cls.__toolname__
        output = '''
Format variables available for %s.
(default format is complex and not reproducable from commandline)

 host        - target host
 port        - target port
 notbefore   - not valid before
 notafter    - not valid after
 serial      - cert serial number
 issuer      - issuer common name, organizational unit, ...
 subject     - subject common name, organizational unit, ...
 C           - subject country
 ST          - subject state
 O           - subject organization
 OU          - subject organizational unit
 CN          - subject common name
 email       - subject email address
        ''' % cls.__toolname__
        return output


def main():
    import xnet.tools.run
    xnet.tools.run.run(SSLInfoTool)


if __name__ == "__main__":
    main()
    #doctest.testmod()
    #unittest.main()
