# -*- mode:python; coding: utf-8 -*-

"""
Client
"""

from __future__ import absolute_import

__author__ = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.
import os
import re
import shutil
import tempfile
import itertools
import functools
import contextlib

__all__ = ['Client', 'Extend']

# local submodule requirements
from restfulie.services import Services
from restfulie.credentials import Credentials

# import here local submodules
RE = re.compile(r'[^\w\-_\.]')
TMPDIR = '/var/tmp'
try:
    from sleipnir.frontends.handset import constants
    TMPDIR = constants.__tmp_dir__
except ImportError:
    pass


class Extend(type):
    """
    Allow Ad-hoc inheritance. See
    http://code.activestate.com/recipes/412717-extending-classes/ for
    details
    """

    clients = {}

    #pylint: disable-msg=W0613
    def __new__(mcs, name, bases, dct):
        prev = Extend.clients[name]
        del dct['__module__']
        del dct['__metaclass__']
        for key, value in dct.iteritems():
            if key == "__doc__":
                continue
            setattr(prev, key, value)
        return prev


class ClientMeta(type):
    """
    Simple metaclass to make client subclasses discoverable by
    Extend metaclass
    """
    def __init__(cls, name, bases, dct):
        super(ClientMeta, cls).__init__(name, bases, dct)
        assert name not in Extend.clients
        Extend.clients[name] = cls


class Client(object):
    """Base class to implement a remote API"""

    __metaclass__ = ClientMeta

    # Services to be registered
    SERVICES = {}

    # Allow to translate a Target variable into a valid service tag
    # already registered in session singleton instance
    ENTRY_POINTS = {}

    def __init__(self, credentials=None):
        # register services
        services = Services.get_instance()
        services.set_services(self.SERVICES)

        # register endpoints, if any
        for target, endpoints in self.ENTRY_POINTS.iteritems():
            for endpoint, service in endpoints.iteritems():
                services.register(target, endpoint, service)

        # create credentials
        self._config = credentials or Credentials()

    @contextlib.contextmanager
    def configure(self):
        """Get an accessor to credentials element"""
        yield self._config

    @property
    def credentials(self):
        """Get credentials element"""
        return self._config

    @classmethod
    def _override_ca_certs(cls, services, locations=None, inline=None):
        """Override ca-certfiles from tornado with a custom cas"""

        def read_files(locs):
            """Fetch pem files from firt level dirs"""

            pem_dirs = itertools.ifilter(os.path.isdir, locs)
            pem_dirs = itertools.imap(os.listdir, pem_dirs)
            # Fetch files
            pem_file = itertools.ifilterfalse(os.path.isdir, locs)
            # Open it; pylint: disable-msg=W0142
            for path in itertools.chain(pem_file, *pem_dirs):
                # Only process One dir level
                try:
                    with open(path, 'r') as source:
                        yield source.read()
                except IOError:
                    pass

        # pylint: disable-msg=W0106
        os.path.exists(TMPDIR) or os.makedirs(TMPDIR, mode=0755)
        crt = tempfile.NamedTemporaryFile(dir=TMPDIR)

        if locations:
            ca_pems = itertools.imap("{0}\n".format, read_files(locations))
            crt.writelines(ca_pems)
        if inline:
            ca_pems = itertools.imap("{0}\n".format, inline)
            crt.writelines(ca_pems)
        crt.seek(0)

        # Register cacert
        ca_files = [os.path.join(TMPDIR, RE.sub('@', key)) for key in services]
        copy_files = itertools.izip([crt.name] * len(services), ca_files)

        # Copy; pylint: disable-msg=W0106
        [shutil.copyfile(src, dst) for src, dst in copy_files]

        # Update services dict for selected services
        instance = Services.get_instance()
        map_func = functools.partial(instance.set_service_item, "ca_certs")
        services = ([service] for service in services)
        list(itertools.imap(map_func, ca_files, services))

    @classmethod
    def override_entrypoint(cls, target, endpoint, service_name):
        """
        Register service_name as provider of target/endpoint
        combination
        """
        # fetch services
        instance = Services.get_instance()
        # Register
        instance.register(target, endpoint, service_name)

    @classmethod
    def override_service(cls, service_name, **items):
        """
        Create a new service definition and register as default
        service for selected targets
        """
        # fetch services
        instance = Services.get_instance()
        # Old service is frozen. Clone and update
        new_service = dict(instance.service(service_name)) \
            if service_name in instance else dict()
        new_service.update(items)
        # Register
        instance.set_services([(service_name, new_service,)])

    @classmethod
    def override_service_item(cls, key, value=None, services=None, **kwargs):
        """Override service item"""
        # fetch services
        instance = Services.get_instance()
        # Get services that will be overrided by cacerts
        services = services or list(iter(instance))
        assert not isinstance(services, basestring)
        # ca_certs update is complex, so we delegate to a custom method
        if key == 'ca_certs':
            return cls._override_ca_certs(services=services, **kwargs)
        # Update services dict for selected services
        instance.set_service_item(key, value, services)
