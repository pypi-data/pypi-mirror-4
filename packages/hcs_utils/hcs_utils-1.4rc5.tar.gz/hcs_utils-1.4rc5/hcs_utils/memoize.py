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

import functools
import hcs_utils.lock
import weakref


class memoize(object):
    """Decorator that caches the function's return value for each set of
    arguments.

    NOTE: All arguments must be hashable for the caching to work.

    Inspired by example on http://wiki.python.org/moin/PythonDecoratorLibrary

    When decorating a method there will only be one cache for the method
    shared by all instances of the class. This implemetation to in that
    case use the instance object as a part of the key to simulate that there
    is one cache for each instance.

    >>> @memoize
    ... def func(*args):
    ...     print('calculating')
    ...     return 42
    ...
    >>> func()
    calculating
    42
    >>> func()
    42
    >>> func(memoize_redo=True)
    calculating
    42
    >>> func(memoize_redo=True)
    calculating
    42
    >>> func({})
    calculating
    42
    >>> func({})
    calculating
    42
    """
    def __init__(self, func, static_cache=False):
        '''
        static_cache: If True use one global cache instead of one for each
            instance object.
        '''
        self.func = func
        self.static_cache = static_cache

        self.cache = {}
        self.locks = hcs_utils.lock.IDLock()
        self.is_instance_method_call = False  # is reset by __get__

    def __call__(self, *args, **kwargs):
        force_redo = False
        if self.is_instance_method_call:
            obj = args[0]
            paras = args[1:]  # parameters (args excluding self ref)
        else:
            paras = args
        try:
            if self.is_instance_method_call and not self.static_cache:
                obj = weakref.ref(obj, self.__cleanup_callback)
                key = (obj, frozenset(paras), frozenset(kwargs.items()))
            else:
                key = (frozenset(paras), frozenset(kwargs.items()))
            if 'memoize_redo' in kwargs:
                force_redo = kwargs['memoize_redo']
                del kwargs['memoize_redo']
            if key in self.cache and not force_redo:
                val = self.cache[key]
            else:
                with self.locks.aquire(key):
                    if key in self.cache and not force_redo:
                        val = self.cache[key]
                    else:
                        val = self.func(*args, **kwargs)
                        self.cache[key] = val
            return val
        except TypeError:
            # If we can't cache we don't (the key is unhashable).
            return self.func(*args, **kwargs)

    def __get__(self, obj, objtype):
        """Support instance methods."""
        if obj is None:
            self.is_instance_method_call = False
            return self
        else:
            self.is_instance_method_call = True
            return functools.partial(self.__call__, obj)

    def __cleanup_callback(self, weak_ref):
        '''If an instance is garbage collected then remove everything
        cached for that instance.

        '''
        for key in list(self.cache):
            obj = key[0]
            if obj == weak_ref:
                del self.cache[key]
