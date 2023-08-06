##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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

import os
from os.path import join
import platform
import sys

from setuptools import setup, find_packages, Extension

README = open('README.rst').read()
CHANGES = open('CHANGES.rst').read()

# PyPy won't build the extension
py_impl = getattr(platform, 'python_implementation', lambda: None)
is_pypy = py_impl() == 'PyPy'
is_pure = 'PURE_PYTHON' in os.environ
py3k = sys.version_info >= (3, )
if is_pypy or is_pure or py3k:
    ext_modules = []
else:
    ext_modules = [
        Extension(
            name='Missing._Missing',
            include_dirs=['include', 'src'],
            sources=[join('src', 'Missing', '_Missing.c')],
            depends=[join('include', 'ExtensionClass', 'ExtensionClass.h')]),
    ]


setup(
    name='Missing',
    version='3.0',
    url='http://pypi.python.org/pypi/Missing',
    license='ZPL 2.1',
    description="Special Missing objects used in Zope2.",
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    long_description='\n\n'.join([README, CHANGES]),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Web Environment",
        "Framework :: Zope2",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    ext_modules=ext_modules,
    install_requires=['ExtensionClass >= 4.1a1'],
    include_package_data=True,
    zip_safe=False,
)
