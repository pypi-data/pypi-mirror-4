# -*- coding: utf-8 -*-
'''blade comparison tests.'''

import platform

PYPY = platform.python_implementation() == 'PyPy'

from stuf.six import unittest


class TestXCmp(unittest.TestCase):

    def test_xall(self):
        from blade.xcmp import xall
        self.assertFalse(xall([True, 1, None, 'yes'], bool))
        self.assertTrue(xall([2, 4, 6, 8], lambda x: x % 2 == 0))

    def test_xany(self):
        from blade.xcmp import xany
        self.assertTrue(xany([None, 0, 'yes', False], bool))
        self.assertTrue(xany([1, 4, 5, 9], lambda x: x % 2 == 0))

    def test_xdiff(self):
        from blade.xcmp import xdiff
        self.assertEqual(
            xdiff(([1, 2, 3, 4, 5], [5, 2, 10], [10, 11, 2])), set([1, 3, 4]),
        )
        self.assertEqual(
            xdiff(([1, 3, 4, 5], [5, 2, 10], [10, 11, 2]), True),
            set([3, 1, 11, 4] if PYPY else [1, 3, 4, 11]),
        )

    def test_xintersect(self):
        from blade.xcmp import xintersect
        self.assertEqual(
            xintersect(([1, 2, 3], [101, 2, 1, 10], [2, 1])), set([1, 2]),
        )

    def test_xunion(self):
        from blade.xcmp import xunion
        self.assertEqual(
            xunion(([1, 2, 3], [101, 2, 1, 10], [2, 1])),
            set([10, 1, 2, 3, 101] if PYPY else [1, 10, 3, 2, 101]),
        )

    def test_xunique(self):
        from blade.xcmp import xunique
        self.assertEqual(
            list(xunique([1, 2, 1, 3, 1, 4])), [1, 2, 3, 4]
        )
        self.assertEqual(
            list(xunique([1, 2, 1, 3, 1, 4], round)), [1, 2, 3, 4],
        )
















