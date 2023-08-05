# -*- coding: utf-8 -*-
''':class:`blade` comparison operations'''

from functools import reduce, partial

from stuf.base import identity
from stuf.six import map as xmap, next


def xall(iterable, test):
    '''
    Discover if `test` is :data:`True` for **all** items in :term:`iterable`.

    :argument iterable: :term:`iterable`
    :argument test: filtering :func:`callable`
    :return: :func:`bool`

    >>> from blade.xcmp import xall
    >>> xall([2, 4, 6, 8], lambda x: x % 2 == 0)
    True
    '''
    return all(xmap(test, iterable))


def xany(iterable, test):
    '''
    Discover if `test` is :data:`True` for **any** items in :term:`iterable`.

    :argument iterable: :term:`iterable`.
    :argument test: filtering :func:`callable`
    :return: :func:`bool`

    >>> from blade.xcmp import xany
    >>> xany([1, 4, 5, 9], lambda x: x % 2 == 0)
    True
    '''
    return any(xmap(test, iterable))


def xdiff(iterable, symmetric=False):
    '''
    Discover difference within a series of :term:`iterable` items in
    :term:`iterable`.

    :argument iterable: :term:`iterable`
    :keyword bool symmetric: return symmetric difference
    :return: :term:`iterator` of items

    >>> from blade.xcmp import xdiff
    >>> # default behavior
    >>> list(xdiff([[1, 2, 3, 4, 5], [5, 2, 10], [10, 11, 2]]))
    [1, 3, 4]
    >>> # symmetric difference
    >>> list(xdiff([[1, 2, 3, 4, 5], [5, 2, 10], [10, 11, 2]], True))
    [1, 2, 3, 4, 11]
    '''
    if symmetric:
        test = partial(lambda s, x, y: s(x).symmetric_difference(y), set)
    else:
        test = partial(lambda s, x, y: s(x).difference(y), set)
    return reduce(test, iterable)


def xintersect(iterable):
    '''
    Discover intersection within a series of :term:`iterable` items in
    :term:`iterable`.

    :argument iterable: :term:`iterable`
    :return: :term:`iterator` of items

    >>> from blade.xcmp import xintersect
    >>> list(xintersect([[1, 2, 3], [101, 2, 1, 10], [2, 1]]))
    [1, 2]
    '''
    return reduce(partial(lambda s, x, y: s(x).intersection(y), set), iterable)


def xunion(iterable):
    '''
    Discover union within a series of :term:`iterable` items in
    :term:`iterable`.

    :argument iterable: :term:`iterable`
    :return: :term:`iterator` of items

    >>> from blade.xcmp import xunion
    >>> list(xunion([[1, 2, 3], [101, 2, 1, 10], [2, 1]]))
    [1, 10, 3, 2, 101]
    '''
    return reduce(partial(lambda s, x, y: s(x).union(y), set), iterable)


def xunique(iterable, test=None):
    '''
    Discover unique items in :term:`iterable` that pass `test`.

    :argument iterable: :term:`iterable`
    :argument test: filtering :func:`callable`
    :return: :term:`iterator` of items

    >>> from blade.xcmp import xunique
    >>> # no key function
    >>> list(xunique([1, 2, 1, 3, 1, 4]))
    [1, 2, 3, 4]
    >>> # with key function
    >>> list(xunique([1, 2, 1, 3, 1, 4], round))
    [1.0, 2.0, 3.0, 4.0]
    '''
    def unique(key, iterable, _n=next):
        seen = set()
        seenadd = seen.add
        try:
            while 1:
                element = key(_n(iterable))
                if element not in seen:
                    yield element
                    seenadd(element)
        except StopIteration:
            pass
    return unique(identity if test is None else test, iter(iterable))
