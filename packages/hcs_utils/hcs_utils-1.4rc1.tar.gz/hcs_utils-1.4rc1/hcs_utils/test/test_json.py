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
from hcs_utils.json import jget, read_incremental_series, read_incremental_list, dump_iter_as_list
from hcs_utils.unittest import eq_
from pytest import raises
import json

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

OBJ1 = {'a': [1, 2, {999: 'abcd'}], 'b': '4'}


def test_jget():
    eq_(jget(OBJ1, None, 'a', 2, 999), 'abcd')
    eq_(jget(OBJ1, 'AOEUI', 'a', 8, 999), 'AOEUI')  # IndexError
    eq_(jget(OBJ1, 'AOEUI', 'a', 2, 888), 'AOEUI')  # KeyError


def test_read_incremental_series():
    inp = StringIO('   [1,2,3,4,5]   {"3":2}   ')
    res = [[1, 2, 3, 4, 5], {u'3': 2}]
    eq_(list(read_incremental_series(inp)), res)
    inp.seek(0)
    eq_(list(read_incremental_series(inp, blocksize=1)), res)


def test_read_incremental_series_err1():
    inp = StringIO('   [1,2,3,4,5]   {"3":2},   ')
    with raises(ValueError):
        list(read_incremental_series(inp))


def test_read_incremental_list():
    inp = StringIO(' [  [1,2,3,4,5]  , {"3":2}  ] ')
    res = [[1, 2, 3, 4, 5], {u'3': 2}]
    eq_(json.load(inp), res)
    inp.seek(0)
    eq_(list(read_incremental_list(inp)), res)
    inp.seek(0)
    eq_(list(read_incremental_list(inp, blocksize=1)), res)


def test_read_incremental_list_err1():
    inp = StringIO('{"3": 2}')
    with raises(ValueError):
        list(read_incremental_list(inp))


def test_read_incremental_list_err2():
    inp = StringIO(' [  [1,2,3,4,5]  , {"3":2}  ] tail')
    with raises(ValueError):
        list(read_incremental_list(inp))


def test_dump_iter_as_list():
    out = StringIO()
    dump_iter_as_list('abc123', out)
    res = out.getvalue()
    eq_(res, '[\n"a",\n"b",\n"c",\n"1",\n"2",\n"3"\n]')
    eq_(json.loads(res), [u'a', u'b', u'c', u'1', u'2', u'3'])
