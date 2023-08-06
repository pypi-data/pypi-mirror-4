# -*- mode:python; coding: utf-8 -*-

"""
plain

Plain converter and resource
"""

from __future__ import absolute_import

__author__ = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.

__all__ = []

# Project requirements

# local submodule requirements
from ..resource import Resource
from ..links import Links
from ..converters import ConverterMixin


class PlainResource(Resource):
    """This resource is returned when a PLAIN is unmarshalled"""

    def __init__(self, content):
        """PlainResource attributes can be accessed with 'dot'"""
        super(PlainResource, self).__init__()
        self._content = content
        self._links = Links([])

    def link(self, rel, default=None):
        return None

    def links(self):
        return self._links

    def body(self):
        return self._content

    def error(self):
        return None


class PlainConverter(ConverterMixin):
    """Dummy converter to plain text"""

    types = ['text/plain', 'text/html']

    def __init__(self):
        ConverterMixin.__init__(self)

    def unmarshal(self, content):
        """Returns content without modification"""
        return PlainResource(content)
