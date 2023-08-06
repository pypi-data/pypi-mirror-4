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

import difflib
import json


def ok_(expr, msg=None):
    __tracebackhide__ = True  # Don't show in traceback (pytest)
    assert expr, msg


def eq_(a, b, msg=None):
    __tracebackhide__ = True  # Don't show in traceback (pytest)
    assert a == b, msg or "%r != %r" % (a, b)


def diff_str(str1, str2):
    return u''.join(difflib.ndiff(str1.splitlines(1), str2.splitlines(1)))


def eq_str(str1, str2, msg=None):
    """assert that strings str1 and str2 are equal.
    If msg is None result of difflib.ndiff() will be used.
    """
    __tracebackhide__ = True  # Don't show in traceback (pytest)
    assert str1 == str2, msg or diff_str(unicode(str2), unicode(str1))


def eq_json(obj1, obj2, msg=None):
    """assert that a and b have equal json representations.
    If msg is None, difflib.ndiff() will be used on json.
    """
    __tracebackhide__ = True  # Don't show in traceback (pytest)
    obj1 = json.dumps(obj1, sort_keys=True, indent=2)
    obj2 = json.dumps(obj2, sort_keys=True, indent=2)
    assert obj1 == obj2, msg or diff_str(obj2, obj1)
