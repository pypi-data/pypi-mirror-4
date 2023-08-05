#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
multipart

multipart marshaller
"""

from __future__ import absolute_import

__author__ = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.
import urllib

__all__ = []

# Project requirements

# local submodule requirements
from ..converters import ConverterMixin


class MultiPartConverter(ConverterMixin):
    """Multipart form encoder"""

    types = ['application/x-www-form-urlencoded']

    def __init__(self):
        ConverterMixin.__init__(self)

    def marshal(self, content):
        """Produces a well formaed form"""
        return urllib.urlencode(content)
