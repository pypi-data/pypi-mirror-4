##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
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
version = '0.4.0'

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

entry_points = """
[console_scripts]
buildout-source-release = zc.sourcerelease:source_release
"""

long_description=(
    '.. contents::\n\n'
    +
    read('src', 'zc', 'sourcerelease', 'README.txt')
    + '\n' +
    read('src', 'zc', 'sourcerelease', 'CHANGES.txt')
    + '\n' +
    'Download\n'
    '========\n'
    )

open('doc.txt', 'w').write(long_description)


setup(
    name = "zc.sourcerelease",
    description = "Utility script to create source releases from buildouts",
    version = version,
    license = "ZPL 2.1",
    url='http://www.python.org/pypi/zc.sourcerelease',
    author='Jim Fulton', author_email='jim@zope.com',
    long_description=long_description,

    entry_points = entry_points,
    packages = find_packages('src'),
    include_package_data = True,
    zip_safe = False,
    package_dir = {'':'src'},
    namespace_packages = ['zc'],
    install_requires = [
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg',
        ],
    extras_require=dict(
        test=[
            'zope.testing',
            ]),
    )
