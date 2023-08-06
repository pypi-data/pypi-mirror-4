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
from hcs_utils.unittest import diff_str, eq_str, eq_json, eq_
from pytest import raises


STR1 = '''Two
identical strings.'''
STR2 = '''Two
identical strings.'''
STR3 = '''And one that is different to the
identical strings.'''

DIFF1_2 = '''\
  Two
  identical strings.'''

DIFF1_3 = '''\
- Two
+ And one that is different to the
  identical strings.'''

OBJ1 = {'a': [1, 2, 3], 'b': '4'}
OBJ2 = {'a': [1, 2, 3], 'b': '4'}
OBJ3 = {'a': [1, 2, 5], 'b': '4'}
OBJ4 = {'a': [1, 2, 5], 'b': lambda i: i < 1}  # Not JSON serializable


def test_diff_str():
    eq_(diff_str(STR1, STR2), DIFF1_2)
    eq_(diff_str(STR1, STR3), DIFF1_3)


def test_eq_str1():
    eq_str(STR1, STR1)


def test_eq_str2():
    eq_str(STR1, STR2)


def test_eq_str3():
    with raises(AssertionError):
        eq_str(STR1, STR3)


def test_eq_str4():
    eq_str('åäö', 'åäö')
    eq_str(u'åäö', u'åäö')


def test_eq_str5():
    with raises(AssertionError):
        eq_str('åäö', 'åäö2')
    with raises(AssertionError):
        eq_str(u'åäö', u'åäö2')


def test_eq_json1():
    eq_json(OBJ1, OBJ1)


def test_eq_json2():
    eq_json(OBJ1, OBJ2)


def test_eq_json3():
    with raises(AssertionError):
        eq_json(OBJ1, OBJ3)


def test_eq_json4():
    with raises(TypeError):
        eq_json(OBJ1, OBJ4)
