# -*- coding: utf-8 -*-
''':class:`blade` mathing operations.'''

from math import fsum
from itertools import tee
from operator import truediv
from collections import deque, namedtuple

from stuf.six import next
from stuf.iterable import count
from stuf.collects import Counter

from .xslice import xslicer

Count = namedtuple('Count', 'least most overall')
MinMax = namedtuple('MinMax', 'min max')


def xaverage(iterable):
    '''
    Discover average value of numbers in `iterable`.

    :argument iterable: iterable object
    :return: a number

    >>> from blade.xmath import xaverage
    >>> xaverage([10, 40, 45])
    31.666666666666668
    '''
    i1, i2 = tee(iterable)
    return truediv(sum(i1, 0.0), count(i2))


def xcount(iterable):
    '''
    Discover how common each item in `iterable` is and the overall count of each
    item in `iterable`.

    :argument iterable: iterable object

    :return: Collects :func:`~collections.namedtuple` ``Count(least=int,
      most=int, overall=[(thing1, int), (thing2, int), ...])``

    >>> from blade.xmath import xcount
    >>> common = xcount([11, 3, 5, 11, 7, 3, 5, 11])
    >>> # least common thing
    >>> common.least
    7
    >>> # most common thing
    >>> common.most
    11
    >>> # total count for every thing
    >>> common.overall
    [(11, 3), (3, 2), (5, 2), (7, 1)]
    '''
    cnt = Counter(iterable).most_common
    commonality = cnt()
    return Count(
        # least common
        commonality[:-2:-1][0][0],
        # most common (mode)
        cnt(1)[0][0],
        # overall commonality
        commonality,
    )


def xmedian(iterable):
    '''
    Discover median value of numbers in `iterable`.

    :argument iterable: iterable object
    :return: a number

    >>> from blade.xmath import xmedian
    >>> xmedian([4, 5, 7, 2, 1])
    4
    >>> xmedian([4, 5, 7, 2, 1, 8])
    4.5
    '''
    i1, i2 = tee(sorted(iterable))
    result = truediv(count(i1) - 1, 2)
    pint = int(result)
    if result % 2 == 0:
        return xslicer(i2, pint)
    i3, i4 = tee(i2)
    return truediv(xslicer(i3, pint) + xslicer(i4, pint + 1), 2)


def xminmax(iterable):
    '''
    Discover the minimum and maximum values among items in `iterable`.

    :argument iterable: iterable object
    :return:  :func:`~collections.namedtuple` ``MinMAx(min=value, max=value)``.

    >>> from blade.xmath import xminmax
    >>> minmax = xminmax([1, 2, 4])
    >>> minmax.min
    1
    >>> minmax.max
    4
    '''
    i1, i2 = tee(iterable)
    return MinMax(min(i1), max(i2))


def xinterval(iterable):
    '''
    Discover the length of the smallest interval that can contain the value of
    every items in `iterable`.

    :argument iterable: iterable object

    :return: a number

    >>> from blade.xmath import xinterval
    >>> xinterval([3, 5, 7, 3, 11])
    8
    '''
    i1, i2 = tee(sorted(iterable))
    return deque(i1, maxlen=1).pop() - next(i2)


def xsum(iterable, start=0, precision=False):
    '''
    Discover the total value of adding `start` and items in `iterable` together.

    :argument iterable: iterable object
    :keyword start: starting number
    :type start: :func:`int` or :func:`float`
    :keyword bool precision: add floats with extended precision

    >>> from blade.xmath import xsum
    >>> # default behavior
    >>> xsum([1, 2, 3])
    6
    >>> # with a starting mumber
    >>> xsum([1, 2, 3], start=1)
    7
    >>> # add floating points with extended precision
    >>> xsum([.1, .1, .1, .1, .1, .1, .1, .1], precision=True)
    0.8
    '''
    return fsum(iterable) if precision else sum(iterable, start)
