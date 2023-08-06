#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2013 Krister Hedfors
#


def raises(exc, fn, *args, **kw):
    '''
        doesn't catch any exceptions other than exc

        >>> raises(ValueError, int, 'foo')
        True
        >>> raises(ValueError, int, '1')
        False
    '''
    try:
        fn(*args, **kw)
    except exc:
        return True
    return False


def assert_raises(exc, fn, *args, **kw):
    '''
        returns nothing if expected exception is raised,
        raises AssertionError if no exception in raised,
        leave all other exceptions unhandled

        >>> assert_raises(ValueError, int, 'foo')
        >>> raises(AssertionError, assert_raises, Exception, lambda: 1)
        True
    '''
    try:
        fn(*args, **kw)
    except exc:
        return
    raise AssertionError


def _test():
    import doctest
    import unittest
    doctest.testmod()
    unittest.main()

if __name__ == "__main__":
    _test()

