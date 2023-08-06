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

import threading


def synchronized(lock=None):
    ''' Synchronization decorator FACTORY, that is you must call the decorator.

        That is only one call to the method can be acitive at any time.
        If manually passing a lock object to the decorator multiple
        functions can share a lock.

        >>> @synchronized()
        ... def func():
        ...     print(123)
        >>> func()
        123

        >>> custom_lock = threading.Lock()
        >>> @synchronized(custom_lock)
        ... def func():
        ...     print(234)
        >>> func()
        234
    '''
    if not lock:  # lock is from synchronized()
        lock = threading.Lock()

    def decorator(func):
        def wrapped_f(*args, **kwargs):
            with lock:
                func(*args, **kwargs)
        return wrapped_f

    return decorator
