"""
Contains classes for representing lazy strings (i.e. strings that aren't constructed until they're
needed).
"""

from stringlike.core import StringLike


class LazyString(StringLike):
    """
    A lazy string *without* caching. The resulting string is regenerated for every request.
    """
    def __init__(self, func):
        """
        Creates a `LazyString` object using `func` as the delayed closure. `func` must return a
        string.
        """
        self._func = func

    def __str__(self):
        """
        Returns the actual string.
        """
        return self._func()


class CachedLazyString(LazyString):
    """
    A lazy string with caching.
    """
    def __init__(self, func):
        """
        Uses `__init__()` from the parent and initializes a cache.
        """
        super(CachedLazyString, self).__init__(func)
        self._cache = None

    def __str__(self):
        """
        Returns the actual string and caches the result.
        """
        if not self._cache:
            self._cache = self._func()
        return self._cache
