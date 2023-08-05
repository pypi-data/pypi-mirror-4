# -*- coding: utf-8 -*-
''':class:`blade` mapping tests.'''

from stuf.six import unittest


class TestXMap(unittest.TestCase):

    def test_xrepeat(self):
        from blade.xmap import xrepeat
        test = lambda *args: list(args)
        self.assertEqual(
            list(xrepeat([40, 50, 60], n=3)),
            [(40, 50, 60), (40, 50, 60), (40, 50, 60)],
        )
        self.assertEqual(
            list(xrepeat((40, 50, 60), test, 3)),
            [[40, 50, 60], [40, 50, 60], [40, 50, 60]],
        )

    def test_xcopy(self):
        from blade.xmap import xcopy
        testlist = [[1, [2, 3]], [4, [5, 6]]]
        newlist = list(xcopy(testlist))
        self.assertFalse(newlist is testlist)
        self.assertListEqual(newlist, testlist)
        self.assertFalse(newlist[0] is testlist[0])
        self.assertListEqual(newlist[0], testlist[0])
        self.assertFalse(newlist[1] is testlist[1])
        self.assertListEqual(newlist[1], testlist[1])

    def test_xkwargmap(self):
        from blade.xmap import xkwargmap
        test = lambda *args, **kw: sum(args) * sum(kw.values())
        self.assertEqual(
            list(xkwargmap(
                [((1, 2), {'a': 2}), ((2, 3), {'a': 2}), ((3, 4), {'a': 2})],
                test,
            )),
            [6, 10, 14],
        )
        self.assertEqual(
            list(xkwargmap(
                [((1, 2), {'a': 2}), ((2, 3), {'a': 2}), ((3, 4), {'a': 2})],
                test,
                True,
                1, 2, 3, b=5, w=10, y=13
            )),
            [270, 330, 390],
        )
        self.assertEqual(
            list(xkwargmap(
                (((1, 2), {'a': 2}), ((2, 3), {'a': 2}), ((3, 4), {'a': 2})),
                test,
                False,
                1, 2, 3,
                b=5, w=10, y=13,
            )),
            [6, 10, 14],
        )

    def test_xargmap(self):
        from blade.xmap import xargmap
        self.assertEqual(
            list(xargmap(
                [(1, 2), (2, 3), (3, 4)], lambda x, y: x * y,
            )),
            [2, 6, 12],
        )
        self.assertEqual(
            list(xargmap(
                [(1, 2), (2, 3), (3, 4)],
                lambda x, y, z, a, b: x * y * z * a * b,
                True,
                7, 8, 9
            )),
            [1008, 3024, 6048],
        )
        self.assertEqual(
            list(xargmap(
                [(1, 2), (2, 3), (3, 4)],
                lambda x, y, z, a, b: x * y * z * a * b,
                True,
                7, 8, 9
            )),
            [1008, 3024, 6048],
        )

    def test_xinvoke(self):
        from blade.xmap import xinvoke
        self.assertEqual(
            list(xinvoke([[5, 1, 7], [3, 2, 1]], 'index', 1)), [1, 2],
        )
        self.assertEqual(
            list(xinvoke([[5, 1, 7], [3, 2, 1]], 'sort')),
            [[1, 5, 7], [1, 2, 3]],
        )

    def test_xkeyvalue(self):
        from blade.xmap import xkeyvalue
        self.assertEqual(
            list(xkeyvalue(
            [dict([(1, 2), (2, 3), (3, 4)]), dict([(1, 2), (2, 3), (3, 4)])],
            keys=True
            )), [1, 2, 3, 1, 2, 3],
        )
        self.assertEqual(
            list(xkeyvalue(
                [dict([(1, 2), (2, 3), (3, 4)]), dict([(1, 2), (2, 3), (3, 4)])],
                values=True
            )),
            [2, 3, 4, 2, 3, 4],
        )
        self.assertEqual(
            list(xkeyvalue(
            [dict([(1, 2), (2, 3), (3, 4)]), dict([(1, 2), (2, 3), (3, 4)])],
            lambda x, y: x * y,
            )),
            [2, 6, 12, 2, 6, 12],
        )
        self.assertEqual(
            dict(xkeyvalue(
                [dict([(1, 2), (2, 3), (3, 4)]), dict([(1, 2), (2, 3), (3, 4)])]
            )),
            dict([(1, 2), (2, 3), (3, 4)]),
        )
