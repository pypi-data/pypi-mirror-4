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
from hcs_utils.lock import IDLock, Lock, LockError
from hcs_utils.path import tempdir
from hcs_utils.unittest import eq_
from pytest import raises
import os
import socket
import time


## Tests for Lock

def test_1():
    with tempdir() as tmpd:
        lockn = os.path.join(tmpd, 'lockfile')
        lock = Lock(lockn)
        eq_(lock.testlock(), None)
        lock.lock()
        assert os.path.islink(lockn)
        eq_(len(lock.testlock()), 2)
        lock.release()
        eq_(lock.testlock(), None)


def test_2():
    with tempdir() as tmpd:
        lockn = os.path.join(tmpd, 'lockfile')
        with Lock(lockn) as lock:
            eq_(len(lock.testlock()), 2)
            assert os.path.islink(lockn)


def test_we_already_have_the_lock():
    with tempdir() as tmpd:
        lockn = os.path.join(tmpd, 'lockfile')
        with Lock(lockn) as lock:
            eq_(len(lock.testlock()), 2)
            assert os.path.islink(lockn)
            with raises(LockError):
                with Lock(lockn) as lock2:
                    pass


def test_locked_on_other_host():
    with tempdir() as tmpd:
        lockn = os.path.join(tmpd, 'lockfile')

        #create broken lock
        os.symlink('other_host:123456789', lockn)

        lock = Lock(lockn)
        with raises(LockError):
            lock.lock(timeout=0.3)

        # try to release someone elses lock
        with raises(LockError):
            lock.release()

        assert not lock.has_lock()

        # Steal someone elses lock
        lock.lock(timeout=0, steal=True)
        assert lock.has_lock()
        lock.release()
        eq_(lock.testlock(), None)


def test_fail_to_read_lock():
    with tempdir() as tmpd:
        lockn = os.path.join(tmpd, 'lockfile')
        lock = Lock(lockn)

        #create broken lock
        os.symlink('other_host:123456789', lockn)

        eq_(lock.testlock(), ('other_host', 123456789))
        os.chmod(tmpd, 0)  # remove all rights from directory
        with raises(LockError):
            eq_(lock.testlock(), None)  # fails to read lock
        os.chmod(tmpd, 0o700)  # give us rights to do the test cleanup


def test_fail_to_create_lock():
    with tempdir() as tmpd:
        lockn = os.path.join(tmpd, 'lockfile')
        lock = Lock(lockn)
        os.chmod(tmpd, 0)  # remove all rights from directory
        with raises(LockError):
            lock.lock(timeout=0.3)
        os.chmod(tmpd, 0o700)  # give us rights to do the test cleanup


def test_break_lock():
    with tempdir() as tmpd:
        lockn = os.path.join(tmpd, 'lockfile')

        #create broken lock
        os.symlink(socket.gethostname() + ':123456789', lockn)

        lock = Lock(lockn)
        lock.lock()


def test_blocking():
    '''check that the lock() blocks for the correct amount of time'''
    with tempdir() as tmpd:
        lockn = os.path.join(tmpd, 'lockfile')

        #create broken lock
        os.symlink('other_host:123456789', lockn)

        lock = Lock(lockn)
        start = time.time()
        with raises(LockError):
            lock.lock(timeout=0.3)
        elapsed = time.time() - start
        assert elapsed > 0.3 and elapsed < 0.35


def test_release_unlocked():
    with tempdir() as tmpd:
        lockn = os.path.join(tmpd, 'lockfile')
        lock = Lock(lockn)
        with raises(LockError):
            lock.release()


## Tests for IDLock
def test_idl_1():
    lock = IDLock()
    lock.aquire('a1')
    lock.aquire('a2')
    with raises(LockError):
        lock.aquire('a1', timeout=0)
    lock.release('a1')
    lock.aquire('a1')
    with raises(LockError):
        lock.release('a3')


def test_idl_2():
    lock = IDLock()
    lock.aquire('a1', timeout=0)
    lock.aquire('a2', timeout=0)
    with raises(LockError):
        lock.aquire('a1', timeout=0)
    lock.release('a1')
    lock.aquire('a1', timeout=0)


def test_idl_context():
    lock = IDLock()
    with lock.aquire('a1'):
        with raises(LockError):
            lock.aquire('a1', timeout=0)
    lock.aquire('a1')
