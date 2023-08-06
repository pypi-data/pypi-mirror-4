# -*- mode:python; coding: utf-8 -*-

"""
Memoize utilities
"""

from __future__ import absolute_import

__author__ = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# required modules
import re
import itertools
import functools

__all__ = ['Cached']

# Import here local requirements


# pylint:disable-msg=C0103
class cached(object):
    """
    Decorator that caches a function's return value each time it is
    called. If called later with the same arguments, the cached value
    is returned, and not re-evaluated.
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args, **kwargs):
        try:
            args = hash(args) + hash(kwargs)
            return self.cache[args]
        except KeyError:
            value = self.func(*args)
            self.cache[args] = value
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)


# pylint: disable-msg=R0924, R0903
class Cached(object):
    """Lazy Memoizer class"""

    __infunc__  = lambda self, x, y: hasattr(x, y)
    __getfunc__ = lambda self, x, y: getattr(x, y)
    __factory__ = {}
    __slots__   = ("_wrapper_", "_cache_", "_notify_")

    def __init__(self, wrapper, notify=None):
        self._wrapper_ = wrapper
        self._cache_   = {}
        self._notify_  = notify
        if self._wrapper_ == 0:
            raise AttributeError(wrapper)

    def __contains__(self, key):
        return key in self._wrapper_

    def __iter__(self):
        for key, value in self._wrapper_.iteritems():
            yield (key, self._cache_.get(key, value),)

    def __repr__(self):
        dct = dict(iter(self))
        dct.update(self._cache_)
        return repr(dct)

    def __getitem__(self, key):
        return self._cache_.get(key, self._wrapper_[key])

    def __getattr__(self, key):
        # already cached stuff
        if key in self._cache_:
            return self._cache_[key]
        # non cached stuff; pylint: disable-msg=E1120
        if self.__infunc__(self._wrapper_, key):
            wrapper = self.__getfunc__(self._wrapper_, key)
            wrptype = self._get_type(wrapper)
            if wrptype in self.__factory__:
                cached_cls = self.__factory__[wrptype]
                return self.__create_cached(cached_cls, key, wrapper)
            return wrapper
        # Error
        raise AttributeError(key)

    def __setattr__(self, key, value):
        # private stuff
        if key[0] == "_" and key[-1] == "_":
            object.__setattr__(self, key, value)
            return
        # cache stuff; pylint: disable-msg=E1120
        if self.__infunc__(self._wrapper_, key):
            self._cache_[key] = value
            # pylint: disable-msg=W0106
            callable(self._notify_) and self._notify_(self)
            return
        raise AttributeError(key)

    def __create_cached(self, cls, key, wrapper):
        """Cache factory"""
        return cls(wrapper, lambda x: self._cache_.__setitem__(key, x))

    @staticmethod
    def _get_type(instance):
        """Utility method"""
        if isinstance(instance, dict):
            return dict
        return type(instance)


# pylint: disable-msg=R0903
class CachedDict(Cached):
    """Specialized cached class to wrap dicts"""

    __infunc__  = lambda self, x, y: y in x
    __getfunc__ = lambda self, x, y: x.get(y)
    __dict__    = True

    def __iter__(self):
        return self._wrapper_.iteritems()

    def __getattr__(self, key):
        try:
            return super(CachedDict, self).__getattr__(key)
        except AttributeError:
            return getattr(self._wrapper_, key)


# pylint: disable-msg=R0903, R0924
class CachedList(Cached):
    """Specialized cached class to wrap dicts"""

    __slots__ = ()
    __list__ = True

    __RE = re.compile(' |@')

    def __init__(self, wrapper, notify):
        super(CachedList, self).__init__(wrapper, notify)
        self._cache_ = [None] * len(wrapper)

    def __repr__(self):
        return repr(list(iter(self)))

    def __len__(self):
        return len(self._cache_)

    def __iter__(self):
        for index, value in enumerate(self._cache_):
            yield self._wrapper_[index] if value is None else value

    def __getattr__(self, key):
        raise AttributeError(key)

    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)

    def __getkey(self, key):
        """Memoizer accessor"""
        guards = self.__RE.sub("", key).split(",")
        guards = list(itertools.imap(lambda x: x.split("="), guards))
        # parse values to strip spurius data
        for item in guards:
            try:
                value = int(item[1])
            except ValueError:
                value = item[1].strip(' \'"')
            finally:
                item[1] = value
        for index, dct in enumerate(self._wrapper_):
            if isinstance(dct, dict):
                dct_items = dct.items()
                if all([tuple(item) in dct_items for item in guards]):
                    return index
        raise AttributeError("Index not found '%s'" % key)

    def __getitem__(self, key):
        # Try to find a json based pointer
        if isinstance(key, basestring):
            key = self.__getkey(key)
        # already cached stuff
        if self._cache_[key] is not None:
            return self._cache_[key]
        # Default behaviour
        assert isinstance(key, int)

        wrapper = self._wrapper_[key]
        wrptype = self._get_type(wrapper)
        if wrptype in self.__factory__:
            cached_cls = self.__factory__[wrptype]
            return self.__create_cached(cached_cls, key, wrapper)
        return wrapper

    def __setitem__(self, key, value):
        self._cache_[key] = value

    def __create_cached(self, cls, key, wrapper):
        def notify(value):
            """observer method"""
            self._cache_[key] = value
            # pylint: disable-msg=W0106
            callable(self._notify_) and self._notify_(self)
        return cls(wrapper, notify)

# Init this when class has been defined properly
Cached.__factory__ = {
    dict: CachedDict,
    list: CachedList,
}
