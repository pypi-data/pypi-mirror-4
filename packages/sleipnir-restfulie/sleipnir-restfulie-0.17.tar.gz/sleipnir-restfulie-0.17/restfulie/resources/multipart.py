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
import hashlib
import tempfile

__all__ = []

# Project requirements
from tornado.escape import utf8

# local submodule requirements
from ..converters import ConverterMixin

TEMP_FILE_SIZE = 128 * 1024

class FileWrapper(object):
    """
    Simple wrapper to allow get length of content. Required by HTTP
    handlers
    """
    
    __slots__ = ("_file",)
    
    def __init__(self, wrapped):
        object.__setattr__(self, "_file", wrapped)

    def __len__(self):
        # get current pos
        curpos = self._file.tell()
        # got to end
        self._file.seek(0, 2)
        # compute length
        length = self._file.tell()
        # restore pos
        self._file.seek(curpos)
        return length
        
    def __getattr__(self, key):
        return getattr(self._file, key)
        
    def __setattr__(self, key, value):
        setattr(self._file, key, value)
        
    def read(self, *args):
        """Overrided read to return always an utf8 string"""
        return utf8(self._file.read(*args))
        
        
        
class Part(object):

    EOL="\r\n".encode('latin-1')

    def __init__(self, boundary, name, contents):
        self.boundary = boundary
        self.name     = name
        self.contents = contents

    def write(self, output):
        raise NotImplementedError

        
class ParamPart(Part):
    def write(self, output):
        output.writelines(("--", self.boundary, self.EOL))
        output.writelines(('Content-Disposition: form-data; name="', self.name, '"', self.EOL))
        output.writelines((self.EOL, self.contents, self.EOL))


class FilePart(Part):
    def write(self, output, algorithm=None):
        # write header
        output.writelines(("--", self.boundary, self.EOL))
        output.writelines(('Content-Disposition: form-data; name="', self.name, '"; filename="', self.name, '"' ,self.EOL))
        output.writelines(('Content-Type: application/octet-stream', self.EOL))
        output.writelines(('Content-Transfer-Encoding: binary', self.EOL))
        output.write(self.EOL)

        # write file contents
        digest = algorithm() or None
        for chunk in iter(lambda: self.contents.read(8192), b''):
            output.write(chunk)
            digest and digest.update(chunk)

        # end header
        output.write(self.EOL)
        return digest

    
class MultiPartConverter(ConverterMixin):
    """Multipart form encoder"""

    types = ['multipart/form-data']


    def __init__(self, boundary=None):
        # Only create a boundary property if boundary is defined
        if boundary is not None:
            self.boundary = boundary[0].split('=')[1]
        ConverterMixin.__init__(self)


    def marshal(self, content):
        """Produces a well formated multipart"""

        assert isinstance(content, dict)
        assert self.boundary

        # ouput buffer
        try:
            # Use a memory file solution for content <= 128Kb
            output = tempfile.SpooledTemporaryFile(TEMP_FILE_SIZE)
        except Exception:
            # python 2.5
            output = tempfile.TemporaryFile()

        # parse params
        for key, value in content.iteritems():
            # write header
            if hasattr(value, "writelines"):
                flpart = FilePart(self.boundary, key, value)
                digest = flpart.write(output, algorithm=hashlib.sha1)
                
                # prepare to write digest param
                key   = key + "_sha1sum"
                value = digest.hexdigest()

            # it's a param or we are writing sum
            param = ParamPart(self.boundary, key, value)
            param.write(output)

        output.writelines(("--", self.boundary, "--", Part.EOL))

        # return output stored file
        output.seek(0)
        return FileWrapper(output)

