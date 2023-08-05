# -*- coding: utf-8 -*-
''':class:`blade` slicing operations'''

from random import randrange
from collections import deque
from functools import partial
from itertools import islice, tee

from stuf.six import next
from stuf.six.moves import zip_longest  # @UnresolvedImport
from stuf.iterable import deferfunc, deferiter, count, partmap

xslicer = partial(lambda n, i, x, y: n(i(x, y, None)), next, islice)


def xat(iterable, n, default=None):
    '''
    :term:`Slice` off items in `iterable` found at index `n`.

    :argument iterable: :term:`iterable`
    :argument int n: index of some items in `iterable`
    :keyword default: default returned if nothing is found at `n`
    :return: :term:`iterator` of items

    >>> from blade.xslice import xat
    >>> # default behavior
    >>> xat([5, 4, 3, 2, 1], 2)
    3
    >>> # return default value if nothing found at index
    >>> xat([5, 4, 3, 2, 1], 10, 11)
    11
    '''
    return next(islice(iterable, n, None), default)


def xchoice(iterable):
    '''
    Randomly :term:`slice` off **one** items in `iterable`.

    :argument iterable: :term:`iterable`

    >>> from blade.xslice import xchoice
    >>> list(xchoice([1, 2, 3, 4, 5, 6])) # doctest: +SKIP
    3
    '''
    i1, i2 = tee(iterable)
    return xat(i1, randrange(0, count(i2)))


def xdice(iterable, n, fill=None):
    '''
    :term:`Slice` one `iterable` items in `iterable` into `n` iterable items in
    `iterable`.

    :argument iterable: :term:`iterable`
    :argument int n: number of items in `iterable` per slice
    :keyword fill: value to pad out incomplete iterables
    :return: :term:`iterator` of items

    >>> from blade.xslice import xdice
    >>> list(xdice(['moe', 'larry', 'curly', 30, 40, 50, True], 2, 'x'))
    [('moe', 'larry'), ('curly', 30), (40, 50), (True, 'x')]
    '''
    return zip_longest(fillvalue=fill, *[iter(iterable)] * n)


def xfirst(iterable, n=0):
    '''
    :term:`Slice`  off `n` things from the **starting** end of `iterable` or
    just the **first** items in `iterable`.

    :argument iterable: :term:`iterable`
    :keyword int n: number of items in `iterable`
    :return: :term:`iterator` of items

    >>> from blade.xslice import xfirst
    >>> # default behavior
    >>> list(xfirst([5, 4, 3, 2, 1]))
    [5]
    >>> # first things from index 0 to 2
    >>> list(xfirst([5, 4, 3, 2, 1], 2))
    [5, 4]
    '''
    return islice(iterable, n) if n else deferiter(iter(iterable))


def xinitial(iterable):
    '''
    :term:`Slice` off every items in `iterable` except the **last** `iterable`.

    :argument iterable: :term:`iterable`
    :return: :term:`iterator` of items

    >>> from blade.xslice import xinitial
    >>> list(xinitial([5, 4, 3, 2, 1]))
    [5, 4, 3, 2]
    '''
    i1, i2 = tee(iterable)
    return islice(i1, count(i2) - 1)


def xlast(iterable, n=0):
    '''
    :term:`Slice` off `n` things from the **tail** end of items in `iterable` or
    just the **last** items in `iterable`.

    :argument iterable: :term:`iterable`
    :keyword int n: number of items in `iterable` to slice off
    :return: :term:`iterator` of items

    >>> from blade.xslice import xlast
    >>> # default behavior
    >>> list(xlast([5, 4, 3, 2, 1]))[0]
    1
    >>> # fetch last two things
    >>> list(xlast([5, 4, 3, 2, 1], 2))
    [2, 1]
    '''
    if n:
        i1, i2 = tee(iterable)
        return islice(i1, count(i2) - n, None)
    return iter(deferfunc(deque(iterable, maxlen=1).pop))


def xrest(iterable):
    '''
    :term:`Slice` off every items in `iterable` except the **first** item.

    :argument iterable: :term:`iterable`
    :return: :term:`iterator` of items

    >>> from blade.xslice import xrest
    >>> list(xrest([5, 4, 3, 2, 1]))
    [4, 3, 2, 1]
    '''
    return islice(iterable, 1, None)


def xsample(iterable, n):
    '''
    Randomly :term:`slice` off `n` items in `iterable`.

    :argument iterable: :term:`iterable`
    :argument int n: sample size
    :return: :term:`iterator` of items

    >>> from blade.xslice import xsample
    >>> list(xsample([1, 2, 3, 4, 5, 6], 3)) # doctest: +SKIP
    [2, 4, 5]
    '''
    i1, i2 = tee(iterable)
    return partmap(
        lambda i, r, c, x: i(x, r(0, c)),
        tee(i2, n),
        islice,
        randrange,
        count(i1),
    )
