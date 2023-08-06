#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2013 Krister Hedfors
#

__all__ = [
    'Tool',  # refactor >> InputHandler
    'run',
]

import unittest
import doctest
import re

from gevent import Timeout

from xnet.tools.run import run


class ToolException(Exception):
    pass


class NotImplementedException(ToolException):
    pass


class InvalidParseResult(ToolException):
    pass


class InvalidToolResult(ToolException):
    pass


class NoResultAvailable(ToolException):
    pass


class BadFormat(ToolException):
    pass


class Formatter(object):
    '''
        Formatter
            Behaves as string.format but allows loops.
            >>> fmt = Formatter('for i in col: yay {i}, ')
            >>> fmt.format(col=[1, 2, 3])
            'yay 1, yay 2, yay 3, '
    '''

    _loop_stmt = re.compile(r'^for (?P<varname>\w+) in (?P<colname>\w+):(?P<text>.*)')

    def __init__(self, fstr):
        self._fstr = fstr

    def format(self, *args, **kw):
        return self._render(self._fstr, *args, **kw)

    def _render(self, fstr, *args, **kw):
        m = self._loop_stmt.match(fstr)
        if m:
            return self._render_loop(m.group('varname'), m.group('colname'),
                                     m.group('text'), *args, **kw)
        return self._format(fstr, *args, **kw)

    def _render_loop(self, varname, colname, text, *args, **kw):
        col = kw[colname]
        output = ''
        for i in col:
            kw[varname] = i
            #
            # make this statement:
            #  'for i in x: blabla..'
            # behave as this:
            #  'for i in x:blabla..'
            #
            if len(text) > 1 and text[0] == ' ':
                text = text[1:]

            output += self._render(text, *args, **kw)
        return output

    def _format(self, fstr, *args, **kw):
        fstr = fstr.replace('\\n', '\n')
        fstr = fstr.replace('\\t', '\t')
        return fstr.format(*args, **kw)


class Test_Formatter(unittest.TestCase):

    def test_basic(self):
        f = Formatter('asd {0} foo {BAR}')
        r = f.format(123, BAR='bar')
        self.assertEqual(r, 'asd 123 foo bar')

    def test_loop_1(self):
        f = Formatter('for n in numbers: {n},')
        r = f.format(numbers=[1, 2, 3])
        self.assertEqual(r, '1,2,3,')

    def test_loop_2(self):
        f = Formatter('for c in chars: for n in numbers: {c}{n},')
        r = f.format(chars=['a', 'b'], numbers=[1, 2, 3])
        self.assertEqual(r, 'a1,a2,a3,b1,b2,b3,')


class ToolError:
    codes = dict(
        CustomError=0,
        ParseFailed=1,
        ActionFailed=2,
    )
    CustomError = 0
    ParseFailed = 1
    ActionFailed = 2

    def __init__(self, code, message=None):
        self.code = code
        self.message = message or self.strerror

    @property
    def strerror(self):
        return self.codes[self.code]


