# -*- mode:python; coding: utf-8 -*-

"""
credentials
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.
from itertools import ifilter,  product

__all__ = ['Credentials']


class Credentials(object):
    """
    Base class to define required credentials to use a remote
    service
    """

    DEFAULTS = {
        "oauth_callback"        : None,
        "oauth_callback_handler": None,
        "consumer_key"          : None,
        "consumer_secret"       : None,
    }

    SECRETS = {
        "token_key"           : None,
        "token_secret"        : None,
        "oauth_session_handle": None,
    }

    __slots__ = ("_mechanisms", "_properties", "_callbacks",)

    def __init__(self):
        self._callbacks  = {}
        self._mechanisms = {}

        # Maintain this definition last one or we will break set/get
        # logic
        self._properties = {}

    def __iter__(self):
        return self._properties.iterkeys()

    def __contains__(self, value):
        return value in self._properties

    def __getattr__(self, name):
        # Common case
        if name not in self._properties:
            # Check if a callback has been set to retrieve required data
            # callback accepts requeested name and returns something
            # acceptable to dict.update
            if name in self._callbacks or None in self._callbacks:
                callback = self._callbacks.get(name) or self._callbacks[None]
                # Callback MAY fail to add name into properties set
                # (For example if callback is set as default one. For
                # that cases, try to return default value
                callback(self._properties, name)

        # Second try. This time, don't use callbacks to retrieve a
        # safe value, if any
        if name not in self._properties:
            # Try to return a default
            if name in self.DEFAULTS:
                return self.DEFAULTS[name]
            if name in self.SECRETS:
                return self.SECRETS[name]
                # Error: Notify
            raise AttributeError(name)

        # return value
        return self._properties[name]

    def __setattr__(self, name, value):
        if not name.startswith("_"):
            # store as callback if value is a callable
            if callable(value) and name != "oauth_callback_handler":
                self._callbacks[name] = value
            else:
                self._properties[name] = value
        else:
            # default op
            object.__setattr__(self, name, value)

    def to_list(self, *args):
        """Get a list of properties already collected in args"""
        return [getattr(self, arg) for arg in args]

    def to_dict(self, *args):
        """Get a dict of properties collected from args"""
        known   = ifilter(lambda x: x in self._properties, args)
        unknown = ifilter(lambda x: x not in self._properties, args)
        # init retval
        retval = dict((k, self._properties[k]) for k in known)
        # convert to list becouse we probably will change
        # self._properties when iterate over loop
        for key in list(unknown):
            # this should invoke callbacks if needed and update
            # self._properties
            retval[key] = getattr(self, key)
        return retval

    def ask_to(self, callback, values):
        """
        Call callback mehtod whes asked for any values. Values
        could be a string or a collection of them
        """
        values = (values) if isinstance(values, basestring) else values
        self._callbacks.update(product(values, (callback,)))

    def store(self, mechanism):
        """A store for auth mechanism data"""
        return self._mechanisms.setdefault(mechanism, {})

    def clean(self, exclude=None):
        """Clean stores. Excludes may be a list of valid keys. In that
        keys, dose keys arent cleaned
        """
        props = self._properties
        # pylint: disable-msg=W0106
        [props.pop(k) for k in tuple(props.iterkeys()) if k not in exclude] \
            if exclude else props.clear()

    def update(self, values, **kwargs):
        """Update credentias with params followin python dict update rules"""
        if hasattr(values, 'keys'):
            # pylint: disable-msg=W0106
            [setattr(self, key, values[key]) for key in values.keys()]
        else:
            # pylint: disable-msg=W0106
            [setattr(self, key, value) for key, value in values]
        # pylint: disable-msg=W0106
        [setattr(self, key, value) for key, value in kwargs.iteritems()]
