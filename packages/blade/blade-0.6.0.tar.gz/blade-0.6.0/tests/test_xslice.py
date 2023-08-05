# -*- coding: utf-8 -*-
'''blade slicing tests.'''

from stuf.six import unittest


class TestXSlice(unittest.TestCase):

    def test_xdice(self):
        from blade.xslice import xdice
        self.assertEqual(
            list(xdice(('moe', 'larry', 'curly', 30, 40, 50, True), 2, 'x')),
            [('moe', 'larry'), ('curly', 30), (40, 50), (True, 'x')]
        )

    def test_xfirst(self):
        from blade.xslice import xfirst
        self.assertEqual(list(xfirst([5, 4, 3, 2, 1])), [5])
        self.assertEqual(list(xfirst([5, 4, 3, 2, 1], 2)), [5, 4])

    def test_xat(self):
        from blade.xslice import xat
        self.assertEqual(xat((5, 4, 3, 2, 1), 2), 3)
        self.assertEqual(xat((5, 4, 3, 2, 1), 10, 11), 11)

    def test_xlast(self):
        from blade.xslice import xlast
        self.assertEqual(list(xlast((5, 4, 3, 2, 1))), [1])
        self.assertEqual(list(xlast((5, 4, 3, 2, 1), 2)), [2, 1])

    def test_xinitial(self):
        from blade.xslice import xinitial
        self.assertEqual(list(xinitial([5, 4, 3, 2, 1])), [5, 4, 3, 2])

    def test_xrest(self):
        from blade.xslice import xrest
        self.assertEqual(list(xrest([5, 4, 3, 2, 1])), [4, 3, 2, 1])

    def test_xchoice(self):
        from blade.xslice import xchoice
        self.assertEqual(len([xchoice([1, 2, 3, 4, 5, 6])]), 1)

    def test_xsample(self):
        from blade.xslice import xsample
        self.assertEqual(len(list(xsample([1, 2, 3, 4, 5, 6], 3))), 3)
