# -*- coding: utf-8 -*-
''':class:`blade` filtering operations'''

from collections import namedtuple
from inspect import getmro, isclass
from itertools import chain, tee, groupby
from operator import attrgetter, itemgetter

from stuf.base import identity
from stuf.six.moves import filterfalse  # @UnresolvedImport
from stuf.deep import selfname, members
from stuf.six import filter, map as xmap, next
from stuf.collects import OrderedDict, ChainMap

Group = namedtuple('Group', 'keys groups')
TrueFalse = namedtuple('TrueFalse', 'true false')
xmerge = chain.from_iterable


def xattrs(iterable, *names):
    '''
    Collect :term:`attribute` values from items in :term:`iterable` that match
    an :term:`attribute` name in `names`.

    :argument iterable: :term:`iterable`
    :argument str names: attribute names
    :return: :term:`iterator` of values

    >>> from blade.xfilter import xattrs
    >>> from stuf import stuf
    >>> stooge = [
    ...    stuf(name='moe', age=40),
    ...    stuf(name='larry', age=50),
    ...    stuf(name='curly', age=60),
    ... ]
    >>> list(xattrs(stooge, 'name'))
    ['moe', 'larry', 'curly']
    >>> # multiple attribute names
    >>> list(xattrs(stooge, 'name', 'age'))
    [('moe', 40), ('larry', 50), ('curly', 60)]
    >>> # no attrs named 'place'
    >>> list(xattrs(stooge, 'place'))
    []
    '''
    def attrs(iterable, _n=next):
        try:
            get = attrgetter(*names)
            while 1:
                try:
                    yield get(_n(iterable))
                except AttributeError:
                    pass
        except StopIteration:
            pass
    return attrs(iter(iterable))


def xfilter(iterable, test, invert=False):
    '''
    Collect items in :term:`iterable` matched by `test`.

    :argument iterable: :term:`iterable`

    :argument test: filtering :func:`callable`

    :keyword bool invert: collect items in :term:`iterable` that
      `test``test` is :data:`False` rather than :data:`True` for

    :return: :term:`iterator` of :data:`True` or, alternatively, :data:`False`
      items

    >>> from blade.xfilter import xfilter
    >>> # filter for true values
    >>> list(xfilter([1, 2, 3, 4, 5, 6], lambda x: x % 2 == 0))
    [2, 4, 6]
    >>> # filter for false values
    >>> list(xfilter([1, 2, 3, 4, 5, 6], lambda x: x % 2 == 0, invert=True))
    [1, 3, 5]
    '''
    return (filterfalse if invert else filter)(test, iterable)


def xgroup(iterable, test=None):
    '''
    Group items in `iterable` using `test` as the :term:`key function`.

    :argument iterable: :term:`iterable`

    :argument test: filtering :func:`callable`

    :return: :term:`iterator` of :func:`~collections.namedtuple`\s of
      ``Group(keys=keys, groups=tuple)``

    >>> from blade.xfilter import xgroup
    >>> # default grouping
    >>> list(xgroup([1.3, 2.1]))
    [Group(keys=1.3, groups=(1.3,)), Group(keys=2.1, groups=(2.1,))]
    >>> from math import floor
    >>> # use test for key function
    >>> list(xgroup([1.3, 2.1, 2.4], floor))
    [Group(keys=1.0, groups=(1.3,)), Group(keys=2.0, groups=(2.1, 2.4))]
    '''
    def grouper(test, iterable, _n=next, _g=Group, _t=tuple):
        try:
            it = groupby(sorted(iterable, key=test), test)
            while 1:
                k, v = _n(it)
                yield _g(k, _t(v))
        except StopIteration:
            pass
    return grouper(identity if test is None else test, iterable)

def xitems(iterable, *keys):
    '''
    Collect values from items in :term:`iterable` (usually a :term:`sequence` or
    :term:`mapping`) that match a **key** found in `keys`.

    :argument iterable: :term:`iterable`
    :param str keys: keys or indices
    :return: :term:`iterator` of items

    >>> from blade.xfilter import xitems
    >>> stooge = [
    ...    dict(name='moe', age=40),
    ...    dict(name='larry', age=50),
    ...    dict(name='curly', age=60),
    ... ]
    >>> # get items from mappings like dictionaries, etc...
    >>> list(xitems(stooge, 'name'))
    ['moe', 'larry', 'curly']
    >>> list(xitems(stooge, 'name', 'age'))
    [('moe', 40), ('larry', 50), ('curly', 60)]
    >>> # get items from sequences like lists, tuples, etc...
    >>> stooge = [['moe', 40], ['larry', 50], ['curly', 60]]
    >>> list(xitems(stooge, 0))
    ['moe', 'larry', 'curly']
    >>> list(xitems(stooge, 1))
    [40, 50, 60]
    >>> list(xitems(stooge, 'place'))
    []
    '''
    def itemz(iterable, _n=next):
        try:
            get = itemgetter(*keys)
            while 1:
                try:
                    yield get(_n(iterable))
                except (IndexError, KeyError, TypeError):
                    pass
        except StopIteration:
            pass
    return itemz(iter(iterable))


