#!/usr/bin/env python
import os
import sys
import doctest
try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

import urledit


open('README.md', 'w').write(urledit.__doc__.strip())
if sys.argv[-1] == 'publish':
    if not doctest.testfile('README.md', verbose=True).failed:
        os.system('python setup.py sdist upload')
        sys.exit(1)

setup(
    name         = 'urledit',
    version      = urledit.__version__,
    description  = 'Url parsing and editing',
    url          = 'https://github.com/imbolc/urledit',

    py_modules   = ['urledit'],

    author       = 'Imbolc',
    author_email = 'imbolc@imbolc.name',
    license      = 'MIT',
    long_description = open('README.md').read(),

    classifiers  = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
    ],
)
