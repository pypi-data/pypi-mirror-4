#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2013 Krister Hedfors
#

__all__ = [
    'pdb',
    'interactive_debugger_on_exception',
]

import sys

global _orig_excepthook


pdb = None
try:
    mypdb = __import__('ipdb')
except ImportError:
    mypdb = __import__('pdb')
pdb = mypdb




def _stacktrace_and_pm(type, value, tb):
    import traceback
    traceback.print_exception(type, value, tb)
    pdb.pm()


_orig_excepthook = None


def interactive_debugger_on_exception(active):
    global _orig_excepthook
    if _orig_excepthook is None:
        _orig_excepthook = sys.excepthook
    if active:
        sys.excepthook = _stacktrace_and_pm
    else:
        assert not _orig_excepthook is None
        sys.excepthook = _orig_excepthook


def _test():
    import doctest
    import unittest
    doctest.testmod()
    unittest.main()

if __name__ == "__main__":
    _test()