def xmembers(iterable, test, inverse=False):
    '''
    Collect values shallowly from classes or objects in :term:`class`\es in
    :term:`iterable` matched by `test`.

    :argument iterable: :term:`iterable`

    :argument test: filtering :func:`callable`

    :keyword bool invert: collect items in :term:`iterable` that
      `test` is :data:`False` rather than :data:`True` for

    :return: :term:`iterator` of values

    >>> from blade.xfilter import xmembers
    >>> class stooges:
    ...    name = 'moe'
    ...    age = 40
    >>> class stoog2:
    ...    name = 'larry'
    ...    age = 50
    >>> class stoog3:
    ...    name = 'curly'
    ...    age = 60
    ...    class stoog4:
    ...        name = 'beastly'
    ...        age = 969
    >>> list(xmembers([stoog3], lambda x: not x[0].startswith('__'))) # doctest: +SKIP
    [('age', 60), ('name', 'curly'), ('stoog4', stoog3.stoog4)]
    '''
    return xfilter(xmerge(xmap(members, iterable)), test, inverse)


def xmro(iterable):
    '''
    Extract classes in the :term:`method resolution order` of classes or objects
    in :term:`class`\es in :term:`iterable`.

    :argument iterable: :term:`iterable`
    :return: :term:`iterator` of :term:`class`\es

    >>> from blade.xfilter import xmro
    >>> class stooges:
    ...    name = 'moe'
    ...    age = 40
    >>> class stoog2(stooges):
    ...    name = 'larry'
    ...    age = 50
    >>> class stoog3(stoog2):
    ...    name = 'curly'
    ...    age = 60
    ...    class stoog4:
    ...        name = 'beastly'
    ...        age = 969
    >>> results = list(xmro([stoog3]))
    >>> stooges in results
    True
    >>> stoog3 in results
    True
    >>> stoog2 in results
    True
    '''
    return xmerge(xmap(getmro, iterable))


def xtraverse(iterable, test, invert=False):
    '''
    Collect values from deeply :term:`nested scope`\s from items in
    :term:`iterable` matched by `test`.

    :argument iterable: :term:`iterable`

    :argument test: filtering :func:`callable`

    :keyword bool invert: collect items in :term:`iterable` that
      `test` is :data:`False` rather than :data:`True` for

    :return: :term:`iterator` of `ChainMaps <http://docs.python.org/dev/
      library/collections.html#collections.ChainMap>`_ containing
      :class:`~collections.OrderedDict`

    >>> from blade.xfilter import xtraverse
    >>> class stooge:
    ...    name = 'moe'
    ...    age = 40
    >>> class stooge2:
    ...    name = 'larry'
    ...    age = 50
    >>> class stooge3:
    ...    name = 'curly'
    ...    age = 60
    ...    class stooge4(object):
    ...        name = 'beastly'
    ...        age = 969
    >>> def test(x):
    ...    if x[0] == 'name':
    ...        return True
    ...    elif x[0].startswith('__'):
    ...        return True
    ...    return False
    >>> # using test while filtering for False values
    >>> list(xtraverse([stooge, stooge2, stooge3], test, invert=True)) # doctest: +NORMALIZE_WHITESPACE
    [ChainMap(OrderedDict([('classname', 'stooge'), ('age', 40)])),
    ChainMap(OrderedDict([('classname', 'stooge2'), ('age', 50)])),
    ChainMap(OrderedDict([('classname', 'stooge3'), ('age', 60)]),
    OrderedDict([('age', 969), ('classname', 'stooge4')]))]
    '''
    ifilter = filterfalse if invert else filter
    def members(iterable):  # @IgnorePep8
        mro = getmro(iterable)
        names = iter(dir(iterable))
        beenthere = set()
        adder = beenthere.add
        try:
            OD = OrderedDict
            vz = vars
            cn = chain
            ga = getattr
            ic = isclass
            nx = next
            while 1:
                name = nx(names)
                # yes, it's really supposed to be a tuple
                for base in cn([iterable], mro):
                    var = vz(base)
                    if name in var:
                        obj = var[name]
                        break
                else:
                    obj = ga(iterable, name)
                if (name, obj) in beenthere:
                    continue
                else:
                    adder((name, obj))
                if ic(obj):
                    yield name, OD((k, v) for k, v in ifilter(
                        test, members(obj),
                    ))
                else:
                    yield name, obj
        except StopIteration:
            pass
    def traverse(iterable):  # @IgnorePep8
        try:
            iterable = iter(iterable)
            OD = OrderedDict
            sn = selfname
            nx = next
            while 1:
                iterator = nx(iterable)
                chaining = ChainMap()
                chaining['classname'] = sn(iterator)
                cappend = chaining.maps.append
                for k, v in ifilter(test, members(iterator)):
                    if isinstance(v, OD):
                        v['classname'] = k
                        cappend(v)
                    else:
                        chaining[k] = v
                yield chaining
        except StopIteration:
            pass
    return traverse(iterable)


def xtruefalse(iterable, test):
    '''
    Divide items in :term:`iterable` into two :term:`iterable`\s, the first
    everything `test` is :data:`True` for and the second everything `test` is
    :data:`False` for.

    :argument iterable: :term:`iterable`
    :argument test: filtering :func:`callable`

    :return: :func:`~collections.namedtuple` of two :term:`iterator`\s, one of
      items for which `test` is :data:`True` and one for which `test` is
      :data:`False`.

    >>> from blade.xfilter import xtruefalse
    >>> divide = xtruefalse([1, 2, 3, 4, 5, 6], lambda x: x % 2 == 0)
    >>> tuple(divide.true)
    (2, 4, 6)
    >>> tuple(divide.false)
    (1, 3, 5)
    '''
    truth, false = tee(iterable)
    return TrueFalse(filter(test, truth), filterfalse(test, false))
