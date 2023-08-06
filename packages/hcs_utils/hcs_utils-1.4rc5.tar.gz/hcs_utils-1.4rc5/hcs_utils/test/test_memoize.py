#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: fileencoding=UTF-8 filetype=python ff=unix et ts=4 sw=4 sts=4 tw=120
# author: Christer Sjöholm -- hcs AT furuvik DOT net
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
from hcs_utils.memoize import memoize
from hcs_utils.unittest import eq_

# TODO test that the weak references are cleaned up


def test_memoize_on_func():
    call_counter = [0]

    @memoize
    def func(arg):
        call_counter[0] += 1
        return arg + 1
    eq_(func(1), 2)
    eq_(call_counter[0], 1)
    eq_(func(1), 2)
    eq_(call_counter[0], 1)
    eq_(func(2), 3)
    eq_(call_counter[0], 2)


def test_memoize_on_obj():
    call_counter = [0]

    class test(object):
        @memoize
        def func(self, arg):
            call_counter[0] += 1
            return arg + 1
    inst1 = test()
    inst2 = test()

    eq_(inst1.func(1), 2)
    eq_(call_counter[0], 1)
    eq_(inst1.func(1), 2)
    eq_(call_counter[0], 1)
    eq_(inst1.func(2), 3)
    eq_(call_counter[0], 2)

    eq_(inst2.func(1), 2)
    eq_(call_counter[0], 3)
    eq_(inst1.func(2), 3)
    eq_(call_counter[0], 3)


def test_memoize_on_property():
    call_counter = [0]

    class test(object):
        @property
        @memoize
        def func(self):
            call_counter[0] += 1
            return 2 + call_counter[0]
    inst1 = test()
    inst2 = test()

    eq_(call_counter[0], 0)
    eq_(inst1.func, 3)
    eq_(call_counter[0], 1)
    eq_(inst1.func, 3)
    eq_(call_counter[0], 1)

    eq_(inst2.func, 4)
    eq_(call_counter[0], 2)
    eq_(inst2.func, 4)
    eq_(call_counter[0], 2)

    eq_(inst1.func, 3)
    eq_(call_counter[0], 2)
