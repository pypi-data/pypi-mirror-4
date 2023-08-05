#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
request
"""

from __future__ import absolute_import

__author__ = "caelum - http://caelum.com.br"
__modified_by__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.

__all__ = ['Request']

# Project requirements
from .parser import Parser

class Request(object):
    """An HTTP request"""

    def __init__(self, config):
        self._config = config

    def __call__(self, body=None, params=None, callback=None):
        """
        Perform the request.The optional payload argument is sent to
        the server
        """
        env = {
            'params'  : params,
            'payload' : body,
            }

        procs = list(self._config.processors)
        return Parser(procs).follow(callback, self._config, env)
