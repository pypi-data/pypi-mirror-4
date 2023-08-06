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
from hcs_utils.storage import Storage, json_loads_storage, json_dumps_storage, unicode_storage, storageify, unstorageify
from hcs_utils.unittest import eq_
from pytest import raises
import six


def test_init_empty():
    sto = Storage()
    eq_(sto.get_dict(), {})
    eq_(list(sto), [])


def test_init_kwargs():
    di1 = {'a': 1, 'b': 2}
    sto = Storage(a=1, b=2)
    eq_(sto.get_dict(), di1)
    eq_(set(sto), set(['a', 'b']))


def test_init_dict():
    di1 = {'a': 1, 'b': 2}
    sto = Storage(di1)
    eq_(id(sto.get_dict()), id(di1))


def test_init_dict_kwargs():
    di1 = {'a': 1, 'b': 2}
    sto = Storage(di1, b=3, c=4)
    eq_(sto.get_dict(), {'a': 1, 'b': 3, 'c': 4})
    eq_(id(sto.get_dict()), id(di1))


def test_access():
    di1 = {'a': [1], 'b': [2]}
    sto = Storage(di1)
    eq_(sto.a, [1])
    eq_(sto.b, [2])
    eq_(id(sto.get_dict()['a']), id(sto.a))
    eq_(id(sto.a), id(di1['a']))


def test_access_error1():
    sto = Storage()
    with raises(AttributeError):
        _ = sto.a


def test_access_error2():
    sto = Storage()
    with raises(KeyError):
        _ = sto['a']


def test_set():
    sto = Storage()
    sto.a = 1
    eq_(sto.a, 1)
    eq_(sto['a'], 1)
    sto.a = 2
    eq_(sto.a, 2)
    eq_(sto['a'], 2)
    sto['a'] = 3
    sto.a = 3


def test_contains():
    sto = Storage()
    eq_('a' in sto, False)
    sto.a = 1
    eq_('a' in sto, True)
    del sto.a
    eq_('a' in sto, False)


def test_contains_ci():
    sto = Storage(case_insensitive=True)
    eq_('A' in sto, False)
    sto.a = 1
    eq_('A' in sto, True)
    del sto.a
    eq_('A' in sto, False)


def test_del1():
    sto = Storage()
    sto.a = 1
    sto.a
    del sto.a
    with raises(AttributeError):
        sto.a


def test_del2():
    sto = Storage()
    sto.a = 1
    sto.a
    del sto['a']
    with raises(AttributeError):
        sto.a


def test_del_ci1():
    sto = Storage(case_insensitive=True)
    sto.a = 1
    sto.a
    del sto.A
    with raises(AttributeError):
        sto.a


def test_del_ci2():
    sto = Storage(case_insensitive=True)
    sto.a = 1
    sto.a
    del sto['A']
    with raises(AttributeError):
        sto.a


def test_del_error1():
    sto = Storage()
    with raises(AttributeError):
        del sto.a


def test_del_error2():
    sto = Storage()
    with raises(KeyError):
        del sto['a']


def test_repr():
    sto = Storage(a=1, b=2)
    eq_(repr(sto), "Storage(a=1, b=2)")
    sto = Storage(default_factory=list, a=1, b=2)
    # class is for python 3
    assert repr(sto) == "Storage(default_factory=<type 'list'>, a=1, b=2)" or \
        repr(sto) == "Storage(default_factory=<class 'list'>, a=1, b=2)"


def test_json_loads_storage():
    sto = json_loads_storage('[{"a":1}]')
    eq_(sto[0][u'a'], 1)


def test_json_dumps_storage():
    eq_(json_dumps_storage(Storage(a=2)), '{\n  "a": 2\n}')
    eq_(json_dumps_storage([Storage(a=2)]), '[\n  {\n    "a": 2\n  }\n]')
    eq_(json_dumps_storage({'a': 2}), '{\n  "a": 2\n}')


def test_init_empty_defaultdict():
    sto = Storage(default_factory=str)
    eq_(sto.get_dict(), {})
    eq_(list(sto), [])
    eq_(sto.something, '')
    sto.a = 'b'
    eq_(sto.a, 'b')
    eq_(sto.something, '')


def test_case_sensitive():
    sto = Storage()
    sto.a = 'b'
    with raises(AttributeError):
        _ = sto.A
    eq_(sto['a'], 'b')
    with raises(KeyError):
        sto['A']


def test_case_insensitive():
    sto = Storage(case_insensitive=True)
    sto.a = 'b'
    eq_(sto.a, 'b')
    eq_(sto.A, 'b')
    eq_(sto['a'], 'b')
    eq_(sto['A'], 'b')


def test_normalize():
    sto = Storage(normalize=lambda key: key.replace(':', '_colon_'))
    sto['a:b'] = 'b'
    # test that normal access works
    eq_(sto['a:b'], 'b')
    with raises(AttributeError):
        _ = sto.A
    with raises(KeyError):
        sto['A']
    # test access using already normalized keys.
    eq_(sto['a_colon_b'], 'b')
    eq_(sto.a_colon_b, 'b')


def test_normalize_case_insensitive():
    sto = Storage(case_insensitive=True, normalize=lambda key: key.replace(':', '_colon_'))
    sto['a:B'] = 'b'
    eq_(sto.A_coLon_B, 'b')
    eq_(sto['a:b'], 'b')
    eq_(sto['A:b'], 'b')


def test_unicode_storage():
    sto = Storage(a=1, b=2, c=str('3'), d=u'4')
    expect = "Storage(a=1, b=2, c='3', d='4')" if six.PY3 else "Storage(a=1, b=2, c='3', d=u'4')"
    eq_(repr(sto), expect)
    sto = unicode_storage(sto)
    expect = "Storage(a='1', b='2', c='3', d='4')" if six.PY3 else "Storage(a=u'1', b=u'2', c=u'3', d=u'4')"
    eq_(repr(sto), expect)


def test_denormalize():
    sto = Storage(denormalize=lambda key: key.upper())
    sto.a = 1
    assert list(sto.iteritems()) == [('A', 1)]


def test_pickle_fix():
    sto = Storage()
    with raises(AttributeError):
        sto.__getattr__('_dict')

storageify_data = \
    [
        ({}, Storage()),
        ({'a': 4}, Storage(a=4)),
        (
            {'a': 4, 'b': [1, 2, 3, {'b': u'åäö'}]},
            Storage(a=4, b=[1, 2, 3, Storage(b=u'åäö')])
        ),
    ]


def test_storageify():
    for dicts_, storages_ in storageify_data:
        eq_(storageify(dicts_), storages_)


def test_unstorageify():
    for dicts_, storages_ in storageify_data:
        eq_(dicts_, unstorageify(storages_))
