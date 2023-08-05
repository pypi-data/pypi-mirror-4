# -*- coding: utf-8 -*-
'''blade filtering tests.'''

from stuf.six import unittest


class stooges: #@IgnorePep8
    name = 'moe'
    age = 40
class stoog2: #@IgnorePep8
    name = 'larry'
    age = 50
class stoog3: #@IgnorePep8
    name = 'curly'
    age = 60
    class stoog4: #@IgnorePep8
        name = 'beastly'
        age = 969


class stooge: #@IgnorePep8
    name = 'moe'
    age = 40
class stooge2(stooge): #@IgnorePep8
    pname = 'larry'
    page = 50
class stooge3(stoog2): #@IgnorePep8
    aname = 'curly'
    rage = 60
    class stooge4(stooge): #@IgnorePep8
        kname = 'beastly'
        mage = 969


class TextXFilter(unittest.TestCase):

    def test_xgroup(self,):
        from blade.xfilter import xgroup
        self.assertEqual(
            list(xgroup([1.3, 2.1, 2.4])),
            [(1.3, (1.3,)), (2.1, (2.1,)), (2.4, (2.4,))],
        )
        from math import floor
        self.assertEqual(
            list(xgroup([1.3, 2.1, 2.4], floor)),
            [(1.0, (1.3,)), (2.0, (2.1, 2.4))]
        )

    def test_xtraverse(self):
        self.maxDiff = None
        from blade.xfilter import xtraverse
        from stuf.collects import ChainMap, OrderedDict
        test = lambda x: not x[0].startswith('__')
        self.assertEqual(
            list(xtraverse([stoog3], test))[0],
            ChainMap(OrderedDict([
                ('classname', 'stoog3'), ('age', 60), ('name', 'curly')]),
                OrderedDict([
                ('age', 969), ('name', 'beastly'), ('classname', 'stoog4')]))
        )
        self.assertEqual(
            list(xtraverse([stooge, stooge2, stooge3], test)),
            [ChainMap(OrderedDict([
                ('classname', 'stooge'), ('age', 40), ('name', 'moe')])),
            ChainMap(
                OrderedDict([
                    ('classname', 'stooge'), ('age', 40), ('name', 'moe'),
                    ('classname', 'stooge2'), ('page', 50), ('pname', 'larry')
                ])
            ),
            ChainMap(OrderedDict([
                ('classname', 'stooge3'), ('age', 50), ('aname', 'curly'),
                ('name', 'larry'), ('rage', 60)]), OrderedDict([('age', 40),
                ('kname', 'beastly'), ('mage', 969), ('name', 'moe'),
                ('classname', 'stooge4')]))
        ])
        def test(x): #@IgnorePep8
            if x[0] == 'name':
                return True
            elif x[0].startswith('__'):
                return True
            return False
        self.assertEqual(
            list(xtraverse([stooges, stoog2, stoog3], test, True)),
            [ChainMap(OrderedDict([('classname', 'stooges'), ('age', 40)])),
            ChainMap(OrderedDict([('classname', 'stoog2'), ('age', 50)])),
            ChainMap(
                OrderedDict([('classname', 'stoog3'), ('age', 60)]),
                OrderedDict([('classname', 'stoog4'), ('age', 969)])
            )],
        )

    def test_xattrs(self):
        from stuf import stuf
        from blade.xfilter import xattrs
        stooge = [
            stuf(name='moe', age=40),
            stuf(name='larry', age=50),
            stuf(name='curly', age=60)
        ]
        self.assertEqual(
            list(xattrs(stooge, 'name')), ['moe', 'larry', 'curly']
        )
        self.assertEqual(
            list(xattrs(stooge, 'name', 'age')),
            [('moe', 40), ('larry', 50), ('curly', 60)],
        )
        self.assertEqual(list(xattrs(stooge, 'place')), [])

    def test_xitems(self):
        from blade.xfilter import xitems
        stooge = [
            dict(name='moe', age=40),
            dict(name='larry', age=50),
            dict(name='curly', age=60),
        ]
        self.assertEqual(
            list(xitems(stooge, 'name')), ['moe', 'larry', 'curly'],
        )
        self.assertEqual(
            list(xitems(stooge, 'name', 'age')),
            [('moe', 40), ('larry', 50), ('curly', 60)],
        )
        stooge = [['moe', 40], ['larry', 50], ['curly', 60]]
        self.assertEqual(list(xitems(stooge, 0)), ['moe', 'larry', 'curly'])
        self.assertEqual(list(xitems(stooge, 1)), [40, 50, 60])
        self.assertEqual(list(xitems(stooge, 'place')), [])

    def test_xfilter(self):
        from blade.xfilter import xfilter
        self.assertEqual(
            list(xfilter(
                [1, 2, 3, 4, 5, 6], lambda x: x % 2 == 0, invert=True
            )),
            [1, 3, 5]
        )
        self.assertEqual(
            list(xfilter([1, 2, 3, 4, 5, 6], lambda x: x % 2 == 0)), [2, 4, 6]
        )

    def test_xtruefalse(self):
        from blade.xfilter import xtruefalse
        results = xtruefalse([1, 2, 3, 4, 5, 6], lambda x: x % 2 == 0)
        self.assertEqual(
            (tuple(results.true), tuple(results.false)),
            ((2, 4, 6), (1, 3, 5))
        )

    def test_xmembers(self):
        from blade.xfilter import xmembers
        self.assertEqual(
            list(xmembers([stoog3], lambda x: not x[0].startswith('__'))),
            [('age', 60), ('name', 'curly'), ('stoog4', stoog3.stoog4)],
        )

    def test_xmro(self):
        from blade.xfilter import xmro
        results = xmro([stooge3])
        self.assertIn(stooge3, results)
        self.assertIn(stoog2, results)
