#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
converter
"""

from __future__ import absolute_import

__author__ = "caelum - http://caelum.com.br"
__modified_by__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.

__all__ = ['Converters', 'ConverterMixin']

# Project requirements

# local submodule requirements

class ConverterError(Exception):
    """Resource exception"""

class Converters(object):
    """Utility methods for converters."""

    types = {}

    @classmethod
    def register(cls, a_type, converter):
        """Register a converter for the given type"""
        cls.types[a_type] = converter

    @classmethod
    def marshaller_for(cls, a_type):
        """Return a converter for the given type"""
        if type(a_type) in (str, unicode,):
            # common case. Throw a key error exception if no valid one
            # has been registered"
            if ";" not in a_type:
                return cls.types[a_type]
            # Passed a composed string (';' separated)
            a_type, key = a_type.split(";"), a_type
        else:
            # Passed a list
            assert len(a_type) > 0
            a_type, key = a_type, ";".join(a_type)

        # Dinamically, create a valid converter if required for this
        # kind of element.Converters are stateless,
        return cls.types.setdefault(   \
            key,                              \
            cls.types[a_type[0]].__class__(a_type[1:]))

    @classmethod
    def for_type(cls, a_type):
        return cls.marshaller_for(a_type)
        
    
class MetaConverter(type):
    """Converter Metaclass"""

    def __init__(mcs, name, bases, dct):
        type.__init__(mcs, name, bases, dct)
        if name.endswith("Converter"):
            for a_type in mcs.types:
                Converters.register(a_type, mcs())


class ConverterMixin(object):
    """
    Abstract class to define converter classes. This class has support
    to create chained converters
    """

    __metaclass__ = MetaConverter

    def __init__(self, a_type_list=None):
        # Store next converter in chain
        self._chain = None
        assert not a_type_list or hasattr('__iter__', a_type_list)
        # Allow this class to also be used like a dead end
        if a_type_list and len(a_type_list) > 1:
            self._chain = Converters.marshaller_for(list(a_type_list)[1:])

    def marshal(self, content):
        """Does nothing"""
        return content if not self._chain else self.chain.marshal(content)

    def unmarshal(self, content):
        """Returns content without modification"""
        return content if not self._chain else self.chain.marshal(content)
