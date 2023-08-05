# -*- coding: utf-8 -*-
'''core stuf.'''

from itertools import chain
from operator import methodcaller, attrgetter
from collections import Mapping, MutableMapping, defaultdict, namedtuple

from stuf import exhaustitems
from stuf.iterable import exhaustcall
from stuf.desc import lazy_class, lazy
from stuf.deep import clsname, getcls, clsdict
from stuf.six import getvalues, getitems, getkeys
from stuf.collects import ChainMap, OrderedDict, recursive_repr

__all__ = 'defaultstuf fixedstuf frozenstuf orderedstuf stuf'.split()

wraps = attrgetter('_wrapped')
delitem = attrgetter('_wrapped.__delitem__')
getitem = attrgetter('_wrapped.__getitem__')
setitem = attrgetter('_wrapped.__setitem__')
length = attrgetter('_wrapped.__len__')
_iter = attrgetter('_wrapped.__iter__')
asdict = attrgetter('_wrapped._asdict')
_reserved = 'allowed _wrapped _map'.split()


class corestuf(object):

    _map = dict

    def __getattr__(self, key, _getter=object.__getattribute__):
        if key == 'iteritems':
            return getitems(self)
        elif key == 'iterkeys':
            return getkeys(self)
        elif key == 'itervalues':
            return getvalues(self)
        try:
            return self[key]
        except KeyError:
            return _getter(self, key)

    @recursive_repr()
    def __repr__(self):
        return '{0}({1})'.format(clsname(self), methodcaller('items')(self))

    @lazy_class
    def _classkeys(self):
        # protected keywords
        return frozenset(chain(
            iter(vars(self)), iter(vars(getcls(self))), _reserved,
        ))

    def _build(self, iterable):
        # add class to handle potential nested objects of the same class
        try:
            kw = self._map()
            # extract appropriate key-values from sequence
            exhaustcall(kw.update, iterable)
        except ValueError:
            kw.update(iterable)
        return kw

    def _mapping(self, iterable):
        return self._map(iterable)

    def _new(self, iterable):
        return getcls(self)(self._build(iterable))

    def _prepop(self, *args, **kw):
        kw.update(self._build(args))
        return kw

    def _pop(self, past, future):
        def closure(key, value, new=self._new):
            try:
                if not hasattr(value, 'capitalize'):
                    # see if stuf can be converted to nested stuf
                    trial = new(value)
                    value = trial if trial else value
            except (TypeError, IOError):
                pass
            future[key] = value
        exhaustitems(closure, past)
        return self._postpop(future)

    def _postpop(self, future):
        return future

    def copy(self):
        return self._new(dict(self))


class writestuf(corestuf):

    def __setattr__(self, key, value):
        # handle normal object attributes
        if key == '_classkeys' or key in self._classkeys:
            clsdict(self)[key] = value
        # handle special attributes
        else:
            try:
                self[key] = value
            except KeyError:
                raise AttributeError(key)

    def __delattr__(self, key):
        # allow deletion of key-value pairs only
        if not key == '_classkeys' or key in self._classkeys:
            try:
                del self[key]
            except KeyError:
                raise AttributeError(key)

    def update(self, *args, **kw):
        self._pop(self._prepop(*args, **kw), self)


class wrapstuf(corestuf):

    def __init__(self, *args, **kw):
        super(wrapstuf, self).__init__()
        self._wrapped = self._pop(self._prepop(*args, **kw), self._map())

    def _postpop(self, future):
        return self._mapping(future)


class writewrapstuf(wrapstuf, writestuf, MutableMapping):

    @lazy
    def __getitem__(self):
        return getitem(self)

    @lazy
    def __setitem__(self):
        return setitem(self)

    @lazy
    def __delitem__(self):
        return delitem(self)

    @lazy
    def __iter__(self):
        return _iter(self)

    @lazy
    def __len__(self):
        return length(self)

    def __reduce__(self):
        return (getcls(self), (wraps(self).copy(),))


class chainstuf(writestuf, ChainMap):

    '''stuf chained together.'''

    def __init__(self, *args):
        super(chainstuf, self).__init__(*args)
        maps = self.maps
        for idx, item in enumerate(maps):
            maps[idx] = stuf(item)

    def __reduce__(self):
        return (getcls(self), tuple(self.maps))

    @lazy_class
    def _classkeys(self):
        # protected keywords
        return frozenset(chain(
            super(chainstuf, self)._classkeys, ['maps'],
        ))

    copy = ChainMap.copy
    update = ChainMap.update


class defaultstuf(writestuf, defaultdict):

    '''
    Dictionary with attribute-style access and a factory function to provide a
    default value for keys with no value.
    '''

    __slots__ = []

    _map = defaultdict

    def __init__(self, default, *args, **kw):
        '''
        :argument default: function that can provide default values
        :param *args: iterable of keys/value pairs
        :param **kw: keyword arguments
        '''
        defaultdict.__init__(self, default)
        writestuf.update(self, *args, **kw)

    def _build(self, iterable):
        # add class to handle potential nested objects of the same class
        try:
            kind = self._map
            kw = kind(self.default_factory)
            # extract appropriate key-values from sequence
            exhaustcall(kw.update, iterable)
        except (ValueError, TypeError):
            kw.update(kind(self.default_factory, iterable))
        return kw

    def _new(self, iterable):
        return getcls(self)(self.default_factory, self._build(iterable))


class fixedstuf(writewrapstuf):

    '''
    Dictionary with attribute-style access where mutability is restricted to
    initial keys.
    '''

    def __setitem__(self, key, value):
        # only access initial keys
        if key in self.allowed:
            super(fixedstuf, self).__setitem__(key, value)
        else:
            raise KeyError('key "{0}" not allowed'.format(key))

    def _prepop(self, *args, **kw):
        iterable = super(fixedstuf, self)._prepop(*args, **kw)
        self.allowed = frozenset(iterable)
        return iterable

    def clear(self):
        wraps(self).clear()

    def popitem(self):
        raise AttributeError()

    def pop(self, key, default=None):
        raise AttributeError()


class frozenstuf(wrapstuf, Mapping):

    '''Immutable dictionary with attribute-style access.'''

    __slots__ = ['_wrapped']

    def __getitem__(self, key):
        try:
            return getattr(wraps(self), key)
        except AttributeError:
            raise KeyError('key {0} not found'.format(key))

    def __iter__(self):
        return iter(asdict(self)())

    def __len__(self):
        return len(asdict(self)())

    def __reduce__(self):
        return (getcls(self), (asdict(self)().copy(),))

    @classmethod
    def _mapping(self, mapping):
        return namedtuple('frozenstuf', iter(mapping))(**mapping)


class orderedstuf(writewrapstuf):

    '''Dictionary with dot attributes that remembers insertion order.'''

    _mapping = OrderedDict

    @lazy
    def __reversed__(self):
        return wraps(self).__reversed__


class stuf(writestuf, dict):

    '''Dictionary with attribute-style access.'''

    __slots__ = []
    __init__ = writestuf.update
