"""Basic Restufl module with support for hypermedia"""

#pylint: disable-msg=W0401
from __future__ import absolute_import

# FIXME: Import this here forces sleipnir shell to load all resources
# code at application startup, which increases shell loginc in a 40%
# (from 1s to ,14s aprox)
from .auth import *
from .resources import *
