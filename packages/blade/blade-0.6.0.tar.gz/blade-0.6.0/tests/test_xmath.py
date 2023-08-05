# -*- coding: utf-8 -*-
'''blade mathing tests.'''

from stuf.six import unittest


class TestXMath(unittest.TestCase):

    def test_xaverage(self):
        from blade.xmath import xaverage
        self.assertEqual(xaverage((10, 40, 45)), 31.666666666666668)

    def test_xcount(self):
        from blade.xmath import xcount
        common = xcount((11, 3, 5, 11, 7, 3, 11))
        self.assertEqual(common.overall, [(11, 3), (3, 2), (5, 1), (7, 1)])
        # most common
        self.assertEqual(common.most, 11)
        # least common
        self.assertEqual(common.least, 7)

    def test_xmedian(self):
        from blade.xmath import xmedian
        self.assertEqual(xmedian((4, 5, 7, 2, 1)), 4)
        self.assertEqual(xmedian((4, 5, 7, 2, 1, 8)), 4.5)

    def test_xminmax(self):
        from blade.xmath import xminmax
        self.assertEqual(xminmax((1, 2, 4)), (1, 4))
        self.assertEqual(xminmax((10, 5, 100, 2, 1000)), (2, 1000))

    def test_xinterval(self):
        from blade.xmath import xinterval
        self.assertEqual(xinterval((3, 5, 7, 3, 11)), 8)

    def test_xsum(self):
        from blade.xmath import xsum
        self.assertEqual(xsum((1, 2, 3)), 6)
        self.assertEqual(xsum((1, 2, 3), 1), 7)
        self.assertEqual(
            xsum((.1, .1, .1, .1, .1, .1, .1, .1, .1, .1), precision=True), 1.0,
        )
