#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2013 Krister Hedfors
#

__all__ = ['WebgetTool']


import unittest
import doctest
import sys
import urllib2

from xnet.tools import Tool


class WebgetException(Exception):
    pass


class WebgetTool(Tool):

    __toolname__ = 'webget'
    __itemname__ = 'url'
    __description__ = 'get information from web services'

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

    def __init__(self, *args, **kw):
        super(WebgetTool, self).__init__(*args, **kw)
        self._url = None

    def __parse__(self, line, iterator):
        '''
            only accepts plain urls atm.
        '''
        result = {}
        self._url = url = line.strip()
        if not '://' in url:
            proto = 'http'
            if self.options.https:
                proto = 'https'
            url = proto + '://' + url
        result['url'] = url
        result['host'] = self.options.host or self._get_host(url)
        return result

    def _get_host(self, url):
        host = url.split('://', 1)[1]
        if '/' in host:
            host = host.split('/', 1)[0]
        return host

    def __action__(self, parse_result):
        result = {}
        _host = parse_result['host']
        _url = parse_result['url']
        _response = None
        _code = None
        _msg = None
        _body = None
        #
        #proxies = {}
        #
        request_kwargs = {}
        request_kwargs['url'] = _url
        if self.options.host:
            request_kwargs['headers'] = {'Host': self.options.host}
            _host = self.options.host
        request = urllib2.Request(**request_kwargs)
        #
        # FIXME: broken with proto mismatches etc.
        #
        if self.options.proxy:
            if _url.startswith('http://'):
                request.set_proxy(self.options.proxy, 'http')
            elif _url.startswith('https://'):
                request.set_proxy(self.options.proxy, 'http')
            else:
                errmsg = 'invalid url prefix: ' + _url
                raise WebgetException(errmsg)
            #request.set_proxy(self.options.proxy, 'https')

        read_response = not self.options.code and not self.options.server
        if self.options.format and '{body}' in self.options.format:
            read_response = True

        try:
            _response = urllib2.urlopen(request)
            self._register_cleanup(lambda: _response.close())
            _code = _response.code
            _msg = _response.msg
            if read_response:
                _body = _response.read()
        except urllib2.HTTPError, e:
            _response = None
            _code = e.code
            _msg = e.msg
            if read_response:
                _body = e.read()
        except urllib2.URLError, e:
            errmsg = _url + ' '
            errmsg += e.reason.strerror.replace(' ', '-').replace(',', '-')
            self.set_error(errmsg)
            self.stderr = True
            return None
        #except:
        #    e = str(sys.exc_info())
        #    self.set_error(e)
        #    self.stderr = True
        #    return None
        finally:
            try:
                _response.close()
            except:
                pass
        result['host'] = _host
        result['url'] = _url
        result['response'] = _response
        result['code'] = _code
        result['msg'] = _msg
        result['body'] = _body
        return result

    def __format__(self, line, parse_result, value):
        options = self.options
        url = value['url']
        response = value['response']
        code = value['code']
        msg = value['msg']
        output = ''
        #
        if options.server:
            server = response.headers.get('server', None)
            output = '{0} {1}'.format(url, server)
        elif options.code:
            if options.verbose:
                output = '{0} {1} {2}'.format(url, code, msg)
            else:
                output = '{0} {1}'.format(url, code)
        else:
            output = value['body']
        return output

    @classmethod
    def __format_help__(cls):
        output = '''
Format variables for %s:

 host     - target host
 url      - target URL
 code     - status code
 msg      - status message
 body     - response body

Default format depend on commandline arguments.
        ''' % cls.__toolname__
        return output

    def __timeout__(self):
        return 'timeout {0}\n'.format(self._url)


def main():
    import xnet.tools
    xnet.tools.run(WebgetTool)


if __name__ == "__main__":
    main()
    #doctest.testmod()
    #unittest.main()
