#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
processors
"""

from __future__ import absolute_import

__author__ = "caelum - http://caelum.com.br"
__modified_by__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.
from base64 import b64encode
from urllib import splittype, splithost, urlencode

from tornado.gen import Task, engine
from tornado.httputil import url_concat
from tornado.httpclient import AsyncHTTPClient, HTTPClient, HTTPError

__all__ = []

# Project requirements
from oauth2 import Request, Consumer, Token, SignatureMethod_HMAC_SHA1, HTTP_METHOD

try:
    from urlparse import parse_qs
except ImportError:
    # fall back for Python 2.5
    from cgi import parse_qs


# local submodule requirements
from .processor import AuthMixin

class AuthError(Exception):
    """Auth exception"""

class HandShakeError(Exception):
    """Error on auth process"""

#pylint: disable-msg=R0903
class BasicAuth(AuthMixin):
    """Processor responsible for making HTTP simple auth"""

    implements = "plain"

    def authorize(self, credentials, request, env, callback):
        self.authorize_sync(credentials, request, env)
        callable(callback) and callback()

    def authorize_sync(self, credentials, request, env):
        creden = credentials.to_list("consumer_key", "consumer_secret")
        encode = b64encode("%s:%s" % creden)
        request.headers['authorization'] = 'Basic %s' % encode


class OAuthMixin(AuthMixin):
    """ oauth method """

    implements = "oauth"
    
    @property
    def request_url(self):
        """Get request_token url according to OAuth 1.0 specs"""
        raise NotImplementedError

    @property
    def access_url(self):
        """Get access_token url according to OAuth 1.0 specs"""
        raise NotImplementedError

    @property
    def authorize_url(self):
        """Get authorize url according to OAuth 1.0 specs"""
        raise NotImplementedError

    @property
    #pylint: disable-msg=W0201
    def method(self):
        """Get method used to sign oauth requests"""
        if not hasattr(self, "_method"):
            self._method = SignatureMethod_HMAC_SHA1()
        return self._method

    ##
    # Fetch methods (HTTP/HTTPS)
    #
    def _fetch(self, consumer, token, uri, callback, **kwargs):
        """Send request async"""
        def on_response(response):
            if hasattr(response, 'error') and response.error:
                raise HandShakeError(response.error)
            return callback(Token.from_string(response.buffer.read()))

        # process
        request = self._get_request(consumer, token, uri, **kwargs)
        AsyncHTTPClient().fetch(
            uri,
            method=request.method,
            body=kwargs.get("body", ''),
            headers=request.to_header(),
            callback=on_response
        )

    def _fetch_sync(self, consumer, token, uri, **kwargs):
        """Send request sync"""
        request  = self._get_request(consumer, token, uri, **kwargs)
        response = HTTPClient().fetch(
            uri,
            method=request.method,
            body=kwargs.get("body", ''),
            headers=request.to_header())
        return Token.from_string(response.buffer.read())

    ##
    # OAuth related (sugar) protected methods
    #
    @staticmethod
    def _get_realm(uri):
        """ calculate realm """
        schema, rest = splittype(uri)
        hierpart = ''
        if rest.startswith('//'):
            hierpart = '//'
        host, rest = splithost(rest)
        return schema + ':' + hierpart + host

    def _get_request(self, consumer, token, uri, **kwargs):
        """Prepare an oauth request based on arguments"""
        request = Request.from_consumer_and_token(
            consumer, token, 
            http_url=uri,
            http_method=kwargs.get("method", HTTP_METHOD),
            parameters=kwargs.get("params"),
            body=kwargs.get("body", ''),
            is_form_encoded = bool(kwargs.get("body", False)),
        )
        request.sign_request(self.method, consumer, token)
        return request

    def _get_consumer(self, credentials):
        """Prepare and store consumer based on oauth arguments"""
        if 'consumer' not in credentials.store(self.implements):
            creds = credentials.to_list("consumer_key", "consumer_secret")
            assert all(creds)
            credentials.store(self.implements)['consumer'] = Consumer(*creds)
        return credentials.store(self.implements)['consumer']

    def _get_token(self, credentials):
        """Prepare and store a token based on credentials"""
        if 'token' not in credentials.store(self.implements):
            creds = credentials.to_list("token_key", "token_secret")
            if all(creds):
                credentials.store(self.implements)['token'] = Token(*creds)
        return credentials.store(self.implements).get('token', None)

    ##
    # OAuth Public token adquisition methods
    #
    def request_token(self, credentials, callback, method="POST"):
        """Implements first stage on OAuth  dance async"""
        self._fetch(
            self._get_consumer(credentials),
            None, self.request_url, callback,
            method=method,
            params=credentials.to_dict("oauth_callback")
        )

    def request_token_sync(self, credentials, method="POST"):
        """Implements first stage on OAuth dance sync"""
        return self._fetch_sync(
            self._get_consumer(credentials),
            None, self.request_url,
            method=method,
            params=credentials.to_dict("oauth_callback")
        )
        
    ###
    # OAuth authorization methods
    #
    def authorization_redirect(self, token):
        """Get the authorization URL to redirect the user"""
        request = Request.from_token_and_callback(       \
            token=token, http_url=self.authorize_url)
        return request.to_url()

    def authorization_redirect_url(self, token, callback):
        """Handle url redirection after user authenticates"""
        raise NotImplementedError

    def authorization_redirect_url_sync(self, token):
        """
        Handle url redirection after user authenticates syncronously
        """
        raise NotImplementedError

    ##
    # OAuth access methods
    #
    def renew_token(self, credentials, callback, method="POST"):
        """
        Renew an already used token
        """

        if not credentials.oauth_session_handle:
            raise HandShakeError("token_not_renewable")

        self._fetch(
            self._get_consumer(credentials),
            self._get_token(credentials),
            self.access_url, callback,
            method=method,
            params=credentials.to_dict('oauth_session_handle')
        )
        
    def renew_token_sync(self, credentials, method="POST"):
        """
        Renew an already used token syncronously
        """

        if not credentials.oauth_session_handle:
            raise HandShakeError("token_not_renewable")

        return self._fetch_sync(
            self._get_consumer(credentials),
            self._get_token(credentials),
            self.access_url,
            method=method,
            params=credentials.to_dict('oauth_session_handle')
        )

    def access_token(self, credentials, token, verifier, callback, method="POST"):
        """
        After user has authorized the request token, get access token
        with user supplied verifier
        """
        self._fetch(
            self._get_consumer(credentials),
            token, self.access_url, callback,
            method=method,
            params={'oauth_verifier' : verifier},
        )

    def access_token_sync(self, credentials, token, verifier, method="POST"):
        """
        After user has authorized the request token, get access token
        with user supplied verifier
        """
        return self._fetch_sync(
            self._get_consumer(credentials),
            token, self.access_url,
            method=method,
            params={'oauth_verifier' : verifier}
        )

    ###
    # XAuth stuff (2LO)
    #
    def xauth_access_token(self, credentials, callback):
        """
        Get an access token from an username and password combination.
        """
        parameters = {
            'x_auth_mode':     'client_auth',
            'x_auth_username': credentials.username,
            'x_auth_password': credentials.password,
            }

        self._fetch(
            self._get_consumer(credentials),
            None, self.access_url, callback,
            method="POST",
            params=parameters,
            body=urlencode(parameters, True).replace('+', '%20')
        )

    def xauth_access_token_sync(self, credentials):
        """
        Get an access token from an username and password combination.
        """
        parameters = {
            'x_auth_mode':     'client_auth',
            'x_auth_username': credentials.username,
            'x_auth_password': credentials.password,
            }

        return self._fetch_sync(
            self._get_consumer(credentials),
            None, self.access_url,
            method="POST",
            params=parameters,
            body=urlencode(parameters, True).replace('+', '%20')
        )

    ###
    # OAuth sign
    # 
    def sign(self, credentials, request, env):
        """Sign request"""
        
        #pylint: disable-msg=C0103
        POST_CONTENT_TYPE = 'application/x-www-form-urlencoded'

        consumer = self._get_consumer(credentials)
        token    = self._get_token(credentials)
        
        if not consumer or not token:
            raise AuthError("Missing oauth tokens")

        # POST
        headers  = request.headers
        if request.verb == "POST":
            assert 'content-type' in headers
            
        # Only hash body and generate oauth_hash for body if
        # Content-Type != form-urlencoded
        isform = headers.get('content-type') == POST_CONTENT_TYPE

        # process post contents if required
        body, parameters = env.get('body', ''), None
        if isform and body:
            contents = body
            if hasattr(body, "read"):
                contents = body.read()
                body.seek(0)
            parameters = parse_qs(contents)

        # update request uri
        oauth_request = Request.from_consumer_and_token(
            consumer, token, request.verb,
            url_concat(request.uri, env["params"]),
            parameters, body, isform)

        # sign
        oauth_request.sign_request(self.method, consumer, token)

        # process body if form or uri if a get/head
        if isform:
            env['body'] = oauth_request.to_postdata()
        elif request.verb in ('GET', 'HEAD',):
            # remove params and update uri store params
            request.uri   = oauth_request.to_url()
            env["params"] = None
        else:
            headers.update(oauth_request.to_header(               \
                    realm=self._get_realm(request.uri)))

    @engine
    def _authenticate(self, credentials, callback):
        token = None

        # First try, if possible, to renew token
        try:
            token = yield Task(self.renew_token, credentials)
            callback(token)
            return
        except HandShakeError, err:
            pass
        except HTTPError, err:
            if err != 'invalid_session_handle':
                # reset credentials
                credentials.oauth_session_handle = None

        # Last chance, try to get a new token
        try:
            if credentials.oauth_callback_handler:
                # Use PIN based OAuth
                token = yield Task(self.request_token, credentials)
                reurl = self.authorization_redirect(token)
                verfy = credentials.oauth_callback_handler(reurl)
                token = yield Task(self.access_token, credentials, token, verfy)
            else:
                # Use XAuth
                token = yield Task(self.xauth_access_token, credentials)
            # retval
            callback(token)
        # A handshake error is also notified.
        except HandShakeError, err:
            callback(err.message)
        except HTTPError, err:
            callback(err)

    def _authenticate_sync(self, credentials):
        token = None
        # First try, if possible, to renew token
        try:
            return self.renew_token_sync(credentials)
        except HandShakeError, err:
            pass
        except HTTPError, err:
            if err != 'invalid_session_handle':
                # reset credentials
                credentials.oauth_session_handle = None

        if credentials.oauth_callback_handler:
            # Use PIN based OAuth
            token = self.request_token_sync(credentials)
            reurl = self.authorization_redirect(token)
            verfy = credentials.oauth_callback_handler(reurl)
            token = self.access_token_sync(credentials, token, verfy)
        else:
            # Use XAuth
            token = self.xauth_access_token_sync(credentials)
        return token

    def _update_credentials(self, credentials, token):
        # store token
        credentials.store(self.implements)['token'] = None
        if isinstance(token, Token):
            credentials.store(self.implements)['token']=token

    ##
    # Auth Main methods
    ##
    @engine
    def authorize(self, credentials, request, env, callback):
        response = None
        try:
            self.sign(credentials, request, env)
        except AuthError:
            response = yield Task(self._authenticate, credentials)
            self._update_credentials(credentials, response)
        # fetch token or response from server
        response = response or credentials.store(self.implements)['token']
        callback(response)
        
    def authorize_sync(self, credentials, request, env):
        try:
            self.sign(credentials, request, env)
        except AuthError:
            # fetch token
            token = self._authenticate_sync(credentials)
            self._update_credentials(credentials, token)
            self.sign(credentials, request, env)

