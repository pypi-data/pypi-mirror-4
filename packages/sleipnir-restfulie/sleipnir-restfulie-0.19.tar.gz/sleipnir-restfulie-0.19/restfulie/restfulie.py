# -*- mode:python; coding: utf-8 -*-

"""
Request
"""

from __future__ import absolute_import

__author__ = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.

__all__ = ['Restfulie']

# Project requirements
from .configuration import Configuration


#pylint: disable-msg=R0903
class Restfulie(object):
    """Restfulie entry point"""

    # pylint: disable-msg=C0103, R0913
    @staticmethod
    def at(uri, flavors=None, chain=None, compress=False,
           ca_certs=None, connect_timeout=None, request_timeout=None):
        """Create a new entry point for executing requests"""

        return Configuration(
            uri,
            flavors=flavors,
            chain=chain,
            compress=compress,
            ca_certs=ca_certs,
            connect_timeout=connect_timeout,
            request_timeout=request_timeout
        )
