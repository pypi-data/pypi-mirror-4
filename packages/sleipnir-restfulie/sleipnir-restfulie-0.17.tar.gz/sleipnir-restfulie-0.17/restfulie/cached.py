import re
import itertools

class Cached(object):
    
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
        # non cached stuff
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
        # cache stuff
        if self.__infunc__(self._wrapper_, key):
            self._cache_[key] = value
            callable(self._notify_) and self._notify_(self)
            return
        raise AttributeError(key)

    def __create_cached(self, cls, key, wrapper):
        return cls(wrapper, lambda x: self._cache_.__setitem__(key, x))

    @staticmethod
    def _get_type(instance):
        if isinstance(instance, dict):
            return dict
        return type(instance)

class CachedDict(Cached):

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
        
            
class CachedList(Cached):

    __slots__   = ()
    __list__    = True

    __RE        = re.compile(' |@')
    
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
            self._cache_[key] = value
            callable(self._notify_) and self._notify_(self)
        return cls(wrapper, notify)

# Init this when class has been defined properly
Cached.__factory__ = {
    dict: CachedDict,
    list: CachedList,
}
