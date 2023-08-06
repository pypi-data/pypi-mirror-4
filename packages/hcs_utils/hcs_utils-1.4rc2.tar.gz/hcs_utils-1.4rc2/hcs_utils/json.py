#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: fileencoding=UTF-8 filetype=python ff=unix et ts=4 sw=4 sts=4 tw=120
# author Christer Sjöholm <hcs@furuvik.net>
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

import json


def jget(data, default, *args):
    ''' Get a element from a tree of nested dicts and lists (JSON style).
    Using this function you will have a default returned it there is a
    problem on any level.

    '''
    try:
        for key in args:
            data = data[key]
    except (KeyError, IndexError):
        data = default
    return data


##############################################################################
# Read series of json documents from a stream

def read_incremental_series(inp, blocksize=1024 * 1024):
    ''' Incrementally read a series of JSON documents from a filelike object.

    > from StringIO import StringIO
    > inp = StringIO('   [1,2,3,4,5]   {"3":2}   ')
    > print([e for e in read_incremental_series(inp)])
    > print([e for e in read_incremental_series(inp, blocksize=1)])

    '''
    decoder = json.JSONDecoder()
    buf = ''
    need_data = True
    while True:
        if need_data:
            data = inp.read(blocksize)
            if not data:
                break  # no more parsable data
            buf += data
            need_data = False
        buf = buf.lstrip()
        try:
            obj, index = decoder.raw_decode(buf)
        except Exception:
            need_data = True
        else:
            buf = buf[index:]
            yield obj
    if buf.strip():
        raise ValueError('Failed to parse all data in file.')

##############################################################################
# Handle large json documents


def dump_iter_as_list(iter_, out):
    '''Incrementally write a iterator as if it was a list'''
    first = True
    out.write('[\n')
    for obj in iter_:
        if first:
            first = False
        else:
            out.write(',\n')
        json.dump(obj, out, check_circular=False)
    out.write('\n]')


def read_incremental_list(inp, blocksize=1024 * 1024):
    ''' Incrementally read a JSON documents with a list as root
    from a filelike object.

    > from StringIO import StringIO
    > inp = StringIO(' [  [1,2,3,4,5]  , {"3":2}  ] ')
    > print([e for e in read_incremental_list(inp)])
    > print([e for e in read_incremental_list(inp, blocksize=1)])
    '''
    decoder = json.JSONDecoder()
    buf = ''
    need_data = True
    start_of_file = True
    while True:
        if need_data:
            data = inp.read(blocksize)
            if not data:
                break  # no more parsable data
            buf += data
            need_data = False
        if start_of_file:
            buf = buf.lstrip()
            if not buf:
                need_data = True
                continue
            elif buf[0] == '[':
                buf = buf[1:]
                start_of_file = False
            else:
                raise ValueError('Files root element is not a JSON list.')
        buf = buf.lstrip(' ,')
        try:
            obj, index = decoder.raw_decode(buf)
        except Exception:
            need_data = True
        else:
            buf = buf[index:]
            yield obj
    if buf.strip() != ']':
        raise ValueError('Failed to parse all data in file.')
