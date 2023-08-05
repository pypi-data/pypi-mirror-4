# -*- coding: utf-8 -*-
'''blade repeating tests.'''

from stuf.six import unittest


class TestXReduce(unittest.TestCase):

    def test_xflatten(self):
        from blade.xreduce import xflatten
        self.assertEqual(
            list(xflatten([[[1, [2], [3, [[4]]]], 'here']])),
            [1, 2, 3, 4, 'here'],
        )

    def test_xreduce(self):
        from blade.xreduce import xreduce
        self.assertEqual(xreduce((1, 2, 3), lambda x, y: x + y), 6)
        self.assertEqual(xreduce((1, 2, 3), lambda x, y: x + y, 1), 7)
        self.assertEqual(
            xreduce(([0, 1], [2, 3], [4, 5]), lambda x, y: x + y, invert=True),
            [4, 5, 2, 3, 0, 1],
        )
        self.assertEqual(
            xreduce([[0, 1], [2, 3], [4, 5]], lambda x, y: x + y, [0, 0], True),
            [4, 5, 2, 3, 0, 1, 0, 0],
        )
