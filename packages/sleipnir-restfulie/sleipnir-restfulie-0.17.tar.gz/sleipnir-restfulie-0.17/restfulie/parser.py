#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
parser
"""

from __future__ import absolute_import

__author__ = "caelum - http://caelum.com.br"
__modified_by__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.

__all__ = ['Parser']


#pylint: disable-msg=R0903
class Parser(object):
    """Executes processors ordered by the list"""

    def __init__(self, processors):
        self._processors = processors

    def __len__(self):
        return len(self._processors)
        
    def follow(self, callback, request, env):
        """Follow chain"""
        processor = self._processors.pop(0)
        return processor.execute(callback, self, request, env)
