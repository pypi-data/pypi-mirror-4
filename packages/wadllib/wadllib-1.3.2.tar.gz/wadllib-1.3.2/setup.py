#!/usr/bin/env python

# Copyright 2008-2009 Canonical Ltd.  All rights reserved.
#
# This file is part of wadllib
#
# wadllib is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, version 3 of the License.
#
# wadllib is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with wadllib. If not, see <http://www.gnu.org/licenses/>.

import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

# generic helpers primarily for the long_description
def generate(*docname_or_string):
    res = []
    for value in docname_or_string:
        if value.endswith('.txt'):
            f = open(value)
            value = f.read()
            f.close()
        res.append(value)
        if not value.endswith('\n'):
            res.append('')
    return '\n'.join(res)
# end generic helpers

__version__ = open("src/wadllib/version.txt").read().strip()

install_requires = [
    'setuptools',
    'lazr.uri',
    ]
if sys.version < '2.5':
    # This module is in the standard library as of Python 2.5.  In Python 3,
    # it doesn't work when fetched separately.
    install_requires.append('elementtree')
if sys.version < '2.6':
    # This module is in the standard library as of Python 2.6.  In Python 3,
    # it doesn't work when fetched separately.
    install_requires.extend('simplejson')

setup(
    name='wadllib',
    version=__version__,
    packages=find_packages('src'),
    package_dir={'':'src'},
    include_package_data=True,
    zip_safe=False,
    maintainer='LAZR Developers',
    maintainer_email='lazr-developers@lists.launchpad.net',
    description=open('README.txt').readline().strip(),
    long_description=generate(
        'src/wadllib/README.txt',
        'src/wadllib/NEWS.txt'),
    license='LGPL v3',
    install_requires=install_requires,
    url='https://launchpad.net/wadllib',
    download_url= 'https://launchpad.net/wadllib/+download',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        ],
    extras_require=dict(
        docs=['Sphinx',
              'z3c.recipe.sphinxdoc']
    ),
    test_suite='wadllib.tests',
    )
