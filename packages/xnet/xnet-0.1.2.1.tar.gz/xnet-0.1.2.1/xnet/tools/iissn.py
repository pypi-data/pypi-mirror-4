#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2011 Krister Hedfors
#

__all__ = ['IISShortnameTool']


import unittest
import doctest

from webget import WebgetTool
from xnet.net.ipv4 import IPRangeIterator


class IISShortnameTool(WebgetTool):

    __description__ = 'identify IIS shortname functionality'
    __toolname__ = 'iissn'
    __itemname__ = 'url'

    cmdline_options = [
        ('-s', '--server', 'print server header',
            dict(dest='server', action='store_true')),
        ('-S', '--https', 'default to https when protocol is missing',
            dict(dest='https', action='store_true')),
        ('', '--host', 'specify Host header manually',
            dict(dest='host')),
        ('', '--proxy', 'use this proxy for all protocols',
            dict(dest='proxy')),
        ('', '--code', 'only print response code',
            dict(dest='code', action='store_true')),
    ]

    @classmethod
    def print_source(cls):
        cls._print_source(__file__)

    def __init__(self, *args, **kw):
        super(IISShortnameTool, self).__init__(*args, **kw)
        self._url = None

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
        result = super(IISShortnameTool, self).__parse__(line, iterator)
        self._url = url = result['url']
        if not url.endswith('/'):
            url += '/'
        url1 = url + '*~1*/.aspx'
        url2 = url + 'poipoipoi*~1*/.aspx'
        result['url'] = url
        result['url1'] = url1
        result['url2'] = url2
        return result

    def __action__(self, parse_result):
        '''
            v0 = url
            v1 = vulnerable
        '''
        host = parse_result['host']
        url = parse_result['url']
        url1 = parse_result['url1']
        url2 = parse_result['url2']
        result1 = super(IISShortnameTool, self).__action__(
            {'host': host, 'url': url1})
        result2 = super(IISShortnameTool, self).__action__(
            {'host': host, 'url': url2})
        vulnerable = False
        code1 = result1['code']
        code2 = result2['code']
        if type(code1) is int and type(code2) is int:
            vulnerable = code1 != code2
        result = {}
        result['host'] = host
        result['url'] = result['v0'] = url
        result['vulnerable'] = result['v1'] = vulnerable
        result['url1'] = url1
        result['url2'] = url2
        result['code1'] = result1['code']
        result['code2'] = result2['code']
        result['msg1'] = result1['msg']
        result['msg2'] = result2['msg']
        result['body1'] = result1['body']
        result['body2'] = result2['body']
        return result

    def __format__(self, line, parse_result, value):
        host = value['host']
        url = value['url']
        vulnerable = value['vulnerable']
        code1 = value['code1']
        code2 = value['code2']
        output = ''
        #
        #if options.server:
        #elif options.code:
        if self.options.verbose or self.options.code:
            output = '{0} {1} {2} {3} {4}'.format(
                url,
                host,
                vulnerable,
                code1,
                code2,
            )
        else:
            output = '{0} {1}'.format(
                url,
                vulnerable,
            )
        return output

    @classmethod
    def __format_help__(cls):
        name = cls.__toolname__
        output = '''
Format variables for %s:

 url         - url to probe
 host        - Host header
 vulnerable  - boolean result
 code1       - response code from url+'*~1*/.aspx'
 code2       - response code from url+'poipoipoi*~1*/.aspx'

Default format:
 '{url} {host} {vulnerable} {code1} {code2}'

Default format if verbose (-v):
 '{url} {vulnerable}'
        ''' % cls.__toolname__
        return output

    def __timeout__(self):
        return 'timeout {0}\n'.format(self._url)


def main():
    import xnet.tools.run
    xnet.tools.run.run(IISShortnameTool)


if __name__ == "__main__":
    main()
    #doctest.testmod()
    #unittest.main()
