#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2011 Krister Hedfors
#


import unittest
import doctest

import sys
import os
import optparse
import itertools
import time
import fcntl

import gevent
import gevent.pool
import gevent.monkey
from gevent.socket import wait_read

from xnet.debug import pdb

gevent.monkey.patch_all(thread=False)

DEVELOPMENT = 1

if DEVELOPMENT:
    #
    # FIXME: FULHACK dev
    #
    import os
    from os.path import join, abspath

    sys.path.insert(0, abspath(join(os.getcwd(), '../../')))

import xnet.debug


class XNetOptionParser(optparse.OptionParser):
    '''
        Provides some common options and an interface to add nicely formatted
        local options for each tool. Each local option is defined as a
        four-tuple of (shortoption, longoption, helptext, keyword-dict).

        Example follows below:

        class LocalOptionParser(OptionParserBase):
            local_options = [
                ('-p', '--port', 'Port to state.',
                    dict(dest='port'))
            ]
    '''
    def __init__(self, local_options, **kw):
        optparse.OptionParser.__init__(self, **kw)
        self.add_option('', '--test', dest='test', action='store_true',
                        help='run tests')
        self.add_option('', '--pdb', dest='pdb', action='store_true',
                        help='enable interactive pdb debugging on exceptions')
        self.add_option('-y', '--parallelism', dest='parallelism', metavar='n',
                        help='set parallelism (default 128)')
        self.add_option('-r', '--read', dest='read', metavar='path',
                        help='read input from file')
        self.add_option('-w', '--wait', dest='wait', metavar='nsecs',
                        help='wait at most nsecs seconds for actions to complete')
        self.add_option('-i', '--interval', dest='interval', metavar='nsecs',
                        help='time interval between each action ')
        self.add_option('-T', '--supress-timeout', dest='supress_timeout',
                        help='supress messages from tasks timing out', action='store_true')
        self.add_option('-f', '--format', dest='format', metavar='fmt',
                        help='specify output format manually, use {v0}, {v1},.. as placeholders')
        self.add_option('', '--split-output', dest='split_output', metavar='base',
                        help='produce one output file for each piece of input')
        self.add_option('', '--split-tee', dest='split_tee', metavar='base',
                        help='like --split-output but also print to stdout')
        self.add_option('-v', '--verbose', dest='verbose',
                        help='verbose output', action='store_true')
        self._load_local_options(local_options)

    def _load_local_options(self, local_options):
        for (short_, long_, help_, kw) in local_options:
            help_ = '* ' + help_  # mark tool-unique options
            self.add_option(short_, long_, help=help_, **kw)


def get_action_usage():
    _action_usage = ''
    for tup in _available_actions:
        name = tup[0]
        desc = available_actions[name].__description__
        line = ' '
        line += name
        line += ' ' * (11 - len(name))
        line += desc
        line += '\n'
        _action_usage += line
    return _action_usage


__usage__ = """

    $$$ Merry Xnet! $$$

 $ {{tool}} [options] item1 item2 ...
 $ {{tool}} [options] -r itemfile.txt
 $ cat itemsfile.txt | {{tool}} [options] -
"""


def top_usage():
    output = __usage__
    output += '\n'
    output += 'Available tools:\n'
    output += get_action_usage()
    return output


def print_error(errval):
    errmsg = str(errval)
    if not errmsg.strip():
        errmsg = 'no-error-set\n'
    if not errmsg[-1] == '\n':
        errmsg += '\n'
    sys.stderr.write(errmsg)


def stdin_disperser_greenlet(pool):
    '''
        loop forever feeding active greenlets with data
        read from stdin.
    '''
    done = False
    fcntl.fcntl(sys.stdin, fcntl.F_SETFL, os.O_NONBLOCK)
    while not done:
        wait_read(sys.stdin.fileno())
        try:
            data = sys.stdin.read()
        except:
            raise
        done = (data == '')
        for greenlet in pool:
            obj = greenlet._run  # fulhack
            if not hasattr(obj, '__massage__'):  # fulhack
                continue
            #obj.feed_stdin(data)  # put in queue or list
            os.write(obj._stdin_pipe[1], data)


def _get_output_filepath(a, base):
    #
    # item is the result of some specific processing
    # and may contain arbitrary meta characters
    # which should not affect the file system path
    # where the output file is created.
    #
    item = str(a._item)
    item = item.replace('/', '__')
    item = item.replace('\\', '--')
    path = base + '_' + item
    return path

def run(ToolImplementation, stdin_data_arg=None, tool_reads_stdin=False):
    try:
        return _run(ToolImplementation, stdin_data_arg, tool_reads_stdin)
    except KeyboardInterrupt:
        return 1
    

