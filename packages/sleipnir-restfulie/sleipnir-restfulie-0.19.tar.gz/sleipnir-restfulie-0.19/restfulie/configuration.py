# -*- mode:python; coding: utf-8 -*-

"""
Configuration
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.
import re
import sys
import itertools

_PROT_RE = re.compile(r'(?P<proto>http.?://)?'
                      '(?P<url>.*)')
_PORT_RE = re.compile(r'(?P<proto>http.?://)?'
                      '(?P<host>[^:/ ]+)(:[0-9]*)?(?P<url>.*)')


__all__ = ['Configuration']

# Project requirements
from tornado.httputil import HTTPHeaders

# local submodule requirements
from .processor import tornado_chain
from .request import Request


# pylint: disable-msg=R0902, R0913
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

    def __init__(self, uri, flavors=None, chain=None, compress=False,
                 ca_certs=None, connect_timeout=None, request_timeout=None):
        """Initialize the configuration for requests at the given URI"""
        self.uri         = uri
        self.headers     = HTTPHeaders()
        self.flavors     = flavors or ['json', 'xml']
        self.processors  = chain or tornado_chain
        self.credentials = {}
        self.verb        = None
        self.use_gzip    = compress
        self.ca_certs    = ca_certs

        # Request extra arguments
        self.progress_callback = None
        self.connect_timeout   = connect_timeout or self.TIMEOUT
        self.request_timeout   = request_timeout or self.TIMEOUT

    def __iter__(self):
        """Iterate over properties"""
        prop_filter = lambda x: x[0][0] != '_'
        return itertools.ifilter(prop_filter, self.__dict__.iteritems())

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
        verb_allowed = self.verb in ('POST', 'PUT', 'PATCH')
        if verb_allowed and 'content-type' not in self.headers:
            self.headers['content-type'] = self.FLAVORS['form']['content-type']

        # Debug helper
        if __debug__:
            sys.stderr.write("=" * 70)
            sys.stderr.write("\nRequest:{0} {1}".format(self.verb, self.uri))

            sys.stderr.write("\nHeaders:")
            sys.stderr.write("\n  Accept:'{0}'".format(self.headers['accept']))
            if 'content-type' in self.headers:
                ctype = self.headers['content-type']
                sys.stderr.write("\n  Content-Type:'{0}'".format(ctype))
                sys.stderr.write("\n  Compressed:'{0}'".format(self.use_gzip))
            if self.uri.startswith("https"):
                sys.stderr.write("\nCerts:'{0}'".format(self.ca_certs))
            sys.stderr.write("\n{0}\n".format("=" * 70))

        return Request(self)

    def use(self, feature):
        """Register a feature (processor) at this configuration"""
        self.processors.insert(0, feature)
        return self

    def secure(self, value=None, port=None, ca_certs=None):
        """Force connection using https protocol at port specified"""
        if isinstance(value, bool):
            scheme = 'http' if not value else 'https'
            self.uri = _PROT_RE.sub(scheme + r"://\g<url>", self.uri)
        if isinstance(port, int):
            regx_str = r"\g<proto>\g<host>:{0}\g<url>".format(port)
            self.uri = _PORT_RE.sub(regx_str, self.uri)
        if isinstance(ca_certs, basestring):
            self.ca_certs = ca_certs
        return self

    def compress(self, compress=True):
        """Notify server that we will be zipping request"""
        self.use_gzip = bool(compress)
        return self

    def progress(self, progress_callback):
        """
        Allow to define a progress callback about operaiton. This
        progress callback takes 2 arguments, total length, if any and
        amount of bytes already transfered
        """
        self.progress_callback = progress_callback
        return self

    def until(self, connect_timeout=None, request_timeout=None):
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
        self.credentials[path] = (rmatch, method, credentials,)
        return self
