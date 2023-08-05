# -*- coding: UTF-8 -*-
# vim: fileencoding=UTF-8 filetype=python ff=unix et ts=4 sw=4 sts=4 tw=120
#
# Copyright (c) 2010, Christer Sjöholm -- hcs AT furuvik DOT net
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
'''
'''
from __future__ import absolute_import

import hcs_utils.lock
import os
import signal
import sys
import time


def send_sigterm(pid):
    '''
    Default implementation of stop signaller
    '''
    os.kill(pid, signal.SIGTERM)


class Daemon(object):
    '''
    Inspired by the Supay library.
    '''

    def __init__(self, name, run, pid_dir='/var/run'):
        '''
        name: name of daemon, used for the lockfile and in printed messages.
        run: callable to call when staring daemon (this is what executes in
             the daemon)
        '''
        self.name = name
        self.run = run
        self.lockfile = os.path.join(pid_dir, '{0}.pid'.format(name))
        self.lock = hcs_utils.lock.Lock(self.lockfile)

    def start(self, foreground=False):
        '''
            Lock on daemon name and make us a daemon.

            foreground: If true then lock on daemon name but don't
                        make us into a daemon, Can be useful when
                        debugging.
        '''
        try:
            self.lock.lock(timeout=0)
        except hcs_utils.lock.AlreadyLockedError:
            print >> sys.stderr, self.name, 'already running.'
        except hcs_utils.lock.LockError, error:
            print >> sys.stderr, 'Failed to create lock for', self.name, error
            sys.exit(1)
        print 'Starting', self.name, 'daemon.'
        if not foreground:
            daemonize()
            # Now we are a daemon, but the lock is on the wrong PID
            self.lock.lock(steal=True)

        return self.run()

    def stop(self, wait=True, signaller=send_sigterm):
        '''
            wait: If true the call blocks util the daemon process has
                  disappeared.
            signaller: function that taken one argument (pid) and signals the
                       daemon to shutdown. Default is to send SIGTERM.
        '''
        pid = self.get_running_pid()
        if pid:
            print 'Stopping', self.name, 'daemon. With PID:', pid
            signaller(pid)
            if wait:
                print 'Waiting for daemon to terminate',
                while self.get_running_pid() == pid:
                    sys.stdout.write('.')
                    sys.stdout.flush()
                    time.sleep(0.5)
                print ''  # linebreak after dots

        else:
            print self.name, 'daemon is not running.'

    def kill(self, wait=True):
        pid = self.get_running_pid()
        if pid:
            print 'Killing', self.name, 'daemon. With PID:', pid
            os.kill(pid, signal.SIGKILL)
            if wait:
                print 'Waiting for daemon to terminate',
                while self.get_running_pid() == pid:
                    sys.stdout.write('.')
                    sys.stdout.flush()
                    time.sleep(0.5)
                print ''  # linebreak after dots
        else:
            print self.name, 'daemon is not running.'

    def restart(self):
        self.stop(wait=True)
        self.start()

    def status(self):
        pid = self.get_running_pid()
        if pid:
            print '{0} process is running with PID: {1}'.format(
                    self.name, pid)
        else:
            print '{0} process is not running.'.format(self.name)

    def get_running_pid(self):
        '''
        Get PID of running daemon. returns 0 if there is no daemon running.

        '''
        lock = self.lock.testlock()
        if lock:
            (_host, pid) = lock
            return pid
        else:
            return 0


def daemonize(stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    ''' Fork the current process as a daemon, redirecting standard file
        descriptors (by default, redirects them to /dev/null).

        Based on example in Python Cookbook, 2nd Edition, by Alex Martelli,
        Anna Ravenscroft and David Ascher

    References:

        UNIX Programming FAQ
            1.7 How do I get my program to act like a daemon?
            http://www.unixguide.net/unix/programming/1.7.shtml
            http://www.faqs.org/faqs/unix-faq/programmer/faq/

        Advanced Programming in the Unix Environment
            W. Richard Stevens, 1992, Addison-Wesley, ISBN 0-201-56317-7.
    '''
    # Perform first fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)  # Exit first parent.
    except OSError, e:
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
    # Decouple from parent environment.
    os.chdir("/")
    os.umask(0)
    os.setsid()
    # Perform second fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)  # Exit second parent.
    except OSError, e:
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
    # The process is now daemonized, redirect standard file descriptors.
    for f in sys.stdout, sys.stderr:
        f.flush()
    si = file(stdin, 'r')
    so = file(stdout, 'a+')
    se = file(stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

##############################################################################
# Helpers for doing a nice shutdown


def install_sigterm_handler(callback=None):
    '''
        Handling a SIGTERM
        Calling Daemon.stop() sends a SIGTERM to the daemon, you may catch
        that to do a controlled shutdown. If you use this function to install
        such a handler you must then often check the sigterm_received flag
        and manually shutdown when it's set.

        callback: If callback is given it will be called after the
                  sigterm_received flag has been set.
    '''
    global __sigterm_callback
    __sigterm_callback = callback
    signal.signal(signal.SIGTERM, handle_sigterm)


def __handle_sigterm():
    global sigterm_received
    sigterm_received = True
    if __sigterm_callback:
        __sigterm_callback()

sigterm_received = False
__sigterm_callback = None