def _run(ToolImplementation, stdin_data_arg, tool_reads_stdin):
    '''
            tool_reads_stdin - tool uses stdin for other purpose than
                               to obtain startup arguments
    '''
    args = sys.argv[:]
    action_name = args[0]
    #args = list(args)[1:]

    _E_INVALID_ARGUMENT_STDIN = \
        '-: Invalid argument, target hosts may not be specified on stdin.'

    _usage = __usage__.replace('{{tool}}', action_name)
    if hasattr(ToolImplementation, '__itemname__'):
        itemname = ToolImplementation.__itemname__
        _usage = _usage.replace('item', itemname)
    parser = XNetOptionParser(ToolImplementation.cmdline_options, usage=_usage)
    (opt, args) = parser.parse_args(args)
    cmdlineinputs = args[1:]

    if opt.pdb:
        xnet.debug.interactive_debugger_on_exception(True)

    #
    # chain input sources, handle options
    # precedence order: cmdline, -r, stdin
    # NOTE that if stdin_data_arg is not None,
    # stdin is not used as a source for items.
    #
    _inputs = []
    if '-' in cmdlineinputs:
        if not stdin_data_arg is None and not tool_reads_stdin:
            raise Exception(_E_INVALID_ARGUMENT_STDIN)
        cmdlineinputs.remove('-')
        _inputs.append(sys.stdin)
    if opt.read:
        f = open(opt.read)
        _inputs.insert(0, f)
    if len(cmdlineinputs):
        _inputs.insert(0, cmdlineinputs)
    inputchain = itertools.chain(*_inputs)

    _parallelism = 128
    if not opt.parallelism is None:
        _parallelism = int(opt.parallelism)

    _wait = None
    if not opt.wait is None:
        _wait = float(opt.wait)

    _interval = 0.0
    if not opt.interval is None:
        _interval = float(opt.interval)

    _outfile = sys.stdout
    #
    # main loop
    #

    pool = gevent.pool.Pool(_parallelism)
    actions = []  # all spawned actions
    greenlets = []

    waitkill_greenlets = []

    def waitkill(g):
        gevent.sleep(_wait)
        if not g.ready():
            gevent.kill(g)

    inputchain = ToolImplementation.__massage__(inputchain)

    kwargs = {}
    if not stdin_data_arg is None:
        kwargs[stdin_data_arg] = sys.stdin.read()

    if tool_reads_stdin:
        pool.spawn(stdin_disperser_greenlet, pool)

    #
    # FIXME: --wait only activated after all greenlets
    # are spawned, so inputs larger than poolsize
    # are unaffected.
    # FIXME: output is only generated when all greenlets
    # are done; should be as real time as possible in order
    #
    _t = 0.0
    for (i, line) in enumerate(inputchain):
        pool.wait_available()
        a = ToolImplementation(opt, **kwargs)
        actions.append(a)
        #
        # handle interval and spawn
        #
        _this_interval = _interval - (time.time() - _t)
        if _this_interval > 0:
            gevent.sleep(_this_interval)
        g = pool.spawn(a, line, inputchain)

        if not _wait is None:
            wk = gevent.spawn(waitkill, g)
            waitkill_greenlets.append(wk)
            if len(waitkill_greenlets) > 2 * _parallelism:
                finished, waitkill_greenlets = waitkill_greenlets[:_parallelism],\
                    waitkill_greenlets[_parallelism:]
                t = time.time()
                gevent.joinall(waitkill_greenlets)
                tdiff = time.time() - t
                print 'waitkill jointime:', tdiff

        _t = time.time()
        greenlets.append(g)

    timeout = _wait
    if not timeout is None:
        timeout += 1  # one second of grace time for greenlets to exit
    gevent.joinall(greenlets, timeout=timeout)
    not_done = filter(lambda g: (not g.ready()), greenlets)
    if len(not_done) > 0 and not _wait is None:
        print 'not_done has contents inspite of _wait and grace time'
        print not_done
    gevent.killall(not_done, block=True)
    gevent.joinall(not_done)

    #
    # also assert all waitkill_greenlets are done
    #

    if opt.split_tee:
        opt.split_output = opt.split_tee

    for a in actions:
        outfile = _outfile
        if opt.split_output:
            path = _get_output_filepath(a, opt.split_output)
            outfile = open(path, 'wb')

        if not a.error is None:
            print_error(a.error)
        elif not a.finished:
            if not opt.supress_timeout:
                msg = a.__timeout__()
                if a.stderr:
                    outfile = sys.stderr
                if not msg is None:
                    outfile.write(msg)
                    if opt.split_tee and not a.stderr:
                        _outfile.write(msg)
        else:
            msg = str(a)
            #
            # ignore empty output from Tool.__format__()
            #
            if len(msg) == 0:
                continue
            msg += '\n'
            if a.stderr:
                outfile = sys.stderr
            outfile.write(msg)
            if opt.split_tee and not a.stderr:
                _outfile.write(msg)

        if opt.split_output:
            outfile.close()


if __name__ == "__main__":
    if '--test' in sys.argv:
        sys.argv.remove('--test')
        doctest.testmod()
        unittest.main()
    #else:
    #    main(*sys.argv)
