#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
request
"""

from __future__ import absolute_import

__author__ = "caelum - http://caelum.com.br"
__modified_by__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.

__all__ = ['Response']

# Project requirements
from .converters import Converters
from .patchers import Patchers
from .links import Links
from .cached import Cached

class Response(object):
    """Handle and parse a HTTP response"""

    __slots__ = ("_response", "_resource", "_cached")
    
    def __init__(self, response):
        self._response = response
        self._resource = None
        self._cached   = None
        
    def __getattr__(self, key):
        # already cached stuff
        if self._cached is None:
            self._cached = Cached(self.resource)
        # delegate getattr
        return getattr(self._cached, key)

    def __setattr__(self, key, value):
        # private stuff
        if key in self.__slots__:
            object.__setattr__(self, key, value)
            return
        # already cached stuff
        if self._cached is None:
            self._cached = Cached(self.resource)
        setattr(self._cached, key, value)
            
    def __iter__(self):
        return iter(self.resource)

    @property
    def headers(self):
        """Returns HTTP headers"""
        return self._response.headers

    @property
    def code(self):
        """Returns response code"""
        return self._response.code

    @property
    def body(self):
        """Returns a formatted body"""
        return self._response.body

    @property
    def resource(self):
        """Unmarshalled object of the response body"""
        if self._resource is None:
            marshalto = self._response.headers.get_list('content-type')
            marshalto = marshalto[0] if marshalto else 'text/plain'
            converter = Converters.marshaller_for(marshalto.split(';')[0])
            self._resource = converter.unmarshal(self._response.buffer)
        return self._resource

    @property
    def error(self):
        """Get exception if any from server"""
        return self.resource.error()

    #pylint: disable-msg=W0201
    @property
    def links(self):
        """Returns the Links of the header"""
        if not hasattr(self, '_links'):
            self._links = self.resource.links()
            values = self._response.headers.get('link')
            self._links.update([link for link in Links.parse(values)])
        return self._links

    def link(self, rel, default=None):
        """Get a link with 'rel' from header"""
        return self.links.rel(rel, default)

    def diff(self):
        """Create a valid document for response type"""
        patcher_type = self._response.headers.get_list('content-type')[0]
        patcher = Patchers.for_type(patcher_type.split(';')[0])
        return patcher.make(self._resource, self._cached)

        