class Tool(object):
    '''
        Must implement __action__, all other methods are optional.
        By default, __action__ is called with a single-value dict:
            {'item': item}

        Implementations of __parse__, __action__, __filter__ or __format__
        may use set_error(...) to define arbitrary errors, later readable
        through the 'error' property, which if evaluates as True means
        that action value is not available.

        @classmethod
        __massage__(iterator)
            input: iterator with all input
            output: generate (yield) items to __parse__()

                Used to split or skip certain input items.

        __parse__(item)
            input: item or line of input
            output: dict or None

                None prevents all following method calls and doesn't produce output.

        __action__(parse_result)
            input: dict
            output: dict or None

                None prevents all following method calls and doesn't produce output.
                Each value in output dict should have a corresponding 'vN' value
                where N is the precedence order of the value. This makes
                user-controlled output formatting easier.
                Example:
                    d['v0'] = d['host'] = '1.2.3.4'
                    d['v1'] = d['port'] = '80'

        __filter__(action_result)
            input: dict
            output: bool

                Used to limit output depending on cmdline options, for
                instance.

        __format__(line, parse_result, action_result)
            input: str, dict, dict
            output: str or None

                None prevents all following actions and doesn't produce output.
                Terminating newline may be omitted to produce output from multiple
                invoked action on a single line.

        __timeout__()
            output: str or None

                Used to produce output if user-controlled timeout occurrs (-w)
                when __format__() cannot be used due to lack of required input.
                Default __timeout__() returns None.
                May set self.stderr to True to force output to stderr.


    '''
    PRE_CALL = 0
    POST_CALL = 1

    MODE_SINGLE = 0x00
    MODE_GEVENT = 0x01

    def __init__(self, options, mode=MODE_GEVENT):
        self._options = options
        self._mode = mode
        self._parse_result = None
        self._action_result = None
        self._state = self.PRE_CALL
        self._error = None
        self._cleanup_funcs = []
        self.stderr = False  # if True, print output to stderr
        self._validate_implementations()

    def _validate_implementations(self):
        #
        # assert __massage__ is classmethod generator
        #
        pass

    def __call__(self, item, iterator):
        '''
            always returns self
        '''
        result = self
        timeout = None
        if not self.options.wait is None:
            wait = float(self.options.wait)
            timeout = Timeout(wait)
        try:
            try:
                result = self._call(item, iterator)
            except Timeout, t:
                if t is not timeout:
                    raise
            finally:
                if timeout:
                    timeout.cancel()
        finally:
            self._do_cleanup()
        return result

    def _call(self, item, iterator):
        '''
            FIXME: how handle empty result from __parse__?

            always returns self
        '''
        self._item = item  # used in filename by --split-output
        parse_result = None
        action_result = None
        #
        # sanity
        #
        assert self._state == self.PRE_CALL
        assert self._error is None
        #
        # __parse__
        #
        parse_result = self.__parse__(item, iterator)
        if parse_result is None or not self.error is None:
            if self.error is None:
                code = ToolError.ParseFailed
                error = ToolError(code)
                self.set_error(error)
            return None
        if not isinstance(parse_result, dict):
            msg = '__parse__() did not return a dict subclass.'
            raise InvalidParseResult(msg)
        #
        # __action__
        #
        action_result = self.__action__(parse_result)
        if action_result is None or not self.error is None:
            if self.error is None:
                code = ToolError.ActionFailed
                error = ToolError(code)
                self.set_error(error)
            return None
        if not isinstance(action_result, dict):
            msg = '__action__() did not return a dict subclass.'
            raise InvalidToolResult(msg)
        #
        # __filter__
        #
        filter_result = self.__filter__(action_result)
        if not filter_result:
            if not self.error is None:
                msg = '__filter__() may not set error.'
                msg += '. Error set: ' + str(self.error)
                raise ToolException(msg)
            action_result = None
        self._parse_result = parse_result
        self._action_result = action_result
        self._state = self.POST_CALL
        return self

    def _register_cleanup(self, func):
        self._cleanup_funcs.append(func)

    def _do_cleanup(self):
        for func in self._cleanup_funcs:
            func()

    @property
    def value(self):
        '''
            value()
                value may be None only if __action__() succeeds but
                __filter__() returns False.
        '''
        if not self.error is None:
            errmsg = 'value not available, check error'
            raise ToolException(errmsg)
        value = self._action_result
        return value

    @property
    def error(self):
        return self._error

    def set_error(self, error):
        self._error = error

    def __str__(self):
        '''
            __str__()
                Relies on user-implemented __format__().
        '''
        if not self.finished:
            errmsg = 'action not done yet'
            raise NoResultAvailable(errmsg)
        if self._action_result is None:
            errmsg = 'result has been rejected by __filter__()'
            raise NoResultAvailable(errmsg)
        if self.options.format:
            output = self._user_format(
                self.options.format,
                self._action_result
            )
        else:
            output = self.__format__(
                self._item,
                self._parse_result,
                self._action_result)
        return output

    def _user_format(self, fmt, fmt_kwargs):
        '''
            fmt is commandline argument -f
        '''
        output = ''
        try:
            output = Formatter(fmt).format(**fmt_kwargs)
        except KeyError, e:
            bad_key = e.args[0]
            valid_keys = ', '.join(fmt_kwargs.keys())
            errmsg = "invalid format key '{0}', valid keys are: {1}".format(
                bad_key,
                valid_keys
            )
            raise BadFormat(errmsg)
        return output

    def __getitem__(self, name):
        if not self._action_result:
            msg = 'Tool has not yet produced a result.'
            raise NoResultAvailable(msg)
        return self._action_result[name]

    @property
    def options(self):
        return self._options

    @property
    def finished(self):
        assert self._state in (self.PRE_CALL, self.POST_CALL)
        return self._state == self.POST_CALL

    #
    # __massage__ must return iterator of items
    #
    @classmethod
    def __massage__(self, iterator):
        return iterator

    #
    # __parse__ must return either a dict or None.
    #
    def __parse__(self, item, iterator):
        raise NotImplementedException('Please implement Tool.__parse__.')

    #
    # __action__ is called with whatever __parse__ returned.
    #
    def __action__(self, parse_result):
        raise NotImplementedException('Please implement Tool.__action__.')

    #
    # __format__ must be implemented in order to make __str__() work.
    #
    def __format__(self, item, parse_result, action_result):
        raise NotImplementedException('Please implement Tool.__format__.')

    #
    # __filter__ may return None to filter items
    #
    def __filter__(self, action_result):
        return action_result

    #
    # __timeout__ is used instead of __format__ when user-controlled
    #             timeout occurrs.
    #
    def __timeout__(self):
        return None


class Test1(unittest.TestCase):
    def test_file(self):
        pass


if __name__ == "__main__":
    doctest.testmod()
    unittest.main()
