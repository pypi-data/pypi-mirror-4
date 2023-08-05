# -*- coding: utf-8 -*-
''':class:`blade` reduction operations'''

from functools import reduce, partial

from stuf.six import isstring, next


def xflatten(iterable):
    '''
    Reduce nested items in `iterable` to flattened items in `iterable`.

    :argument iterable: :term:`iterable`

    >>> from blade.xreduce import xflatten
    >>> list(xflatten([[1, [2], [3, [[4]]]], 'here']))
    [1, 2, 3, 4, 'here']
    '''
    def flatten(iterable, _n=next, _is=isstring):
        next_ = iter(iterable)
        try:
            while 1:
                item = _n(next_)
                try:
                    # don't recur over strings
                    if _is(item):
                        yield item
                    else:
                        # do recur over other things
                        for j in flatten(item):
                            yield j
                except (AttributeError, TypeError):
                    # does not recur
                    yield item
        except StopIteration:
            pass
    return flatten(iterable)


def xreduce(iterable, callable, initial=None, invert=False):
    '''
    Reduce `iterable` items in `iterable` down to one items in `iterable` using
    `callable`.

    :argument callable: reducing :func:`callable`

    :argument iterable: :term:`iterable`

    :keyword initial: starting value

    :keyword bool invert: reduce from `the right side <http://www.zvon.org/
      other/haskell/Outputprelude/foldr_f.html>`_ of items in `iterable`

    >>> from blade.xreduce import xreduce
    >>> # reduce from left side
    >>> xreduce([1, 2, 3], lambda x, y: x + y)
    6
    >>> # reduce from left side with initial value
    >>> xreduce([1, 2, 3], lambda x, y: x + y, initial=1)
    7
    >>> # reduce from right side
    >>> xreduce([[0, 1], [2, 3], [4, 5]], lambda x, y: x + y, invert=True)
    [4, 5, 2, 3, 0, 1]
    >>> # reduce from right side with initial value
    >>> xreduce(
    ...   [[0, 1], [2, 3], [4, 5]], lambda x, y: x + y, [0, 0], invert=True
    ... )
    [4, 5, 2, 3, 0, 1, 0, 0]
    '''
    if invert:
        if initial is None:
            return reduce(partial(lambda f, x, y: f(y, x), callable), iterable)
        return reduce(partial(
            lambda f, x, y: f(y, x), callable), iterable, initial,
        )
    if initial is None:
        return reduce(callable, iterable)
    return reduce(callable, iterable, initial)
