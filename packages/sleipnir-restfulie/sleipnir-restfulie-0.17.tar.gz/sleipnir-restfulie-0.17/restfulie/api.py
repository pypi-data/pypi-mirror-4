#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
BaseAPI
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.
from itertools import ifilter

__all__ = ['BaseAPI', 'BaseMapper']

# Project requirements
from .restfulie import Restfulie

# Create:
#-------.
# PUT:  if you are sending the full content of the specified resource (URL).
# POST: if you are sending a command to the server to create a
#       subordinate of the specified resource, using some server-side
#       algorithm.

# Retrieve
# --------
# GET

# Update
# -------
# PUT:   if you are updating the full content of the specified resource.
# PATCH: if you are requesting the server to update one or
#        more subordinates of the specified resource.

# Delete
# ------
# DELETE.

#pylint: disable-msg=R0903
class BaseAPI(object):
    """
    Derive from here Custom API Implementations. All implementations
    MUST be stateless
    """

    API_BASE = None
    FLAVORS  = None
    CHAIN    = None
    COMPRESS = False

    # Timeouts
    CONNECT_TIMEOUT = None
    REQUEST_TIMEOUT = None
    
    
    #pylint: disable-msg=C0301, R0913, W0142
    @classmethod
    def _get(cls, client, auth, endpoint, flavor, compress, secure, args, callback):
        """Implementation of verb GET"""
        return Restfulie.at(endpoint, cls.FLAVORS, cls.CHAIN, compress) \
            .secure(*secure)                                            \
            .auth(client.credentials, method=auth)                      \
            .accepts(flavor)                                            \
            .until(cls.REQUEST_TIMEOUT, cls.CONNECT_TIMEOUT)            \
            .get(callback=callback, params=args)

    #pylint: disable-msg=C0301, R0913, W0142        
    @classmethod
    def _post(cls, client, auth, endpoint, flavor, compress, secure, args, callback):
        """Implementation of verb POST"""

        #default to form-urlencode. If somthing that smells like a
        #file (has read function) is pased in args, encode it as
        #multipart form

        return Restfulie.at(endpoint, cls.FLAVORS, cls.CHAIN, compress) \
            .secure(*secure)                                            \
            .as_(flavor)                                                \
            .auth(client.credentials, method=auth)                      \
            .until(cls.REQUEST_TIMEOUT, cls.CONNECT_TIMEOUT)            \
            .post(args, callback=callback)
        
    #pylint: disable-msg=C0301, R0913, W0142
    @classmethod
    def _put(cls, client, auth, endpoint, flavor, compress, secure, args, callback):
        """Implementation of verb PUT"""

        #default to form-urlencode. If somthing that smells like a
        #file (has read function) is pased in args, encode it as
        #multipart form

        return Restfulie.at(endpoint, cls.FLAVORS, cls.CHAIN, compress) \
            .secure(*secure)                                            \
            .as_(flavor)                                                \
            .auth(client.credentials, method=auth)                      \
            .until(cls.REQUEST_TIMEOUT, cls.CONNECT_TIMEOUT)            \
            .put(args, callback=callback)
        
    #pylint: disable-msg=C0301, R0913, W0142
    @classmethod
    def _patch(cls, client, auth, endpoint, flavor, compress, secure, args, callback):
        """Implementation of verb PATCH"""

        # JSON path expexts an array of objects. Internally, We need
        # to pass Request object will asumme that we are providing an
        # array if args is defined as a length 1 dict with None as key
        # See also:
        # https://datatracker.ietf.org/doc/draft-ietf-appsawg-json-patch/
            
        return Restfulie.at(endpoint, cls.FLAVORS, cls.CHAIN, compress) \
            .secure(*secure)                                            \
            .as_(flavor)                                                \
            .auth(client.credentials, method=auth)                      \
            .until(cls.REQUEST_TIMEOUT, cls.CONNECT_TIMEOUT)            \
            .patch(args, callback=callback)

    #pylint: disable-msg=C0301, R0913, W0142
    @classmethod
    def _delete(cls, client, auth, endpoint, flavor, compress, secure, args, callback):
        """Implementation of verb DELETE"""
        return Restfulie.at(endpoint, cls.FLAVORS, cls.CHAIN, compress) \
            .secure(*secure)                                            \
            .auth(client.credentials, method=auth)                      \
            .accepts(flavor)                                            \
            .until(cls.REQUEST_TIMEOUT, cls.CONNECT_TIMEOUT)            \
            .get(callback=callback, params=args)

    #pylint: disable-msg=C0301, R0913, W0142        
    @classmethod
    def invoke(cls, client, call, body, args, callback=None):
        """Invoke method"""

        # check that requirements are passed
        path = call["endpoint"]
        
        # parse requirements
        for req in ifilter(lambda x: x not in args, call.get("required", ())):
            raise AttributeError("Missing arg '%s' for '%s'" % (req, path))

        # check if body content is required
        if call.get("body", False) and body is None:
            raise AttributeError("Missing body content")
            
        # build endpoint
        uri      = path % args
        auth     = call.get("auth")
        verb     = getattr(cls, "_" + call["method"])
        endpoint = uri if uri.startswith('http') else cls.API_BASE + uri

        # remove used args
        func = lambda x: '%%(%s)' % x[0] not in path
        args = dict(ifilter(func, args.iteritems()))
                
        # we allow only, body or args, bbut not both
        if args and body:
            raise AttributeError("Unused keys found %s", repr(args))
            
        # check if we should override uri security
        secure = call.get("secure", [])
        if not type(secure) in (list, tuple,):
            secure = [secure]

        # invoke
        return verb(client,
                    auth, endpoint,
                    call.get("flavor"), call.get("compress", cls.COMPRESS),
                    secure, body or args, callback)

        
class BaseMapper(object):
    """Sugar class to allow a more pythonic way to invoke REST Api"""

    BASE_API = None
    
    def __init__(self, client, api, ignore=None):
        self.__client = client
        self.__api    = api
        self.__ignore = ignore or []
        
    def __iter__(self):
        self.__api.iterkeys()

    def __setattr__(self, key, value):
        if key[0] != '_':
            raise AttributeError(key)
        return object.__setattr__(self, key, value)
            
    def __getattr__(self, action):
        
        def invoke(*args, **kwargs):
            """Invoke api"""
            args     = list(args)
            params   = kwargs
            callback = params.pop("callback", None)
            # If callback isn't passed as keyword argument, try to
            # fetch from args
            if not callback and args and callable(args[-1]):
                callback = args.pop(-1)
            for req in self.__api[action].get("required", ()):
                if args and req not in params:
                    params.setdefault(req, args.pop(0))

            assert len(args) <= 1
            body = args[0] if args else None

            return self.BASE_API.invoke(
                self.__client, self.__api[action], body, params, callback)
            
        # validate
        if action not in self.__api:
            raise AttributeError("Missing action '%s'" % action)
        if action in self.__ignore:
            raise AttributeError("Invalid API call '%s'" % action)
        return invoke
            
                    

