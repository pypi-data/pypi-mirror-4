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
    Utilities for working with file/dir/paths.

'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import contextlib
import os
import logging
import re
import shutil
import sys
import tempfile
import time

from collections import namedtuple
from fnmatch import fnmatch

DirectoryListing = namedtuple('DirectoryListing', 'dirs files')


def list_dir(path, sort=True):
    ''' returns namedtuple DirectoryListing   (dirs, files)'''
    names = os.listdir(path)
    dirs, nondirs = [], []
    for name in names:
        if os.path.isdir(os.path.join(path, name)):
            dirs.append(name)
        else:
            nondirs.append(name)
    if sort:
        dirs = sorted(dirs)
        nondirs = sorted(nondirs)
    return DirectoryListing(dirs, nondirs)


def walkfiles(dir_, pattern=None, errors='strict'):
    """ walkfiles(D) -> iterator over files in D, recursively.

    The optional argument, pattern, limits the results to files
    with names that match the pattern.  For example,
    mydir.walkfiles('*.tmp') yields only files with the .tmp
    extension.
    """
    log = logging.getLogger('hcs_utils.path.walkfiles')
    if errors not in ('strict', 'warn', 'ignore'):
        raise ValueError("invalid errors parameter")

    try:
        dirs, files = list_dir(dir_)
    except Exception:
        if errors == 'ignore':
            return
        elif errors == 'warn':
            log.warning(
                "Unable to list directory '%s': %s"
                % (dir_, sys.exc_info()[1]))
            return
        else:
            raise

    for file_ in files:
        if pattern is None or fnmatch(file_, pattern):
            yield os.path.join(dir_, file_)
    del files

    #recurse
    for subdir in dirs:
        for file_ in walkfiles(os.path.join(dir_, subdir), pattern, errors):
            yield file_


@contextlib.contextmanager
def tempdir(suffix='', prefix='tmp', dir_=None):
    '''context that creates and removes a temporary directory.

        >>> with tempdir() as tmpd:
        ...   os.path.isdir(tmpd)
        True
        >>> os.path.exists(tmpd)
        False
    '''
    tmpd = tempfile.mkdtemp(suffix, prefix, dir_)
    yield tmpd
    shutil.rmtree(tmpd)


def scan_for_new_files(path, interval=5, include=None, ignore=None):
    '''yields path of each file in the directory and then
    each new file that is added

    Arguments:
    - path -- directory to watch
    - interval -- number of seconds to delay between each scan
    - include -- If given, only file with names matching regexp is returned
    - ignore -- If given, files matching regexp is ignored

    filenames ending with .tmp is ignored
    '''
    include = include and re.compile(include)
    ignore = ignore and re.compile(ignore)
    previous_files = set()
    while True:
        current_files = list_dir(path).files
        for filename in current_files:
            #yield only files that was not there the last time we looked
            if filename in previous_files:
                continue
            if include and not include.match(filename):
                continue
            if ignore and ignore.match(filename):
                continue
            yield os.path.join(path, filename)
        previous_files = set(current_files)
        time.sleep(interval)  # limit speed


def expand(path):
    """ Clean up a filename by calling expandvars(),
    expanduser(), and normpath() on it.

    This is commonly everything needed to clean up a filename
    read from a configuration file, for example.

    (based on path.py)

    """
    return os.path.normpath(os.path.abspath(os.path.expanduser(
        os.path.expandvars(path))))


def watch_files_callback(paths, callback, delay=5, trigger_on_first_check=False, propagate_callback_errors=False):
    '''
    paths: list of files to watch
    callback: function to call when a file changes, takes 2 arguments
        (path, reason)
    delay: time to sleep between checking files
    trigger_on_first_check: If True it will trigger on each existing
        path on the first check

    '''

    log = logging.getLogger('hcs_utils.path.watch_files_callback')
    for path, reason in watch_files(paths, delay=delay, trigger_on_first_check=trigger_on_first_check):
        try:
            callback(path, reason)
        except:
            if propagate_callback_errors:
                raise
            else:
                log.exception('Ignoring exception thrown by callback')


def watch_files(paths, delay=5, trigger_on_first_check=False):
    ''' watch a list of files for modifications and
    yield a (path, reason) for each detected change

    paths: list of files to watch
    delay: time to sleep between checking files
    trigger_on_first_check: If True it will trigger on each existing
        path on the first check

    '''
    log = logging.getLogger('hcs_utils.path.watch_files')
    mtimes = {}
    first_check = True
    while 1:
        for path in paths:
            try:
                now = os.path.getmtime(path)
            except os.error:
                now = -1
            last = mtimes.get(path, -1)
            if last == now:
                continue
            mtimes[path] = now
            if not first_check or trigger_on_first_check:
                if first_check:
                    yield (path, 'INITIAL')
                elif now == -1:
                    yield (path, 'REMOVED')
                elif last == -1:
                    yield (path, 'CREATED')
                else:
                    yield (path, 'MODIFIED')
        if first_check:
            first_check = False
