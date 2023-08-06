#!/usr/bin/env python
import os
import sys
try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup
import urledit



if sys.argv[-1] in ['test', 'publish']:
    import doctest

    if doctest.testfile('README.md', verbose=True).failed:
        sys.exit()

    if sys.argv[-1] == 'publish':
        os.system('python setup.py sdist upload')
        sys.exit()


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
