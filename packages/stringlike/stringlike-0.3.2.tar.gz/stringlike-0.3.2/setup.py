#!/usr/bin/env python

# stringlike's setup.py
from distutils.core import setup

from stringlike import __version__

setup(
    name = 'stringlike',
    packages = ['stringlike'],
    version = __version__,
    description = 'Classes for mimicking string behavior',
    author = 'Elliot Cameron',
    author_email = 'elliot.cameron@covenanteyes.com',
    url = 'https://github.com/CovenantEyes/py_stringlike',
    download_url = 'https://github.com/CovenantEyes/py_stringlike/tarball/v' + __version__,
    keywords = ['string', 'lazy'],
    platforms = ['any'],
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    long_description = """
String-Like Classes
-------------------

Provides a ``StringLike`` class that adds the behavior of Python's built-in
``string`` to its children. This is useful when you want to implement a class
that behaves like a string but encapsulates some additional functionality
that a normal string doesn't provide.

Additionally provides ``LazyString`` and ``CachedLazyString`` classes which
behave exactly like strings but allow strings to be constructed in a thunk
(i.e. lazily) instead of strictly (i.e. immediately).

An example of how it can be used:
http://developer.covenanteyes.com/stringlike-in-python/"""
)
