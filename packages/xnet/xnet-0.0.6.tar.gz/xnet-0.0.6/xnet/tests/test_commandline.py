#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2013 Krister Hedfors
#


import unittest
import subprocess
import StringIO


class testcase(object):
    def __init__(self, argv, expect_exitcode, expect_stdout, expect_stderr=''):
        self._argv = argv
        self._expect_exitcode = expect_exitcode
        self._expect_stdout = expect_stdout
        self._expect_stderr = expect_stderr

    def test_commandline(self):
        stdout = StringIO.StringIO()
        stderr = StringIO.StringIO()
        exitcode = subprocess.call(argv, stdout=stdout, stderr=stderr)
        self.assertEqual(exitcode, self._expect_exitcode)
        self.assertEqual(stdout, self._expect_stdout)
        self.assertEqual(stderr, self._expect_stderr)

class Test_iprange(unittest.TestCase, CommandlineTester):
    def __init__(self):
        unittest.TestCase.__init__(self)


def _test():
    import doctest
    import unittest
    doctest.testmod()
    unittest.main()

if __name__ == "__main__":
    if 0:  # DISABLED
        _test()
