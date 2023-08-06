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
from hcs_utils.path import list_dir, scan_for_new_files, tempdir, walkfiles, expand, watch_files, watch_files_callback
from hcs_utils.unittest import eq_
from pytest import raises
import os
import threading
import time


def test_list_dir():
    with tempdir() as tmpd:
        eq_(list_dir(tmpd), ([], []))
        open(os.path.join(tmpd, 'f1'), 'w').close()
        open(os.path.join(tmpd, 'f2'), 'w').close()
        os.mkdir(os.path.join(tmpd, 'd1'))
        eq_(list_dir(tmpd), (['d1'], ['f1', 'f2']))


def test_scan_for_new_files():
    with tempdir() as tmpd:
        os.mkdir(os.path.join(tmpd, 'd1'))
        open(os.path.join(tmpd, 'f1'), 'w').close()
        open(os.path.join(tmpd, 'f2'), 'w').close()
        scanner = scan_for_new_files(tmpd, interval=0.1)
        eq_(next(scanner), os.path.join(tmpd, 'f1'))
        eq_(next(scanner), os.path.join(tmpd, 'f2'))
        scanner.close()


def test_scan_for_new_files_include():
    with tempdir() as tmpd:
        open(os.path.join(tmpd, 'f1'), 'w').close()
        open(os.path.join(tmpd, 'f2'), 'w').close()
        open(os.path.join(tmpd, 'f2.test'), 'w').close()
        scanner = scan_for_new_files(tmpd, interval=0.1, include='.*\.test$')
        eq_(next(scanner), os.path.join(tmpd, 'f2.test'))
        open(os.path.join(tmpd, 'f3.test'), 'w').close()
        eq_(next(scanner), os.path.join(tmpd, 'f3.test'))
        scanner.close()


def test_scan_for_new_files_exclude():
    with tempdir() as tmpd:
        open(os.path.join(tmpd, 'f1'), 'w').close()
        open(os.path.join(tmpd, 'f2'), 'w').close()
        open(os.path.join(tmpd, 'f2.test'), 'w').close()
        scanner = scan_for_new_files(tmpd, interval=0.1, ignore='.*\.test$')
        eq_(next(scanner), os.path.join(tmpd, 'f1'))
        eq_(next(scanner), os.path.join(tmpd, 'f2'))
        open(os.path.join(tmpd, 'f3.test'), 'w').close()
        open(os.path.join(tmpd, 'f3'), 'w').close()
        eq_(next(scanner), os.path.join(tmpd, 'f3'))
        scanner.close()


def test_walkfiles():
    with tempdir() as tmpd:
        open(os.path.join(tmpd, 'f2'), 'w').close()
        open(os.path.join(tmpd, 'f1'), 'w').close()
        open(os.path.join(tmpd, 'f2.test'), 'w').close()
        os.makedirs(os.path.join(tmpd, 'd1', 'dd1'))
        os.makedirs(os.path.join(tmpd, 'd2', 'dd2'))
        open(os.path.join(tmpd, 'd2', 'dd2', 'ddf23'), 'w').close()
        open(os.path.join(tmpd, 'd2', 'dd2', 'ddf2'), 'w').close()
        os.makedirs(os.path.join(tmpd, 'd3', 'dd3'))
        open(os.path.join(tmpd, 'd3', 'dd3', 'ddf3'), 'w').close()

        expected_result = ['f1', 'f2', 'f2.test', 'd2/dd2/ddf2', 'd2/dd2/ddf23', 'd3/dd3/ddf3']
        eq_(list(walkfiles(tmpd)), [os.path.join(tmpd, fn) for fn in expected_result])

        expected_result = ['f2.test']
        eq_(list(walkfiles(tmpd, pattern='*.test')), [os.path.join(tmpd, fn) for fn in expected_result])


def test_walkfiles_errors():
    with tempdir() as tmpd:
        with raises(ValueError):
            for _ in walkfiles(tmpd, errors='incorrect'):
                pass


def test_expand():
    eq_(expand('~root/'), '/root')
    eq_(expand('/root/../etc'), '/etc')


def test_watch_files():
    with tempdir() as tmpd:
        fn1 = os.path.join(tmpd, 'test1')
        fn2 = os.path.join(tmpd, 'test2')
        open(fn1, 'w').close()
        print(fn1)
        generator = watch_files((fn1, fn2), delay=0.1, trigger_on_first_check=True)
        (path, reason) = next(generator)
        eq_(path, fn1)
        eq_(reason, 'INITIAL')
        time.sleep(1)
        with open(fn1, 'w') as f:
            f.write('a')
        (path, reason) = next(generator)
        eq_(path, fn1)
        eq_(reason, 'MODIFIED')

        open(fn2, 'w').close()
        (path, reason) = next(generator)
        eq_(path, fn2)
        eq_(reason, 'CREATED')
        os.unlink(fn2)
        (path, reason) = next(generator)
        eq_(path, fn2)
        eq_(reason, 'REMOVED')
        generator.close()


def test_watch_files_callback():
    with tempdir() as tmpd:
        fn1 = os.path.join(tmpd, 'test1')
        open(fn1, 'w').close()
        #dict so that it can be updated from callback
        cb_res = dict(path=None, reason=None)

        def callback(path, reason):
            cb_res['path'] = path
            cb_res['reason'] = reason

        def watcher():
            watch_files_callback((fn1,), callback, delay=10,
                                 trigger_on_first_check=True, propagate_callback_errors=False)
        thr = threading.Thread(target=watcher)
        thr.daemon = True
        thr.start()
        time.sleep(0.01)
        eq_(cb_res['path'], fn1)
        eq_(cb_res['reason'], 'INITIAL')


def test_watch_files_callback_error1():
    with tempdir() as tmpd:
        fn1 = os.path.join(tmpd, 'test1')
        open(fn1, 'w').close()
        #dict so that it can be updated from callback
        cb_res = dict(path=None, reason=None, exc=None)

        def callback(path, reason):
            cb_res['path'] = path
            cb_res['reason'] = reason
            raise Exception('Testing error handling')

        def watcher():
            try:
                watch_files_callback((fn1,), callback, delay=10, trigger_on_first_check=True,
                                     propagate_callback_errors=True)
            except Exception as e:
                cb_res['exc'] = e
        thr = threading.Thread(target=watcher)
        thr.daemon = True
        thr.start()
        time.sleep(0.01)
        eq_(cb_res['path'], fn1)
        eq_(cb_res['reason'], 'INITIAL')
        eq_(str(cb_res['exc']), 'Testing error handling')


def test_watch_files_callback_error2():
    with tempdir() as tmpd:
        fn1 = os.path.join(tmpd, 'test1')
        open(fn1, 'w').close()
        #dict so that it can be updated from callback
        cb_res = dict(path=None, reason=None, exc=None)

        def callback(path, reason):
            cb_res['path'] = path
            cb_res['reason'] = reason
            raise Exception('Testing error handling')

        def watcher():
            watch_files_callback((fn1,), callback, delay=10, trigger_on_first_check=True,
                                 propagate_callback_errors=False)
        thr = threading.Thread(target=watcher)
        thr.daemon = True
        thr.start()
        time.sleep(0.01)
        eq_(cb_res['path'], fn1)
        eq_(cb_res['reason'], 'INITIAL')
        eq_(cb_res['exc'], None)  # it was only logged
