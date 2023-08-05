# -*- coding: utf-8 -*-
''':class:`blade` mapping operations'''

from copy import deepcopy
from operator import methodcaller
from itertools import chain, repeat, starmap

from stuf.iterable import partmap, partstar
from stuf.base import identity, dualidentity
from stuf.six import items, keys as keyz, map as xmap, values as valuez

xmerge = chain.from_iterable


def xargmap(iterable, callable, merge=False, *args):
    '''
    Feed each items in `iterable` to `callable` as :term:`positional argument`\s.

    :argument iterable: :term:`iterable`
    :argument callable: mapped :func:`callable`

    :keyword bool merge: merge global positional :meth:`params` with positional
      arguments derived from items in `iterable` when passed to `callable`

    >>> from blade.xmap import xargmap
    >>> # default behavior
    >>> list(xargmap([(1, 2), (2, 3), (3, 4)], lambda x, y: x * y))
    [2, 6, 12]
    >>> # merge global positional arguments with iterable arguments
    >>> list(xargmap(
    ...   [(1, 2), (2, 3), (3, 4)],
    ...   lambda x, y, z, a, b: x * y * z * a * b,
    ...   True,
    ...   7, 8, 9,
    ...  ))
    [1008, 3024, 6048]
    '''
    if merge:
        return partstar(lambda f, *arg: f(*(arg + args)), iterable, callable)
    return starmap(callable, iterable)


def xcopy(iterable):
    '''
    Duplicate each items in `iterable`.

    :argument iterable: :term:`iterable`

    >>> from blade.xmap import xcopy
    >>> list(xcopy([[1, [2, 3]], [4, [5, 6]]]))
    [[1, [2, 3]], [4, [5, 6]]]
    '''
    return xmap(deepcopy, iterable)


def xinvoke(iterable, name, *args, **kw):
    '''
    Feed global :term:`positional argument`\s and :term:`keyword argument`\s to
    each items in `iterable`'s `name` :term:`method`.

    .. note::

      The original thing is returned if the return value of :term:`method`
      `name` is :data:`None`.

    :argument iterable: :term:`iterable`
    :argument str name: method name

    >>> from blade.xmap import xinvoke
    >>> # invoke list.index()
    >>> list(xinvoke([[5, 1, 7], [3, 2, 1]], 'index', 1))
    [1, 2]
    >>> # invoke list.sort() but return sorted list instead of None
    >>> list(xinvoke([[5, 1, 7], [3, 2, 1]], 'sort'))
    [[1, 5, 7], [1, 2, 3]]
    '''
    def invoke(caller, thing):
        read = caller(thing)
        return thing if read is None else read
    return partmap(invoke, iterable, methodcaller(name, *args, **kw))


def xkwargmap(iterable, callable, merge=False, *args, **kw):
    '''
    Feed each items in `iterable` as a :func:`tuple` of
    :term:`positional argument`\s and :term:`keyword argument`\s to `callable`.

    :argument iterable: :term:`iterable`

    :argument callable: mapped :func:`callable`

    :keyword bool merge: merge global positional or keyword :meth:`params`
      with positional and keyword arguments derived from items in `iterable`
      into a single :func:`tuple` of wildcard positional and keyword
      arguments like ``(*iterable_args + global_args, **global_kwargs +
      iterable_kwargs)`` when passed to `callable`

    >>> from blade.xmap import xkwargmap
    >>> # default behavior
    >>> test = [((1, 2), {'a': 2}), ((2, 3), {'a': 2}), ((3, 4), {'a': 2})]
    >>> def tester(*args, **kw):
    ...    return sum(args) * sum(kw.values())
    >>> list(xkwargmap(test, tester))
    [6, 10, 14]
    >>> # merging global and iterable derived positional and keyword args
    >>> list(xkwargmap(test, tester, True, 1, 2, 3, b=5, w=10, y=13))
    [270, 330, 390]
    '''
    if merge:
        def kwargmap(callable, *params):
            arg, kwarg = params
            kwarg.update(kw)
            return callable(*(arg + args), **kwarg)
    else:
        kwargmap = lambda f, x, y: f(*x, **y)
    return partstar(kwargmap, iterable, callable)


def xkeyvalue(iterable, callable=None, keys=False, values=False):
    '''
    Run `callable` on incoming :term:`mapping` things.

    :argument iterable: :term:`iterable`
    :argument callable: mapped :func:`callable`
    :keyword bool keys: collect mapping keys only
    :keyword bool values: collect mapping values only

    >>> from blade.xmap import xkeyvalue
    >>> # filter items
    >>> list(xkeyvalue(
    ... [dict([(1, 2), (2, 3), (3, 4)]), dict([(1, 2), (2, 3), (3, 4)])],
    ... lambda x, y: x * y))
    [2, 6, 12, 2, 6, 12]
    >>> # mapping keys only
    >>> list(xkeyvalue(
    ... [dict([(1, 2), (2, 3), (3, 4)]), dict([(1, 2), (2, 3), (3, 4)])],
    ... keys=True
    ... ))
    [1, 2, 3, 1, 2, 3]
    >>> # mapping values only
    >>> list(xkeyvalue(
    ... [dict([(1, 2), (2, 3), (3, 4)]), dict([(1, 2), (2, 3), (3, 4)])],
    ... values=True
    ... ))
    [2, 3, 4, 2, 3, 4]
    '''
    if keys:
        callable = identity if callable is None else callable
        return xmap(callable, xmerge(xmap(keyz, iterable)))
    elif values:
        callable = identity if callable is None else callable
        return xmap(callable, xmerge(xmap(valuez, iterable)))
    callable = dualidentity if callable is None else callable
    return starmap(callable, xmerge(xmap(items, iterable)))

def xrepeat(iterable, callable=None, n=None):
    '''
    Repeat items in `iterable` `n` times or invoke `callable` `n` times.

    :argument iterable: :term:`iterable`
    :keyword callable: :func:`callable` to repeatedly invoke
    :keyword int n: number of times to repeat

    >>> from blade.xmap import xrepeat
    >>> # repeat iterable
    >>> list(xrepeat([40, 50, 60], n=3))
    [(40, 50, 60), (40, 50, 60), (40, 50, 60)]
    >>> # with callable
    >>> list(xrepeat([40, 50, 60], lambda *args: list(args), 3))
    [[40, 50, 60], [40, 50, 60], [40, 50, 60]]
    '''
    if not callable:
        return repeat(tuple(iterable), n)
    return starmap(callable, repeat(tuple(iterable), n))