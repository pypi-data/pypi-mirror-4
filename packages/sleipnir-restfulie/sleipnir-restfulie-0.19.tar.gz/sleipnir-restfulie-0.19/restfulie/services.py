# -*- mode:python; coding: utf-8 -*-

"""
Services
"""

from __future__ import absolute_import

__author__ = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# required modules
import os
import numbers
import urlparse
import itertools
import collections

__all__ = ['Services']

# Import here local requirements
from .cached import cached


# pylint: disable-msg=R0903
class FrozenDict(object):
    """Proxy to convert mappings into read-only elements"""

    __FROZEN_METHODS = (
        'clear',
        'pop',
        'popitem',
        'setdefault',
        'update',
    )

    def __init__(self, dct):
        self.__dct = dct

    def __getattr__(self, key):
        if key in self.__FROZEN_METHODS:
            raise AttributeError("Frozen dict in use")
        return getattr(self.__dct, key)

    def __setattr__(self, key, value):
        if not key.startswith("_"):
            raise AttributeError("Frozen dict in use")
        object.__setattr__(self, key, value)


# pylint: disable-msg=R0903
class Services(object):
    """
    Services configuration class. Provides information about available
    services location and security requirements
    """

    # Currently allowed service description keys
    SERVICE_ITEMS = [
        'protocol',
        'host',
        'path',
        'port',
        'secure_port',
        'ca_certs',
        'enforce',
    ]

    def __init__(self):
        # targets defines a map between services and endpoints
        self._targets = {}
        self._services = {}

    def __iter__(self):
        return self._services.iterkeys()

    def __contains__(self, key):
        return key in self._services

    def register(self, target, endpoint, service_name):
        """Set a endpoint to be handled by service"""
        self._targets.setdefault(target, {})[endpoint] = service_name

    def resolv(self, entrypoint, fallback=None):
        """Query wich service provides endpoint"""
        try:
            target, _, endpoint = entrypoint.partition("/")
            return self._targets[target][endpoint]
        except KeyError, err:
            if fallback is not None:
                return fallback
            raise err

    @cached
    def service(self, name):
        """Fetch a service"""
        retval = self._services.get(name)
        return retval or FrozenDict(retval)

    def set_services(self, services):
        """
        Register collection of services. Override current values if
        already exists
        """
        self._services.update(services)

    def set_service_item(self, key, value, services=None):
        """
        Update key, value pair for services
        """
        if key not in self.SERVICE_ITEMS:
            raise AttributeError("Invalid service key '{0}'".format(key))

        # selective update
        if services:
            assert isinstance(services, collections.Sequence)
            svfilter = lambda x: x in self._services
            services = itertools.ifilter(svfilter, services)
        # update all
        services = services or self._services.iterkeys()
        # pylint: disable-msg=W0106
        [self._services[service].update([(key, value)])
         for service in services]

    def get_url(self, service, extra_path=None, query=None, fragment=None):
        """
        Build an url for a service. If extra_path is an absolute path,
        path from service will be ignored
        """

        # fetch service instance
        service = self._services.get(service)
        if service:
            # get protocol
            protocol = service.get('protocol', 'http')
            port = 'secure_port' if protocol == 'https' else 'port'
            # get netloc
            host = service['host']
            port = service.get(port)
            # if it's a valid port number, get a better netloc'
            if isinstance(port, numbers.Integral):
                host = "{0}:{1}".format(host, port)
            # build path
            path = service.get('path', '')
            if extra_path:
                path = extra_path if extra_path[0] == '/' \
                    else os.path.join(path, extra_path)
            # build it;
            return urlparse.urlunsplit((protocol, host, path, query, fragment))
        # No service
        return None

    @cached
    def get_secure(self, service_name, secure=None, port=None, ca_certs=None):
        """Get a secure tuple as required by secure method of restfulie"""

        # fetch service
        service = self._services[service_name]

        # if enforce is set, base is ignored
        ssecure = service.get('protocol') == 'https'
        sport = service.get('secure_port' if ssecure else 'port')
        sca_certs = service.get('ca_certs') if ssecure else None
        if service.get('enforce', False):
            return [ssecure, sport, sca_certs]

        # Get base values
        retval = [secure, port, ca_certs]

        # Override port, if base defines some kind of security None
        # means leave 'as is'
        if retval[0] is not None:
            port = 'port'
            if retval[0]:
                port = 'secure_port'
            # override port
            retval[1] = retval[1] or service.get(port)

        #if retval[0] or retval[0] is None and ssecure:
        # Add ca_certs if no one is set and https or 'as is' is required
        retval[2] = retval[2] or sca_certs

        # done!
        return retval

    @classmethod
    def get_instance(cls):
        """Get service singleton instance"""
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance
