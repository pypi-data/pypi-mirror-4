#!/usr/bin/env python

from stringlike.lazy import LazyString, CachedLazyString
from unittest import main, TestCase


class TestLazyString(TestCase):
    def test_equality(self):
        self.assertEqual(LazyString(lambda: 'abc'), 'abc')

    def test_delay(self):
        self.evaluateCount = 0

        def func():
            self.evaluateCount += 1
            return 'abc'
        
        lazyString = LazyString(func)
        self.assertEqual(self.evaluateCount, 0)

        self.assertEqual(lazyString, 'abc')
        self.assertEqual(self.evaluateCount, 1)

        self.assertEqual(lazyString, 'abc')
        self.assertEqual(self.evaluateCount, 2)


class TestCachedLazyString(TestCase):
    def test_equality(self):
        self.assertEqual(CachedLazyString(lambda: 'abc'), 'abc')

    def test_delay(self):
        self.evaluateCount = 0

        def func():
            self.evaluateCount += 1
            return 'abc'
        
        cachedLazyString = CachedLazyString(func)
        self.assertEqual(self.evaluateCount, 0)

        self.assertEqual(cachedLazyString, 'abc')
        self.assertEqual(self.evaluateCount, 1)

        self.assertEqual(cachedLazyString, 'abc')
        self.assertEqual(self.evaluateCount, 1)


if __name__ == '__main__':
    main()
