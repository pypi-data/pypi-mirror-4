#!/usr/bin/env python
import os
import sys
import doctest
try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup


def mod():
    import jsondict as mod
    return mod

docstring = lambda: mod().__doc__.strip()

open('README.md', 'w').write(docstring())
if sys.argv[-1] == 'publish':
    if not doctest.testfile('README.md', verbose=True).failed:
        os.system('python setup.py sdist upload')
        sys.exit(0)

setup(
    name         = mod().__name__,
    url          = 'https://github.com/imbolc/%s' % mod().__name__,
    version      = mod().__version__,
    description  = docstring().split('===\n')[1].strip().split('\n\n')[0],
    long_description = docstring(),

    py_modules   = [mod().__name__],
    install_requires = ['asjson'],

    author       = 'Imbolc',
    author_email = 'imbolc@imbolc.name',
    license      = 'ISC',

    classifiers  = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
    ],
)
