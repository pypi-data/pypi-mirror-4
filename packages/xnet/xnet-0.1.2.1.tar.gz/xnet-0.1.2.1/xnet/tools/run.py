#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2013 Krister Hedfors
#


import unittest
import doctest

import sys
import os
import os.path
import optparse
import itertools
import time
import fcntl

import gevent
import gevent.pool
import gevent.monkey
from gevent.socket import wait_read

import xnet.tools
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
        self.add_option('', '--print-source', dest='print_source', action='store_true',
                        help='print source code of tool')
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
                        help='specify output format, see --format-help for info')
        self.add_option('', '--format-help', dest='format_help', action='store_true',
                        help='print output format help')
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
    path = base + item
    return path


def run(ToolImplementation, tool_reads_stdin=False):
    try:
        return _run(ToolImplementation, tool_reads_stdin)
    except KeyboardInterrupt:
        return 1
    

def _run(ToolImplementation, tool_reads_stdin):
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

    if opt.print_source:
        ToolImplementation.print_source()
        return

    #
    # chain input sources, handle options
    # precedence order: cmdline, -r, stdin
    #
    _inputs = []
    if '-' in cmdlineinputs:
        if tool_reads_stdin:
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

    if opt.format_help:
        print ToolImplementation.__format_help__()
        sys.exit(0)

    if opt.split_tee:
        opt.split_output = opt.split_tee

    pool = gevent.pool.Pool(_parallelism)
    actions = []  # all spawned actions
    greenlets = []

    wkpool = None
    if _wait:
        wkpool = gevent.pool.Pool(_parallelism)

    def waitkill(g, killtime):
        sleeptime = killtime - time.time()
        #print 'waitkill', sleeptime
        if sleeptime > 0:
            gevent.sleep(sleeptime)
        if not g.ready():
            gevent.kill(g)
            g.join()

    inputchain = ToolImplementation.__massage__(inputchain)

    kwargs = {}

    if tool_reads_stdin:
        gevent.spawn(stdin_disperser_greenlet, pool)


    _t = 0.0
    killtime = 0
    for (i, line) in enumerate(inputchain):
        action = ToolImplementation(opt, **kwargs)
        pool.wait_available()
        if _wait:
            killtime = time.time() + _wait
        g = pool.spawn(action, line, inputchain)
        g.action = action
        greenlets.append(g)
        if _wait:
            wkpool.wait_available()
            wk = wkpool.spawn(waitkill, g, killtime)

        #
        # handle finished actions
        #
        while len(greenlets) and greenlets[0].ready():
            action = greenlets[0].action
            output_action_result(action, opt, _outfile)
            del action
            del greenlets[0]

        #
        # handle interval
        #
        _this_interval = _interval - (time.time() - _t)
        if _this_interval > 0:
            gevent.sleep(_this_interval)
        _t = time.time()


    if wkpool:
        wkpool.join()
    gevent.joinall(greenlets) #, timeout=timeout)
    not_done = filter(lambda g: (not g.ready()), greenlets)
    if len(not_done) > 0 and not _wait is None:
        print 'ERROR: not_done has contents inspite of _wait and grace time'
        print not_done

    #
    # Force-kill greenlets that didn't die in spite of 1 sec of grace time.
    #
    gevent.killall(not_done, block=True)
    gevent.joinall(not_done)

    #
    # print results
    #
    for g in greenlets:
        action = g.action
        output_action_result(action, opt, _outfile)
        del action


def output_action_result(a, opt, _outfile):
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
            return
        msg += '\n'
        if a.stderr:
            outfile = sys.stderr
        outfile.write(msg)
        if opt.split_tee and not a.stderr:
            _outfile.write(msg)

    _outfile.flush()
    if not outfile is _outfile:
        outfile.flush()

    if opt.split_output:
        outfile.close()



__xnet_usage__ = '''

    $$$ Merry Xnet! $$$

The following xnet tools are available:
 iprange   - IP range enumerator
 resolv    - hostname resolver
 tcpstate  - port scanner
 netcats   - netcatish
 webget    - web client
 sslinfo   - SSL info harvester
 iissn     - IIS shortname enumeration

Analogous commands:
$ xnet iprange ...
$ iprange ...

Develop your own xnet tools:
$ existing_xnet_tool --print-source > newtool.py
$ vim newtool.py
$ xnet newtool.py ...
'''


def main():
    args = sys.argv[:]

    if len(args) < 2:
        print __xnet_usage__
        return

    ToolImplementation = None

    toolname = args[1]
    if toolname.endswith('.py'):
        if not toolname.startswith('/'):
            toolname = os.path.abspath(toolname)
        if not os.path.exists(toolname):
            print 'File not found:', toolname
        folder = os.path.dirname(toolname)
        if len(folder):
            sys.path.insert(0, folder)
        modulename = os.path.basename(toolname).rsplit('.', 1)[0]
        toolmodule = __import__(modulename)
        sys.path = sys.path[1:]
        for name in dir(toolmodule):
            val = getattr(toolmodule, name)
            found = False
            try:
                if issubclass(val, xnet.tools.Tool):
                    found = True
            except TypeError:
                pass
            if found and not val is xnet.tools.Tool:
                if not ToolImplementation is None:
                    errmsg = 'Multiple Tool implementations in {0}: {1}, {2}'
                    errmsg = errmsg.format(toolname, ToolImplementation, val)
                    print errmsg
                    sys.exit(1)
                ToolImplementation = val
         
    if not ToolImplementation:    
        if toolname == 'iprange':
            from xnet.tools.iprange import IPRangeTool as ToolImplementation

    if not ToolImplementation:
        print 'Tool not found:', toolname
        sys.exit(1)

    sys.argv = sys.argv[1:]

    result = run(ToolImplementation)
    return result


if __name__ == "__main__":
    main()
    #if '--test' in sys.argv:
    #    sys.argv.remove('--test')
    #    doctest.testmod()
    #    unittest.main()
    #else:
    #    main(*sys.argv)
