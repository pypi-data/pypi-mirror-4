# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
processors
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.
from copy import copy
from urlparse import urlparse

__all__ = [
    'AuthenticationProcessor',
    'ExecuteRequestProcessor',
    'PayloadMarshallingProcessor',
    'RedirectProcessor',
]

# Project requirements
from tornado.httputil import url_concat
from tornado.httpclient import HTTPClient, AsyncHTTPClient, HTTPError

# local submodule requirements
from .converters import Converters
from .response import Response
from .request import Request


#pylint: disable-msg=R0903
class RequestProcessor(object):
    """Base class for all processors"""

    def execute(self, callback, chain, request, env):
        """Command called to be runned"""
        raise NotImplementedError('Subclasses must implement this method')


#pylint: disable-msg=R0903, R0922
class AuthenticationProcessor(RequestProcessor):
    """Abstract class for authentication methods"""

    backends = {}

    def execute(self, callback, chain, request, env):
        if len(request.credentials):
            #pylint: disable-msg=E1101
            path = urlparse(request.uri).path or "/"
            for math, method, credentials in request.credentials.itervalues():
                if not math.match(path):
                    continue
                if method not in self.backends:
                    error = "Unsupported auth mechanism '%s'" % method
                    raise NotImplementedError(error)
                # Call Auth mechanism should be used
                return method, credentials
        return None, None


#pylint: disable-msg=R0903, R0922
class AuthenticationSyncProcessor(AuthenticationProcessor):
    """Abstract class for authentication methods. Used to sign"""

    def execute(self, callback, chain, request, env):
        method = AuthenticationProcessor.execute
        method, cred = method(self, callback, chain, request, env)

        # Becouse authorize_sync calls are 'embbedded' on flow, we
        # need a way to notify to callback that an error happened. To
        # do that, we follow comvention to embbed error on a Response
        # instance and pass it to callback. pylint: disable-msg=W0106
        try:
            method and self.backends[method].authorize_sync(cred, request, env)
        except HTTPError, err:
            callback(Response(err))
            return
        # follow if no method used
        return chain.follow(callback, request, env)


class AuthenticationAsyncProcessor(AuthenticationProcessor):
    """Abstract class for authentication methods. Async"""

    def execute(self, callback, chain, request, env):
        assert not chain or len(chain) == 0
        method = AuthenticationProcessor.execute
        method, cred = method(self, callback, chain, request, env)
        self.backends[method].authorize(cred, request, env, callback)


class MetaAuth(type):
    """Auth Metaclass"""

    def __init__(cls, name, bases, dct):
        type.__init__(cls, name, bases, dct)
        if name.endswith("Auth"):
            implements = cls.implements
            AuthenticationProcessor.backends[implements] = cls()


#pylint: disable-msg=R0921
class AuthMixin(object):
    """Base class to derive authentication mechanisms"""

    __metaclass__ = MetaAuth

    def authorize(self, credentials, request, env, callback):
        """Set authorization content for this request"""
        raise NotImplementedError('Subclasses must implement this method')

    def authorize_sync(self, credentials, request, env):
        """Set authorization content for this request sincronously"""
        raise NotImplementedError('Subclasses must implement this method')


class ExecuteRequestProcessor(RequestProcessor):
    """
    Processor responsible for getting the body from environment and
    making a request with it.
    """

    @staticmethod
    def _sync(request, env):
        """Run blocked"""
        try:
            response = HTTPClient().fetch(
                url_concat(request.uri, env["params"]),
                method=request.verb,
                headers=request.headers,
                body=env.get("body"),
                use_gzip=request.use_gzip,
                ca_certs=request.ca_certs,
                progress_callback=request.progress_callback,
                connect_timeout=request.connect_timeout,
                request_timeout=request.request_timeout)
        except Exception, err:
            if not isinstance(err, HTTPError):
                err = HTTPError(599, repr(err))
            raise err
        # All ok. return retval
        return Response(response)

    @staticmethod
    def _async(callback, request, env):
        """Run async"""
        def on_response(response):
            """Response callback handler"""

            if hasattr(response, 'error') and response.error:
                # We may had non HTTPErrors generated by tornado. (For
                # example, when a host can't be resolved. For that
                # cases, we create a wrapper arount response exception
                # and throw that new Exception
                if not isinstance(response.error, HTTPError):
                    errcode = response.code
                    message = repr(response.error)
                    response.error = HTTPError(errcode, message, response)
            # No error case
            return callback(Response(response))

        resource = AsyncHTTPClient()
        response = resource.fetch(
            url_concat(request.uri, env["params"]),
            callback=on_response,
            method=request.verb,
            headers=request.headers,
            body=env.get("body"),
            use_gzip=request.use_gzip,
            ca_certs=request.ca_certs,
            progress_callback=request.progress_callback,
            connect_timeout=request.connect_timeout,
            request_timeout=request.request_timeout)

        # A cancellable 'future' ;)
        return response

    def execute(self, callback, chain, request, env):
        return self._sync(request, env) \
            if not callable(callback)   \
            else self._async(callback, request, env)


class PayloadMarshallingProcessor(RequestProcessor):
    """Responsible for marshalling the payload in environment"""

    def execute(self, callback, chain, request, env):
        if env["payload"]:
            content_type = request.headers.get("content-type")
            marshaller   = Converters.for_type(content_type)
            env["body"]  = marshaller.marshal(env["payload"])
            del(env["payload"])
        return chain.follow(callback, request, env)


class RedirectProcessor(RequestProcessor):
    """
    A processor responsible for redirecting a client to another URI
    when the server returns the location header and a response code
    related to redirecting.
    """
    REDIRECT_CODES = ['201', '301', '302']

    def _redirect(self, result):
        """Get redirection url, if any"""
        return result.headers.get("location") \
            if (result.code in self.REDIRECT_CODES) else None

    def execute(self, callback, chain, request, env):
        def _on_resource(resource):
            """resource callback"""
            assert callable(callback)
            # copy configuration and update url
            url = self._redirect(resource)
            if not url:
                return callback(resource)
            # make a new request
            config = copy(request.config)
            config.uri = url
            return Request(self)(callback)
        # chain
        return chain.follow(_on_resource, request, env)    \
            if callable(callback) else chain.follow(callback, request, env)


# Main tornado chain (Use follow_redirects so RedirectProcessor is not
# required anymore

#pylint:disable-msg=C0103
tornado_chain = [
    PayloadMarshallingProcessor(),
    AuthenticationSyncProcessor(),
#   RedirectProcessor(),
    ExecuteRequestProcessor(),
]

auth_chain = [
    PayloadMarshallingProcessor(),
    AuthenticationAsyncProcessor(),
]
