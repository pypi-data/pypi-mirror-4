#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
json

Json converter and resource
"""

from __future__ import absolute_import

__author__ = "caelum - http://caelum.com.br"
__modified_by__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.
import logging
try:
    import json
except ImportError:
    # python 2.5
    import simplejson as json
# for patcher
import jsonpatch

__all__ = []

# Project requirements

# local submodule requirements
from ..resource import Resource
from ..links import Links, Link
from ..converters import Converters, ConverterMixin
from ..patchers import PatcherMixin, PatcherError


class JsonResource(Resource):
    """This resource is returned when a JSON is unmarshalled"""

    class JsonData(dict):
        """Simple Dic that allow access to keys as attributes"""
        __dict__ = True
        def __getattr__(self, key):
            return self[key]
        def __setattr__(self, key, value):
            if key not in self:
                dict.__setattr__(self, key, value)
                return
            self[key] = value
            
    def __init__(self, data):
        """JsonResource attributes can be accessed with 'dot'"""
        super(JsonResource, self).__init__()
        
        # We don't spect a tuple from remote, becouse som
        # vulnerabilities with JSON and javascript. Otherwise, is
        # legal to produce json tuple and send to server, (for
        # PATCH). See
        # http://haacked.com/archive/2008/11/20/
        # anatomy-of-a-subtle-json-vulnerability.aspx
        assert isinstance(data, dict)

        # Init parameters to safe defaults
        self._error  = None
        self._links  = Links([])
        self._data   = self.JsonData()

        # Parse data
        self._parse_data(self._data, data)
        
    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return self._data.iteritems()

    def __contains__(self, key):
        return key in self._data

    def __getitem__(self, key):
        return self._data[key]
        
    def __getattr__(self, key):
        if not key.startswith("_"):
            return getattr(self._data, key)
        raise AttributeError(key)
        
    def _parse_data(self, root, data):
        """
        Process data dictionary and store it on root. Root should
        be a dict like instance
        """
        for key, value in data.iteritems():
            # remove unicode
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            # process links
            if key == "_links":
                self._parse_links(data)
            # store error, only one is allowed
            elif key == "_error":
                assert self._error is None
                self._error = self._parse_data(self.JsonData(), value)
            # Just ignore protected args"
            elif key.startswith("_"):
                logging.warning("Ignoring " + key)
            # process data
            elif isinstance(value, dict):
                root[key] = self._parse_data(self.JsonData(), value)
            # process collections
            elif isinstance(value, (list, tuple,)):
                root[key] = []
                for val in value:
                    if isinstance(val, dict):
                        val = self._parse_data(self.JsonData(), val)
                    root[key].append(val)
            # last resource: Store key - value pair
            else:
                root[key] = value
        return root

    #pylint: disable-msg=W0142
    def _parse_links(self, data):
        """Find links on dictionary"""
        retval = []
        #Set a json as the default content-type for this link if
        #no one has been set by the server
        #pylint:disable-msg=W0106
        for key, link in data['_links'].iteritems():
            link = dict(link)
            link.setdefault('rel', key)
            link.setdefault('type', 'application/json')
            retval.append(Link(**link))
        # update links
        self._links.update(retval)

    def link(self, rel, default=None):
        return self.links().rel(rel, default)

    def links(self):
        return self._links

    def error(self):
        return self._error
        

class JsonConverter(ConverterMixin):
    """Converts objects from and to JSON"""

    types = [
        'application/json', 'text/json', 'json',
        'application/json-patch', 'text/json-patch', 'json-patch'
    ]

    def __init__(self):
        ConverterMixin.__init__(self)

    #pylint: disable-msg=R0201
    def marshal(self, content):
        """Produces a JSON representation of the given content"""
        if hasattr(content, 'write'):
            return json.dump(content)    
        return json.dumps(content)

    #pylint: disable-msg=R0201
    def unmarshal(self, json_content):
        """Produces an object for a given JSON content"""
        if hasattr(json_content, 'read'):
            return JsonResource(json.load(json_content))
        return JsonResource(json.loads(json_content))

class JsonPatcher(PatcherMixin):
    """Merge and create patchs in jsonpatch format"""

    types = JsonConverter.types

    def __init__(self):
        PatcherMixin.__init__(self)
        
    @staticmethod
    def __get_python_container(container):
        """
        Sugar method to get a valid python container from a json string
        """
        try:
            if isinstance(container, basestring) or hasattr(container, 'read'):
                container = Converters.for_type('json').unmarshal(container)
        except Exception, err:
            raise PatcherError(err.message)
        return container
    
    def apply(self, doc, patch, in_place=False):
        # get a valid dict of fail
        doc = self.__get_python_container(doc)
        # apply patch
        return jsonpatch.apply_patch(doc, patch, in_place)

    def make(self, src, dst):
        src = self.__get_python_container(src)
        dst = self.__get_python_container(dst)
        return jsonpatch.make_patch(src, dst).patch
            
    
            
        
        