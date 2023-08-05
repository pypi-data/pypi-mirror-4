#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
links

Hipermedia objects
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.
import hal

__all__ = ['Link', 'Links']

# Project requirements

# local submodule requirements

class LinkError(Exception):
    """Define a missing link error"""


#pylint: disable-msg=R0903
class Link(hal.Link):
    """Link represents generic link. You can follow it"""

    def follow(self):
        """Return a DSL object with the Content-Type set"""
        from .configuration import Configuration
        return Configuration(self.href).as_(self.content_type)


#pylint: disable-msg=R0903
class Links(hal.Links):
    """Links a simple Link """
