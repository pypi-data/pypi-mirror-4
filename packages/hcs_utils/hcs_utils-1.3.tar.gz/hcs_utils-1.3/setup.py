#!/usr/bin/env python
# vim: fileencoding=UTF-8 filetype=python ff=unix expandtab sw=4 sts=4 tw=120
# author: Christer Sjöholm -- goobook AT furuvik DOT net

from setuptools import setup, find_packages, Command
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()

version = '1.3'

class UltraMagicString(object):
    ''' Stolen from http://stackoverflow.com/questions/1162338/whats-the-right-way-to-use-unicode-metadata-in-setup-py

    Catch-22:
    - if I return Unicode, python setup.py --long-description as well
      as python setup.py upload fail with a UnicodeEncodeError
    - if I return UTF-8 string, python setup.py sdist register
      fails with an UnicodeDecodeError
    '''

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def __unicode__(self):
        return self.value.decode('UTF-8')

    def __add__(self, other):
        return UltraMagicString(self.value + str(other))

    def split(self, *args, **kw):
        return self.value.split(*args, **kw)

setup(name='hcs_utils',
      version=version,
      description="My personal library collecting some useful snippets.",
      long_description=UltraMagicString(README + '\n\n' + NEWS),
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author=UltraMagicString('Christer Sjöholm'),
      author_email='hcs at furuvik dot net',
      url='http://pypi.python.org/pypi/hcs_utils',
      download_url='http://pypi.python.org/pypi/hcs_utils',
      packages=find_packages(),
      zip_safe=True,
      install_requires = [
          # For more details, see: http://packages.python.org/distribute/setuptools.html#declaring-dependencies
          ],
      entry_points={
          # -*- Entry points: -*-
          }
      )
