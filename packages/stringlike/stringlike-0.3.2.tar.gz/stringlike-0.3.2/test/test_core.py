#!/usr/bin/env python

from stringlike import StringLike
from unittest import main, TestCase


class StringMock(StringLike):
    """
    A simple mock of built-in strings using the StringLike class.
    """
    def __init__(self, string):
        """
        Take a string and use it as the representation of this class.
        """
        self.string = string

    def __str__(self):
        """
        Just return whatever we got during construction.
        """
        return self.string


class TestStringLikeMagicMethods(TestCase):
    def test_str(self):
        self.assertEqual(str(StringMock('abc')), 'abc')

    def test_eq(self):
        self.assertEqual(StringMock(''), '')
        self.assertEqual(StringMock('abc'), 'abc')

    def test_ne(self):
        self.assertNotEqual(StringMock(''), 'abc')
        self.assertNotEqual(StringMock('abc'), '')

    def test_lt(self):
        self.assertTrue(StringMock('a') < 'b')
        self.assertTrue('a' < StringMock('b'))
        self.assertTrue(StringMock('a') < StringMock('b'))

    def test_le(self):
        self.assertTrue(StringMock('a') <= 'b')
        self.assertTrue('a' <= StringMock('b'))
        self.assertTrue(StringMock('a') <= StringMock('b'))

    def test_gt(self):
        self.assertTrue(StringMock('b') > 'a')
        self.assertTrue('b' > StringMock('a'))
        self.assertTrue(StringMock('b') > StringMock('a'))

    def test_ge(self):
        self.assertTrue(StringMock('b') >= 'a')
        self.assertTrue('b' >= StringMock('a'))
        self.assertTrue(StringMock('b') >= StringMock('a'))

    def test_concat(self):
        self.assertEqual(StringMock('a') + 'bc', 'abc')
        self.assertEqual('a' + StringMock('bc'), 'abc')
        self.assertEqual(StringMock('a') + StringMock('bc'), 'abc')

    def test_multiply(self):
        self.assertEqual(StringMock('a') * 3, 'aaa')
        self.assertEqual(3 * StringMock('a'), 'aaa')

    def test_subindex(self):
        self.assertEqual(StringMock('abc')[0], 'a')
        self.assertEqual(StringMock('abc')[2], 'c')
        self.assertEqual(StringMock('abc')[1:], 'bc')
        self.assertEqual(StringMock('abc')[:-1], 'ab')
        with self.assertRaises(IndexError):
            StringMock('abc')[3]

    def test_contains(self):
        self.assertIn('a', StringMock('abc'))

    def test_len(self):
        self.assertEqual(len(StringMock('')), 0)
        self.assertEqual(len(StringMock('abc')), 3)

    def test_iter(self):
        self.assertEqual([x for x in StringMock('')], [])
        self.assertEqual([x for x in StringMock('abc')], ['a', 'b', 'c'])

        iterator = iter(StringMock('abc'))
        self.assertEqual(iterator.next(), 'a')
        self.assertEqual(iterator.next(), 'b')
        self.assertEqual(iterator.next(), 'c')
        with self.assertRaises(StopIteration):
            iterator.next()

    def test_nonzero(self):
        self.assertTrue(bool(StringMock('abc')))
        self.assertFalse(bool(StringMock('')))

    def test_and(self):
        self.assertEqual(StringMock('') and StringMock('abc'), '')
        self.assertEqual(StringMock('abc') and StringMock(''), '')
        self.assertEqual(StringMock('a') and StringMock('bc'), 'bc')

        self.assertEqual('' and StringMock('abc'), '')
        self.assertEqual(StringMock('abc') and '', '')
        self.assertEqual('a' and StringMock('bc'), 'bc')
        self.assertEqual(StringMock('a') and 'bc', 'bc')

    def test_or(self):
        self.assertEqual(StringMock('') or StringMock('abc'), 'abc')
        self.assertEqual(StringMock('abc') or StringMock(''), 'abc')
        self.assertEqual(StringMock('a') or StringMock('bc'), 'a')

        self.assertEqual('' or StringMock('abc'), 'abc')
        self.assertEqual(StringMock('abc') or '', 'abc')
        self.assertEqual('a' or StringMock('bc'), 'a')
        self.assertEqual(StringMock('a') or 'bc', 'a')

    def test_attribute_error(self):
        with self.assertRaises(AttributeError):
            StringMock('').gobbledygook()


class TestSomeStringMethods(TestCase):
    def test_capitalize(self):
        self.assertEqual(StringMock('abc').capitalize(), 'Abc')
        self.assertEqual(StringMock('ABC').capitalize(), 'Abc')

    def test_endswith(self):
        self.assertTrue(StringMock('abc').endswith('c'))
        self.assertFalse(StringMock('abc').endswith('b'))

    def test_format(self):
        self.assertEqual(StringMock('{0}').format('abc'), 'abc')


if __name__ == '__main__':
    main()
