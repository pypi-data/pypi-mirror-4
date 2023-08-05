# -*- coding: utf-8 -*-
'''stuf iterables.'''

from functools import partial
from itertools import starmap

from stuf.six import items, map, next


def _xhaust(call, iterable, exception=StopIteration, n=next, map=map):
    '''Call function `call` on an `iterable` until it's exhausted.'''
    iterable = map(call, iterable)
    try:
        while 1:
            n(iterable)
    except exception:
        pass


def breakcount(call, length):
    '''Call function `call` until it reaches its original `length`.'''
    while length:
        yield call()
        length -= 1


def count(iterable, enumerate=enumerate, next=next, S=StopIteration):
    '''Lazily calculate number of items in `iterable`.'''
    counter = enumerate(iterable, 1)
    idx = ()
    while 1:
        try:
            idx = next(counter)
        except S:
            try:
                return next(iter(idx))
            except S:
                return 0


def deferfunc(call):
    '''Defer running `call`.'''
    yield call()


def deferiter(iterator):
    '''Defer running `iterator`.'''
    yield next(iterator)


def exhaust(iterable, exception=StopIteration, _n=next):
    '''Call `next` on an `iterable` until it's exhausted.'''
    try:
        while 1:
            _n(iterable)
    except exception:
        pass


def exhaustmap(call, mapping, filter=None, exception=StopIteration, _n=next):
    '''Call `call` with optional `filter` on a `mapping` until exhausted.'''
    iterable = starmap(
        call,
        items(mapping) if filter is None else filter(filter, items(mapping)),
    )
    try:
        while 1:
            _n(iterable)
    except exception:
        pass


def gauntlet(throws, this):
    '''Run sequence of callables in `thrown` on `this` object.'''
    for thrown in throws:
        this = thrown(this)
    return this


def iterexcept(call, exception, start=None):
    '''
    Call function `call` until `exception` is raised.

    from Raymond Hettinger Python Cookbook recipe # 577155
    '''
    try:
        if start is not None:
            yield start()
        while 1:
            yield call()
    except exception:
        pass


partmap = partial(
    lambda m, p, c, d, *a, **k: m(p(c, *a, **k), d), map, partial,
)
exhaustcall = partial(_xhaust, map=map)
exhauststar = partial(_xhaust, map=starmap)
xpartmap = partial(
    lambda x, b, c, d, *a, **k: x(b(c, *a, **k), d), exhaustcall, partial,
)
xpartstar = partial(
    lambda x, b, c, d, *a, **k: x(b(c, *a, **k), d), exhauststar, partial,
)
xpartitems = partial(
    lambda x, p, c, i, f=None, *a, **k: x(p(c, *a, **k), i, f),
    exhaustmap,
    partial,
)
