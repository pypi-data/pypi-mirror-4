#!/usr/bin/env python

from __future__ import print_function

import socket
import asyncore
import argparse as arg
import os, sys, atexit

from os import mkfifo, system, unlink, path
from sys import argv, stderr, modules

from functools import partial
from importlib import import_module
from pkg_resources import load_entry_point
from multiprocessing import Process, Pipe

from daemon import DaemonContext
from lockfile import FileLock


usage = '''\
Usage: %(prog)s [-hvdpws] socket [mod, ...]

Options:
  -h, --help           show this help message and exit
  -v, --version        show version and exit
  -d, --daemonize      run in background (default: no)
  -p, --pidfile        pid file to use if running as a daemon
  -w, --workers <num>  worker processes to start (default: 5)
  -s, --spare <num>    spare worker processes to maintain (default: 3)

Arguments:
  socket               location of AF_UNIX socket
  mod*                 modules to pre-import in every worker

Examples:
  %(prog)s -f launcher.sock numpy PySide.QtCore PySide.QtGui
  echo -n "module path.to.module" | nc -U launcher.sock
'''


def parseopt():
    p = arg.ArgumentParser(usage=usage, add_help=False)
    p.formatter_class.format_help = lambda x: usage % {'prog' : p.prog}

    p.add_argument('-h', '--help', action='store_true')
    p.add_argument('-v', '--version', action='version', version='0.1.0')
    p.add_argument('-w', '--workers', type=int, default=5)
    p.add_argument('-d', '--daemonize', action='store_true')
    p.add_argument('-p', '--pidfile', default='/tmp/python-module-launcher.pid')
    p.add_argument('-s', '--spare', type=int, default=3)

    p.add_argument('socket')
    p.add_argument('imports', nargs=arg.REMAINDER, default=None)

    return p, p.parse_args()


class Worker(Process):
    def __init__(self, imports=None):
        super(Worker, self).__init__()

        self.imports = imports
        self.pipe_parent, self.pipe_child = Pipe()

    def run_entrypoint(self, dist, group, name, *args):
        print('+ running entrypoint "{} {} {}" with args "{}"' \
              .format(dist, group, name, args))
        sys.argv = [name] ; sys.argv.extend(args)

        return load_entry_point(dist, group, name)()

    def run_file(self, path, *args):
        raise NotImplementedError

        print('+ running file "{}" with args "{}"'.format(path, args))
        with open(path, 'r') as fh:
            exec(fh.read(), globals(), locals())

    def run_module(self, modpath, *args):
        print('+ running module "{}" with args "{}"'.format(modpath, args))

        sys.argv = ['python'] ; sys.argv.extend(args)
        import_module(modpath)

    def _run(self):
        fileno = [self.pipe_child.fileno()]

        for name in self.imports:
            import_module(name)

        while True:
            res = self.pipe_child.recv()
            if not res: continue

            res = res.split(' ')
            command = res[0]

            if command == 'entrypoint':
                self.run_entrypoint(*res[1:])
            elif command == 'file':
                self.run_file(res[1])
            elif command == 'module':
                self.run_module(res[1])
            else:
                print('unknown command: {}'.format(' '.join(res)))

    def run(self):
        try: self._run()
        except KeyboardInterrupt: pass


class PreforkPool(object):
    def __init__(self, start, spare, imports):
        self.start = start
        self.spare = spare
        self.imports = imports

        self.pool = []

        print('+ starting {:d} worker processes'.format(self.start), file=stderr)
        print('+ will maintain at least {:d} spare processes at all times'.format(self.spare), file=stderr)
        for i in range(self.start):
            worker = Worker(self.imports)
            worker.start()
            self.pool.append(worker)

    def maybeforknew(self):
        print('+ current workers: %d' % len(self.pool), file=stderr)
        if len(self.pool) <= self.spare:
            for i in range(self.spare):
                worker = Worker(self.imports)
                worker.start()
                self.pool.insert(0, worker)

    def run(self, command):
        worker = self.pool.pop()
        worker.pipe_parent.send(command)
        self.maybeforknew()


class DispatchHandler(asyncore.dispatcher_with_send):
    def readable(self):
        return True

    def writable(self):
        return True

    def handle_write(self):
        pass

    def handle_read(self):
        command = self.recv(8192).rstrip()
        if command:
            self.pool.run(command)


class Dispatcher(asyncore.dispatcher):
    def __init__(self, socket_path, pool):
        asyncore.dispatcher.__init__(self)

        self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(socket_path)
        self.listen(50)

        self.pool = pool

    def handle_accept(self):
        s, addr = self.accept()
        handler = DispatchHandler(s)
        handler.pool = self.pool


def cleanup(socket_path):
    if path.exists(socket_path):
        print('\n+ removing AF_UNIX socket: {}'.format(socket_path))
        unlink(socket_path)


def _main(opts):
    atexit.register(partial(cleanup, opts.socket))

    pool = PreforkPool(opts.workers, opts.spare, opts.imports)
    dispatcher = Dispatcher(opts.socket, pool)

    try: asyncore.loop()
    except KeyboardInterrupt: pass


def main():
    parser, opts = parseopt()

    if path.exists(opts.socket):
        print('+ socket file {} already exists'.format(opts.socket))
        exit(1)

    if opts.help:
        print(usage, file=stderr)
        exit(0)

    if opts.daemonize:
        context = DaemonContext(pidfile=FileLock(opts.pidfile))
        print('+ daemonizing - pid file {}'.format(context.pidfile.path))
        with context:
             _main(opts)
    else:
        _main(opts)


if __name__ == '__main__':
    main()
