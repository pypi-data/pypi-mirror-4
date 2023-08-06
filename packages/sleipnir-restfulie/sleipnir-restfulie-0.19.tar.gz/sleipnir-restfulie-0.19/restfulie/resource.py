# -*- mode:python; coding: utf-8 -*-

"""
resource

Represents a generic gateway to AMQP implementation
"""

from __future__ import absolute_import

__author__ = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.

__all__ = ['Resource', 'MappingResource']

# Project requirements

# local submodule requirements


class ResourceError(Exception):
    """Resource exception"""


#pylint: disable-msg=R0922
class Resource(object):
    """
    Prepares a connection. only get a pika connection is lazy
    created
    """

    def links(self):
        """Returns a list of all links."""
        raise NotImplementedError

    def link(self, rel, default=None):
        """Return a Link with rel."""
        raise NotImplementedError

    def body(self):
        """Returns content"""
        raise NotImplementedError

    def error(self):
        """
        Return error if any or None if no error is present or isn't
        suported by format
        """
        raise NotImplementedError


#pylint: disable-msg=R0921
class MappingResource(Resource):
    """
    An specialiced resources that allow to access item collections
    """

    def __len__(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __contains__(self, key):
        raise NotImplementedError

    def __getitem__(self, key):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise AttributeError(
            "Trying to set '{0}' to '{1}' on "
            "a read only resource".format(key, value)
        )

    def __delitem__(self, key):
        raise AttributeError(
            "Trying to remove '{0}' on a read only "
            "resource".format(key)
        )
