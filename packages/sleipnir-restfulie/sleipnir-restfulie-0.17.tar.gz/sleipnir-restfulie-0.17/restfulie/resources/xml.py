#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
xml

XML converter and resource
"""

from __future__ import absolute_import

__author__ = "caelum - http://caelum.com.br"
__modified_by__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.
from xml.etree import ElementTree

__all__ = []

# local submodule requirements
from ..resource import Resource
from ..links import Links, Link
from ..converters import ConverterMixin


class XMLResource(Resource):
    """
    This resource is returned when a XML is unmarshalled.
    """

    def __init__ (self, element_tree):
        super(XMLResource, self).__init__()

        self.element_tree = element_tree
        self._links = Links(self._parse_links())
        self._enhance_element_tree()

    def _enhance_element_tree(self):
        """
        Enables access to XMLResources attributes with 'dot'.
        """
        setattr(self, "tag", self.element_tree.tag)

        for root_child in list(self.element_tree):
            tag = root_child.tag
            if tag != 'link':
                if len(self.element_tree.findall(root_child.tag)) > 1:
                    setattr(self, tag, self.element_tree.findall(tag))
                elif len(list(root_child)) == 0:
                    setattr(self, tag, root_child.text)
                else:
                    setattr(self, tag, self.element_tree.find(tag))

        for element in self.element_tree.getiterator():
            for child in list(element):
                if len(element.findall(child.tag)) > 1:
                    setattr(element, child.tag, element.findall(child.tag))
                elif len(list(child)) == 0:
                    setattr(element, child.tag, child.text)
                else:
                    setattr(element, child.tag, element.find(child.tag))

    def _parse_links(self):
        """
        Find links in a ElementTree
        """
        links = []
        for element in self.element_tree.getiterator('link'):
            link = Link({
                    'href': element.attrib.get('href'),
                    'rel':  element.attrib.get('rel'),
                    'type': element.attrib.get('type') or 'application/xml',
            })
            links.append(link)
        return links

    def links(self):
        return self._links

    def link(self, rel):
        return self.links().get(rel)



class XmlConverter(ConverterMixin):
    """
    Converts objects from and to XML.
    """
    
    types = ['application/xml', 'text/xml', 'xml']

    def __init__(self):
        ConverterMixin.__init__(self)

    def marshal(self, content):
        """
        Produces a XML representation of the given content.
        """
        return ElementTree.tostring(self._dict_to_etree(content))

    def _dict_to_etree(self, content):
        """
        Receives a dictionary and converts to an ElementTree
        """
        tree = ElementTree.Element(content.keys()[0])
        self._dict_to_etree_rec(content[content.keys()[0]], tree)
        return tree

    def _dict_to_etree_rec(self, content, tree):
        """
        Auxiliar function of _dict_to_etree_rec
        """
        if type(content) == dict:
            for key, value in content.items():
                element = ElementTree.Element(key)
                self._dict_to_etree_rec(value, element)
                tree.append(element)
        else:
            tree.text = str(content)

    def unmarshal(self, content):
        """
        Produces an ElementTree object for a given XML content.
        """
        element = ElementTree.fromstring(content.read())
        return XMLResource(element)

