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
Can be used on two levels, either directly use Store, or use a StoreGroup.


'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from hcs_utils.path import list_dir
from hcs_utils.storage import Storage, json_dump_storage, json_load_storage

import codecs
import errno
import hashlib
import hcs_utils.lock
import logging
import os
import shutil

log = logging.getLogger(__name__)


class Store(object):
    def __init__(self, root, mapper=None):
        self.root = root
        # if you want to lock the whole Store
        self.lock = hcs_utils.lock.Lock(os.path.join(root, '.lock'))
        self._map = mapper or HashMapper()
        #self._map = mapper or OneToOneMapper()
        self._meta_path = os.path.join(root, 'meta.json')

    @property
    def items(self):
        '''list of item names'''
        return list(self)

    def mkitem(self, item_name):
        path = self.get_path(item_name)
        log.debug('mkitem {0} {1}'.format(item_name, path))
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno == errno.EEXIST:
                raise AlreadyExistError(
                    'Item already exist: {0}'.format(item_name))
            else:
                raise
        return self[item_name]

    def get_meta(self):
        with open(self._meta_path) as inp:
            return json_load_storage(inp)

    def set_meta(self, metadata):
        with open(self._meta_path, 'w') as out:
            json_dump_storage(metadata, out)

    def get_path(self, item_name):
        id_ = self._map.name_to_id(item_name)
        return os.path.join(self.root, id_)

    def open(self, attachment_name, mode='r', codec=None):
        if codec:
            return codecs.open(self.get_path(attachment_name), mode, codec)
        else:
            return open(self.get_path(attachment_name), mode=mode)

    def rename(self, from_item_name, to_item_name):
        fro = self.get_path(from_item_name)
        to_ = self.get_path(to_item_name)
        tdir = os.path.dirname(to_)
        if not os.path.exists(tdir):
            os.makedirs(tdir)
        os.rename(fro, to_)

    def __delitem__(self, item_name):
        shutil.rmtree(self.get_path(item_name))

    def __contains__(self, item_name):
        return os.path.exists(self.get_path(item_name))

    def __getitem__(self, item_name):
        if item_name not in self:
            raise KeyError('No such item in store: ' + item_name)
        return Item(self.get_path(item_name), item_name)

    def __iter__(self):
        return self._map.iterate_names(self.root)

    def __eq__(self, other):
        return self.root == other.root

    __hash__ = None


class StoreGroup(object):
    """
    Handle a group of Stores,

    The primary use for StoreGroups is to separate Items with different
    statuses (inspired by maildir) for example in a queue system.

    Store names must be valid for the filesystem.

    """
    def __init__(self, root, mapper=None):
        self.root = root
        # if you want to lock the whole StoreGroup
        self.lock = hcs_utils.lock.Lock(os.path.join(root, '.lock'))
        self._map = mapper or HashMapper()
        #self._map = mapper or OneToOneMapper()

    def get_path(self, store_name):
        return os.path.join(self.root, store_name)

    @property
    def stores(self):
        '''list of store names'''
        return list_dir(self.root).dirs

    def mkstore(self, store_name):
        path = self.get_path(store_name)
        log.debug('mkstore {0} {1}'.format(store_name, path))
        os.mkdir(path)
        return self[store_name]

    def __contains__(self, store_name):
        return store_name in self.stores

    def __getitem__(self, store_name):
        return Store(self.get_path(store_name), self._map)

    def __iter__(self):
        for store_name in self.stores:
            yield self.__getitem__(store_name)

    def move(self, item_name, from_store, to_store):
        log.debug('move {0} from {1} to {2}'.format(
            item_name, from_store, to_store))
        fro = self[from_store].get_path(item_name)
        to_ = self[to_store].get_path(item_name)
        tdir = os.path.dirname(to_)
        if not os.path.exists(tdir):
            os.makedirs(tdir)
        os.rename(fro, to_)


class Item(object):
    '''
    An Item consists of:
    1. Metadata stored as json
    2. 0 or more attached files

    An Item is really a directory you can store any files you want in.

    '''

    def __init__(self, path, name):
        self.path = path
        self.name = name
        # if you want to lock the Item
        self.lock = hcs_utils.lock.Lock(os.path.join(path, '.lock'))
        self._meta_path = os.path.join(path, 'meta.json')

    @property
    def attachments(self):
        '''list of attachments'''
        return list_dir(self.path).files

    def get_meta(self):
        if os.path.exists(self._meta_path):
            with self.open(self._meta_path) as inp:
                return json_load_storage(inp)
        else:
            return Storage()

    def set_meta(self, metadata):
        with self.open(self._meta_path, 'w') as out:
            json_dump_storage(metadata, out)

    def get_path(self, attachment_name):
        return os.path.join(self.path, attachment_name)

    def open(self, attachment_name, mode='r', codec=None):
        if codec:
            return codecs.open(self.get_path(attachment_name), mode, codec)
        else:
            return open(self.get_path(attachment_name), mode)

    def __delitem__(self, attachment_name):
        os.unlink(self.get_path(attachment_name))

    def __contains__(self, attachment_name):
        return attachment_name in self.attachments

    def __iter__(self):
        return iter(self.attachments)

    def __eq__(self, other):
        return self.path == other.path

    __hash__ = None

##############################################################################
# Mappers


class OneToOneMapper(object):
    '''Use the name as ID without any modification'''
    def name_to_id(self, name):
        return name

    def id_to_name(self, id_):
        return id_

    def iterate_ids(self, root):
        return iter(list_dir(root).dirs)

    def iterate_names(self, root):
        for id_ in self.iterate_ids(root):
            yield self.id_to_name(id_)


class HashMapper(object):
    '''ID is the SHA1 of the name with __ and the name appended
    The items are spread in a directory tree with "levels" levels.

    How to choose the number of levels:
    Optimization limit (OL) = 256**(levels+1)
    For levels=2 OL is 16777216

    When the numbers of stored items is larger than OL things might
    starting to go slower. How the speed is affected and whether
    there is any hard limits depends on the filesystem.

    '''

    def __init__(self, levels=2):
        self.levels = levels

    def name_to_id(self, name):
        dgst = hashlib.sha1(name.encode()).hexdigest()
        pth = [dgst[i * 2:i * 2 + 2] for i in range(self.levels)]
        pth.append('{0}__{1}'.format(dgst, name))
        return os.path.join(*pth)

    def id_to_name(self, id_):
        return id_.split('__', 1)[1]

    def iterate_ids(self, root):
        for dir_, dirs, _ in os.walk(root):
            dirs.sort()
            found_leaf = False
            for subdir in dirs:
                if '__' in subdir:
                    found_leaf = True
                    yield os.path.join(dir_, subdir)
            if found_leaf:
                dirs[:] = []  # Don't go into any subdir

    def iterate_names(self, root):
        for id_ in self.iterate_ids(root):
            yield self.id_to_name(id_)


class ItemStoreError(Exception):
    pass


class AlreadyExistError(ItemStoreError):
    pass
