##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os, re, shutil, sys, tempfile
import pkg_resources

import zc.buildout.testing

import unittest
import zope.testing
from zope.testing import doctest, renormalizing

try:
    from zc.buildout.testing import not_found
except ImportError:
    not_found = (re.compile(r'Not found: [^\n]+/(\w|\.)+/\r?\n'), '')

setuptools_or_distribute = (
    re.compile(r"[d-]  (setuptools|distribute)-"), "setuptools-")


def newlines_in_program():
    """
There can be newlines in the program option:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = run
    ...
    ... [run]
    ... recipe = zc.zdaemonrecipe
    ... program = sleep
    ...             1
    ... ''')

    >>> print system(buildout),
    Installing run.
    Generated script '/sample-buildout/bin/zdaemon'.
    Generated script '/sample-buildout/bin/run'.

    >>> cat('parts', 'run', 'zdaemon.conf')
    <runner>
      daemon on
      directory /sample-buildout/parts/run
      program sleep 1
      socket-name /sample-buildout/parts/run/zdaemon.sock
      transcript /sample-buildout/parts/run/transcript.log
    </runner>
    <BLANKLINE>
    <eventlog>
      <logfile>
        path /sample-buildout/parts/run/transcript.log
      </logfile>
    </eventlog>

    
    """


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('zc.zdaemonrecipe', test)
    zc.buildout.testing.install('zope.testing', test)
    zc.buildout.testing.install('zc.recipe.egg', test)
    zc.buildout.testing.install('zdaemon', test)
    zc.buildout.testing.install('ZConfig', test)


checker = renormalizing.RENormalizing([
    zc.buildout.testing.normalize_path,
    (re.compile(
    "Couldn't find index page for '[a-zA-Z0-9.]+' "
    "\(maybe misspelled\?\)"
    "\n"
    ), ''),
    (re.compile('#![^\n]+\n'), ''),                
    (re.compile('-\S+-py\d[.]\d(-\S+)?.egg'),
     '-pyN.N.egg',
    ),
    not_found,
    setuptools_or_distribute,
    ])

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            checker=checker,
            ),
        doctest.DocTestSuite(
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            checker=checker,
            ),
        ))
