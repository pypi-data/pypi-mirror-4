stringlike
==========

A Python library for implementing string-like classes and lazy strings.

[![Build Status](https://secure.travis-ci.org/CovenantEyes/py_stringlike.png?branch=master)](http://travis-ci.org/CovenantEyes/py_stringlike)


Installation
------------

`stringlike` is available from [PyPI](http://pypi.python.org/pypi/stringlike).

To install:

    $ pip install stringlike

Or from the source:

    $ python setup.py install


Usage
-----

To implement your own `StringLike` class, inherit from `StringLike` and
implement the `__str__` magic function, like this:

    from stringlike import StringLike
    
    class StringyThingy(StringLike):
        def __str__(self):
            return "A string representation of my class."


Use the provided lazy string implementations like this:

    from stringlike.lazy import LazyString, CachedLazyString

    print "This was lazily {str}".format(str=LazyString(lambda: "generated"))
    print "This is {str}".format(str=CachedLazyString(lambda: "cached"))


A more detailed example can be found
[here](http://developer.covenanteyes.com/stringlike-in-python/).


Unit Tests
----------

To run the unit tests, do this:

    $ python test/run_tests.py


To see the latest test results, check out `stringlike`'s
[Travis CI page](http://travis-ci.org/#!/CovenantEyes/py_stringlike).


Acknowledgements
----------------

Special thanks to [Eric Shull](https://github.com/exupero) for much Python
help!


License
-------

This package is released under the
[MIT License](http://www.opensource.org/licenses/mit-license.php).
(See LICENSE.txt.)
