# -*- coding: utf-8 -*-
'''stuf collections.'''

import sys
from collections import MutableMapping

from stuf.deep import getcls
from stuf.base import second, first
from stuf.six import OrderedDict, items, map as imap, get_ident

try:
    from reprlib import recursive_repr  # @UnusedImport
except ImportError:
    def recursive_repr(fillvalue='...'):
        def decorating_function(user_function):
            repr_running = set()

            def wrapper(self):  # @IgnorePep8
                key = id(self), get_ident()
                if key in repr_running:
                    return fillvalue
                repr_running.add(key)
                try:
                    result = user_function(self)
                finally:
                    repr_running.discard(key)
                return result
            # Can't use functools.wraps() here because of bootstrap issues
            wrapper.__module__ = getattr(user_function, '__module__')
            wrapper.__doc__ = getattr(user_function, '__doc__')
#            wrapper.__name__ = getattr(user_function, '__name__')
            return wrapper
        return decorating_function

if not first(sys.version_info) == 2 and second(sys.version_info) < 7:
    from collections import Counter
else:
    from heapq import nlargest

    class Counter(dict):

        '''dict subclass for counting hashable items'''

        def __init__(self, iterable=None, **kw):
            '''
            If given, count elements from an input iterable. Or, initialize
            count from another mapping of elements to their counts.
            '''
            super(Counter, self).__init__()
            self.update(iterable, **kw)

        def most_common(self, n=None, nl=nlargest, i=items, g=second):
            '''
            List the n most common elements and their counts from the most
            common to the least

            If n is None, then list all element counts.
            '''
            # Emulate Bag.sortedByCount from Smalltalk
            if n is None:
                return sorted(i(self), key=g, reverse=True)
            return nl(n, i(self), key=g)

        def update(self, iterable=None):
            '''like dict.update() but add counts instead of replacing them'''
            if iterable is not None:
                self_get = self.get
                for elem in iterable:
                    self[elem] = self_get(elem, 0) + 1


try:
    from collections import ChainMap  # @UnusedImport
except ImportError:
    # not until Python >= 3.3
    class ChainMap(MutableMapping):

        '''
        `ChainMap` groups multiple dicts (or other mappings) together to create
        a single, updateable view.

        The underlying mappings are stored in a `list`. That `list` is public
        and can accessed or updated using the `maps` attribute. There is no
        other state.

        Lookups search the underlying mappings successively until a key is
        found. In contrast, writes, updates, and deletions only operate on the
        first mapping.
        '''

        def __init__(self, *maps):
            '''
            Initialize `ChainMap` by setting *maps* to the given mappings.
            If no mappings are provided, a single empty dictionary is used.
            '''
            # always at least one map
            self.maps = list(maps) or [OrderedDict()]

        def __missing__(self, key):
            raise KeyError(key)

        def __getitem__(self, key):
            for mapping in self.maps:
                try:
                    # can't use 'key in mapping' with defaultdict
                    return mapping[key]
                except KeyError:
                    pass
            # support subclasses that define __missing__
            return self.__missing__(key)

        def get(self, key, default=None):
            return self[key] if key in self else default

        def __len__(self):
            # reuses stored hash values if possible
            return len(set().union(*self.maps))

        def __iter__(self, set=set):
            return set().union(*self.maps).__iter__()

        def __contains__(self, key, any=any):
            return any(key in m for m in self.maps)

        def __bool__(self, any=any):
            return any(self.maps)

        @recursive_repr()
        def __repr__(self):
            return '{0.__class__.__name__}({1})'.format(
                self, ', '.join(imap(repr, self.maps))
            )

        @classmethod
        def fromkeys(cls, iterable, *args):
            '''
            Create a ChainMap with a single dict created from the iterable.
            '''
            return cls(dict.fromkeys(iterable, *args))

        def copy(self):
            '''
            New ChainMap or subclass with a new copy of maps[0] and refs to
            maps[1:]
            '''
            return getcls(self)(first(self.maps).copy(), *self.maps[1:])

        __copy__ = copy

        def new_child(self):
            '''New ChainMap with a new dict followed by all previous maps.'''
            # like Django's Context.push()
            return getcls(self)({}, *self.maps)

        @property
        def parents(self):
            '''New ChainMap from maps[1:].'''
            # like Django's Context.pop()
            return getcls(self)(*self.maps[1:])

        def __setitem__(self, key, value):
            first(self.maps)[key] = value

        def __delitem__(self, key):
            try:
                del first(self.maps)[key]
            except KeyError:
                raise KeyError(
                    'Key not found in the first mapping: {!r}'.format(key)
                )

        def popitem(self):
            '''
            Remove and return an item pair from maps[0]. Raise `KeyError` is
            maps[0] is empty.
            '''
            try:
                return first(self.maps).popitem()
            except KeyError:
                raise KeyError('No keys found in the first mapping.')

        def pop(self, key, *args):
            '''
            Remove *key* from maps[0] and return its value. Raise KeyError if
            *key* not in maps[0].
            '''
            try:
                return first(self.maps).pop(key, *args)
            except KeyError:
                raise KeyError(
                    'Key not found in the first mapping: {!r}'.format(key)
                )

        def clear(self):
            '''Clear maps[0], leaving maps[1:] intact.'''
            first(self.maps).clear()
