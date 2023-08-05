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
from hcs_utils.itemstore import Store, StoreGroup
from hcs_utils.path import tempdir
from hcs_utils.storage import Storage
from hcs_utils.unittest import eq_
from pytest import raises
import os


def test_storegroup():
    with tempdir() as tmpd:
        sgrp = StoreGroup(tmpd)
        eq_(sgrp.stores, [])
        eq_(list(sgrp), [])
        store1 = sgrp.mkstore('test')
        eq_(sgrp.stores, ['test'])
        eq_(store1, Store(os.path.join(tmpd, 'test'), 'test'))
        store2 = sgrp['test']
        eq_(store1, store2)
        eq_(list(sgrp), [store1])
        assert 'test' in sgrp
        assert 'test2' not in sgrp


def test_storegroup_move():
    with tempdir() as tmpd:
        sgrp = StoreGroup(tmpd)
        storea = sgrp.mkstore('a')
        storeb = sgrp.mkstore('b')
        item = storea.mkitem('aa')
        eq_(list(iter(storea)), ['aa', ])
        eq_(list(iter(storeb)), [])
        sgrp.move('aa', 'a', 'b')
        eq_(list(iter(storea)), [])
        eq_(list(iter(storeb)), ['aa', ])


def test_itemgroup():
    with tempdir() as tmpd:
        sgrp = StoreGroup(tmpd)
        sgrp.mkstore('test')
        store = sgrp['test']

        eq_(store.root, os.path.join(sgrp.root, 'test'))
        eq_(store.items, [])
        item = store.mkitem('testi')
        eq_(store.items, ['testi'])
        eq_(store.items, list(store))
        eq_(store['testi'], item)
        assert 'testi' in store
        assert 'test' not in store
        del store['testi']
        assert 'testi' not in store

        with raises(IOError):
            store.get_meta()
        meta = Storage(a=1, b=2)
        store.set_meta(meta)
        meta2 = store.get_meta()
        eq_(meta2.a, 1)
        eq_(meta2.b, 2)


def test_itemgroup_move():
    with tempdir() as tmpd:
        sgrp = StoreGroup(tmpd)
        storea = sgrp.mkstore('a')
        item = storea.mkitem('aa')
        eq_(list(iter(storea)), ['aa'])
        storea.rename('aa', 'bb')
        eq_(list(iter(storea)), ['bb'])


def test_itemgroup3():
    with tempdir() as tmpd:
        sgrp = StoreGroup(tmpd)
        store = sgrp.mkstore('g')
        item = store.mkitem('a')
        item = store.mkitem('b')
        eq_(list(iter(store)), ['a', 'b'])


def test_item():
    with tempdir() as tmpd:
        sgrp = StoreGroup(tmpd)
        store = sgrp.mkstore('g')
        item = store.mkitem('i')

        eq_(item.get_meta(), Storage())
        meta = Storage(a=1, b=2)
        item.set_meta(meta)
        meta2 = item.get_meta()
        eq_(meta2.a, 1)
        eq_(meta2.b, 2)

        eq_(item.attachments, ['meta.json'])
        eq_(list(item), ['meta.json'])

        assert 'a1' not in item
        with raises(IOError):
            item.open('a1')
        with item.open('a1', 'w') as out:
            out.write('testcontent')
        assert 'a1' in item
        with item.open('a1') as inp:
            eq_(inp.read(), 'testcontent')
        del item['a1']
        assert 'a1' not in item
