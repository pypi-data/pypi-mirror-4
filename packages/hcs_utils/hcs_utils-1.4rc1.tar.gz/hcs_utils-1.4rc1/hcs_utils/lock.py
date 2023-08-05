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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import errno
import logging
import os
import socket
import threading
import time


class Lock(object):
    '''
    Interprocess locking using a PID file (symlink actually).

    - Supports locks on NFS
    - Has support for breaking stale locks of processes on the same host.


    A lock ID looks like this: HOST:PID
    '''
    log = logging.getLogger(__name__)

    def __init__(self, pathname, timeout=10, sleep_interval=0.1):
        self.pathname = pathname
        self.hostname = socket.gethostname()
        self.default_timeout = timeout  # timeout in secs
        self.sleep_interval = sleep_interval

    def __enter__(self):
        self.lock()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

    def lock(self, timeout=None, steal=False):
        '''
        timeout: in seconds, may be a float, use 0 to only try once.
                 If None, use the sel.default_timeout.
        steal: If True then we remove any existing lock even if it is
               owned by a living process.
        '''
        if timeout is None:
            timeout = self.default_timeout
        start_time = time.time()
        while True:
            try:
                return self._lock(steal)
            except AlreadyLockedError:
                if time.time() - start_time > timeout:
                    raise
                time.sleep(self.sleep_interval)

    def _lock(self, steal=False):
        '''This is the lock implementation used by lock() that has the timeout
        handling.'''
        locker = '%s:%d' % (self.hostname, os.getpid())
        try:
            test_res = self.testlock()
            if test_res:
                if steal:
                    os.unlink(self.pathname)
                elif test_res == (self.hostname, os.getpid()):
                    raise AlreadyLockedError('We already have the lock (pid: %s): %s'
                                             % (os.getpid(), self.pathname))
                else:
                    raise AlreadyLockedError('Already locked (pid: %s): %s' %
                                             (os.getpid(), self.pathname))
            self.log.debug('Locking: {0} {1}'.format(locker, self.pathname))
            return os.symlink(locker, self.pathname)
        except OSError as err:
            raise LockError('Failed to create lock: %s' % self.pathname, err)

    def release(self):
        if self.has_lock():
            self.log.debug('Unlocking: {0}'.format(self.pathname))
            os.unlink(self.pathname)
        elif self.testlock() is None:
            raise LockError('Tried to release non existing.')
        else:
            raise LockError('Tried to release someone elses lock.')

    def has_lock(self):
        '''
        returns True if this process has the lock, otherwise False.
        '''
        lock = self.testlock()
        if lock and lock == (self.hostname, os.getpid()):
            return True
        else:
            return False

    def testlock(self):
        """return (host, pid) if locked, else None.
        If the lock is invalid it is removed and None is returned.

        """
        try:
            host, pid = os.readlink(self.pathname).split(':', 1)
            pid = int(pid)
        except OSError as err:
            if err.errno == errno.ENOENT:
                return None
            raise LockError('Failed to read lock: %s' % self.pathname, err)
        if host != self.hostname or check_pid(pid):
            return host, pid
        # Lock the lock before breaking it.
        try:
            with Lock(self.pathname + '.break'):
                os.unlink(self.pathname)
        except LockError:
            return host, pid


def check_pid(pid):
    '''Check if the process exists'''
    try:
        os.kill(pid, 0)
        return True  # Process alive
    except OSError:
        return False


class IDLock(object):
    '''
    This class lets you have a infinite amount of locks.

    What you do is that you lock an ID (str/int/...) and nobody
    else can lock that ID until you release it.

    This class do NOT do interprocess locking.
    '''
    log = logging.getLogger(__name__)

    def __init__(self, timeout=10, sleep_interval=0.1):
        self.default_timeout = timeout  # timeout in secs
        self.sleep_interval = sleep_interval
        self.master_lock = threading.Lock()
        self.locks = set()  # currently locked IDs

    def aquire(self, id, timeout=None):
        '''
        timeout: in seconds, may be a float, use 0 to only try once.
                 If None, use the sel.default_timeout.
        '''
        if timeout is None:
            timeout = self.default_timeout
        start_time = time.time()
        while True:
            try:
                return self._lock(id)
            except AlreadyLockedError:
                if time.time() - start_time > timeout:
                    raise
                time.sleep(self.sleep_interval)

    def _lock(self, id):
        '''This is the lock implementation used by aquire()
        that has the timeout handling.

        '''
        with self.master_lock:
            if id in self.locks:
                raise AlreadyLockedError('Already locked: {0}'.format(id))
            else:
                self.locks.add(id)

        class Releaser(object):
            def __enter__(self2):
                return

            def __exit__(self2, *exci):
                self.release(id)
        return Releaser()

    def release(self, id):
        with self.master_lock:
            if id in self.locks:
                self.locks.remove(id)
            else:
                raise LockError(
                    'Tried to release non existing lock: {0}'.format(id))


class LockError(Exception):
    pass


class AlreadyLockedError(LockError):
    pass
