#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
configuration
"""

from __future__ import absolute_import

__author__ = "caelum - http://caelum.com.br"
__modified_by__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.
import re

_SCHEME_RE = re.compile(r'(http.?://)?(?P<url>/.*)')
_PORT_RE   = re.compile(r'(?P<host>[^:/ ]+)(:[0-9]*)?(?P<url>/.*)')

__all__ = ['Configuration']

# Project requirements
from tornado.httputil import HTTPHeaders

# local submodule requirements
from .processor import tornado_chain
from .request import Request


class Configuration(object):
    """Configuration object for requests at a given URI"""

    HTTP_VERBS = [
        'delete',
        'get',
        'head',
        'options',
        'patch',
        'post',
        'put',
        'trace'
        ]

    FLAVORS = {
        'json': {
            'content-type': 'application/json',
            'accept':       'application/json',
        },
        'xml': {
            'content-type': 'application/xml',
            'accept':       'application/xml',
        },
        'plain': {
            'content-type': 'text/plain',
            'accept':       'text/plain',
        },

        # POST and PUT only flavors
        'form': {
            'content-type': 'application/x-www-form-urlencoded',
        },
        'multipart': {
            'content-type': 'multipart/form-data; boundary=AaB03x',
        },
    }

    # Default tornado timeout
    TIMEOUT = 20
    
    def __init__(self, uri, flavors=None, chain=None, compress=False):
        """Initialize the configuration for requests at the given URI"""
        self.uri             = uri
        self.headers         = HTTPHeaders()
        self.flavors         = flavors or ['json', 'xml']
        self.processors      = chain or tornado_chain
        self.credentials     = {}
        self.verb            = None
        self.use_gzip        = compress

        # Request extra arguments
        self.progress_callback = None
        self.request_timeout   = self.TIMEOUT
        self.connect_timeout   = self.TIMEOUT
        
    def __getattr__(self, value):
        """
        Perform an HTTP request. This method supports calls to the following
        methods: delete, get, head, options, patch, post, put, trace

        Once the HTTP call is performed, a response is returned (unless the
        async method is used).
        """
        if (value not in self.HTTP_VERBS):
            raise AttributeError(value)

        # store current verb to be passed to Request
        self.verb = value.upper()

        # set accept if it wasn't set previously
        if 'accept' not in self.headers:
            for flavor in self.flavors:
                if 'accept' in self.FLAVORS[flavor]:
                    self.headers.add('accept', self.FLAVORS[flavor]['accept'])

        # set form type and default if noone is present
        if 'content-type' not in self.headers and self.verb in ('POST', 'PUT', 'PATCH'):
            self.headers['content-type'] = self.FLAVORS['form']['content-type']
            
        return Request(self)

    def use(self, feature):
        """Register a feature (processor) at this configuration"""
        self.processors.insert(0, feature)
        return self

    def secure(self, value=None, port=None):
        """Force connection using https protocol at port specified"""
        if isinstance(value, bool):
            scheme    = 'http' if not value else 'https'
            self.uri  = _SCHEME_RE.sub(scheme + "://\g<url>", self.uri)
        if isinstance(port, int):
            self.uri = _PORT_RE.sub("\g<host>:" + port + "\g<url>", self.uri)
        return self
        
    def compress(self):
        """Notify server that we will be zipping request"""
        self.use_gzip = True
        return self

    def progress(self, progress_callback):
        """
        Allow to define a progress callback about operaiton. This
        progress callback takes 2 arguments, total length, if any and
        amount of bytes already transfered
        """
        self.progress_callback = progress_callback
        return self
        
    def until(self, request_timeout=None, connect_timeout=None):
        """Set current timeout in seconds for every call"""
        self.connect_timeout = connect_timeout or self.connect_timeout
        self.request_timeout = request_timeout or self.request_timeout
        return self

    def as_(self, flavor):
        """Set up the Content-Type"""
        if flavor is not None:
            # Just use default flavors in case we pass a None param
            if flavor in self.FLAVORS:
                self.headers.update(self.FLAVORS[flavor])
            else:
                self.headers["accept"] = flavor
                self.headers["content-type"] = flavor
        return self

    def accepts(self, flavor):
        """Configure the accepted response format"""
        if flavor is not None:
            if flavor in self.FLAVORS:
                flavor = self.FLAVORS[flavor]['accept']
            self.headers.add('accept', flavor)
        return self

    def auth(self, credentials, path="*", method='plain'):
        """Authentication feature. It does simple HTTP auth"""
        # already defined ?
        if path in self.credentials or method is None:
            return self
        # process a regex valid for path
        expr = "%s.*" if path.endswith('*') else "%s$"
        rmatch = re.compile(expr % path.rsplit('*', 1)[0])
        # now store it
        self.credentials[path]=(rmatch, method, credentials,)
        return self
