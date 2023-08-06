# -*- mode:python; coding: utf-8 -*-

"""
Response
"""

from __future__ import absolute_import

__author__ = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.
from collections import namedtuple

__all__ = ['Response']

# Project requirements
from .converters import Converters
from .patchers import Patchers
from .links import Links
from .cached import Cached


# Simple error to wrap exceptions to what we may find on an seever
# error response; pylint: disable-msg=C0103
_Error = namedtuple('ResponseError', ['status_code', 'value', 'details'])


class Response(object):
    """Handle and parse a HTTP response"""

    __slots__ = ("_exception", "_response", "_resource", "_cached")


    def __init__(self, response):
        # Init values
        self._resource  = None
        self._cached    = None
        try:
            # Common Case, an HTTPResponse
            self._response  = response
            self._exception = response.error
        except AttributeError:
            if isinstance(response, Exception):
                # Try to handle HTTPErrors
                self._exception = response
                self._response  = response.response

    def __getattr__(self, key):
        # delegate getattr
        return getattr(self.__cached(), key)

    def __setattr__(self, key, value):
        # private stuff
        if key in self.__slots__:
            object.__setattr__(self, key, value)
            return
        # already cached stuff
        setattr(self.__cached(), key, value)

    def __iter__(self):
        return iter(self.__cached())

    def __cached(self):
        """
        Get a wrapable arount resource to make easy to fetch keys
        as attributes
        """
        # already cached stuff
        if self._cached is None:
            self._cached = Cached(self.resource)
        return self._cached

    @property
    def headers(self):
        """Returns HTTP headers"""
        return self._response and self._response.headers or {}

    @property
    def code(self):
        """Returns response code"""
        return self._response and self._response.code or self._exception.code

    @property
    def body(self):
        """Returns a formatted body"""
        return self._response and self._response.body or ""

    @property
    def resource(self):
        """Unmarshalled object of the response body"""
        # Response may be an empty string if comes from an tornado
        # client exception
        if self._resource is None:
            # sanity values
            resbuffer = ""
            marshalto = 'text/plain'
            # parse response, if any
            if self._response is not None:
                resbuffer = self._response.buffer
                marshalto = self._response.headers.get_list('content-type')
                marshalto = marshalto[0] if marshalto else 'text/plain'
            # get a valid resource
            converter = Converters.for_type(marshalto.split(';')[0])
            self._resource = converter.unmarshal(resbuffer)
            assert self._resource is not None
        return self._resource

    @property
    def error(self):
        """Get exception if any from server"""
        retval = self.resource.error()
        if not retval and self._exception:
            retval = _Error(
                self._exception.code,
                str(self._exception),
                None)
        return retval

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

    def rethrow(self):
        """Try to raise again if response was an error"""
        if self._exception:
            raise self._exception
