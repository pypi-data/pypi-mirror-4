#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
patcher
"""

from __future__ import absolute_import

__author__   = "Carlos Martin <inean.es@gmail.com>"
__license__  = "See LICENSE.restfulie for details"

# Import here any required modules.

__all__ = ['Patchers', 'PatcherMixin']

# Project requirements

# local submodule requirements

class PatcherError(Exception):
    """Resource exception"""

class Patchers(object):
    """Utility methods for patchers."""

    types = {}

    @classmethod
    def register(cls, a_type, patcher):
        """Register a patcher for the given type"""
        cls.types[a_type] = patcher

    @classmethod
    def for_type(cls, a_type):
        """Return a valid patcher for the given type"""
        return cls.types[a_type]

        
class MetaPatcher(type):
    """Patcher Metaclass"""

    def __init__(mcs, name, bases, dct):
        type.__init__(mcs, name, bases, dct)
        if name.endswith("Patcher"):
            for a_type in mcs.types:
                Patchers.register(a_type, mcs())


class PatcherMixin(object):
    """
    Abstract class to define patcher classes. This class has support
    to create chained patchers
    """

    __metaclass__ = MetaPatcher

    def apply(self, doc, patch, in_place=False):
        """Does nothing"""
        raise NotImplementedError

    def make(self, src, dst):
        """Returns content without modification"""
        raise NotImplementedError
