##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
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
name = 'zc.zdaemonrecipe'

import os
from setuptools import setup, find_packages

entry_points = '''
[zc.buildout]
default=zc.zdaemonrecipe:Recipe
'''

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description=(
        read('README.rst')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('zc', 'zdaemonrecipe', 'README.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        )

open('doc.txt', 'w').write(long_description)

tests_require = ['zope.testing']

setup(
    name = name,
    version='0.3.1',
    author = 'Jim Fulton',
    author_email = 'jim@zope.com',
    description = 'ZC Buildout recipe for zdaemon scripts',
    long_description=long_description,
    license = 'ZPL 2.1',

    entry_points=entry_points,
    packages = find_packages('.'),
    namespace_packages = ['zc'],
    extras_require = dict(test=['zdaemon', 'zope.testing']),
    install_requires = ['setuptools',
                        'zc.buildout', 'zc.recipe.egg',
                        'ZConfig'],
    test_suite='zc.zdaemonrecipe.tests.test_suite',
    tests_require=tests_require,
    zip_safe=False,
    )
