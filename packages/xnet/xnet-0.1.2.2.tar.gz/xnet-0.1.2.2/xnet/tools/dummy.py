#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2013 Krister Hedfors
#

import gevent
from xnet.tools import Tool


class DummyTool(Tool):

    __description__ = 'dummy to use for testing'
    __itemname__ = 'dummy'

    cmdline_options = [
        ('', '--sleep', 'gevent.sleep() for each input, treat items as float',
            dict(dest='sleep', action='store_true')),
    ]

    @classmethod
    def print_source(cls):
        cls._print_source(__file__)

    def __parse__(self, line, iterator):
        item = line.strip()
        return {'item': item}

    def __action__(self, parse_result):
        item = parse_result['item']
        result = {}
        if self.options.sleep:
            sleeptime = float(item)
            gevent.sleep(sleeptime)
            result = {'sleeptime': sleeptime}
        return result

    def __format__(self, line, parse_result, action_result):
        output = ''
        if self.options.sleep:
            sleeptime = action_result['sleeptime']
            output += 'slept:{0} '.format(sleeptime)
        return output


def main():
    import xnet.tools.run
    xnet.tools.run.run(DummyTool)


if __name__ == "__main__":
    main()
    #doctest.testmod()
    #unittest.main()
