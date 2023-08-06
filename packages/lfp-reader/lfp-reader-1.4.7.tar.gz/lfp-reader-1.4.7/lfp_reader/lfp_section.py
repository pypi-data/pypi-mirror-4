# python
#
# lfp-reader
# LFP (Light Field Photography) File Reader.
#
# http://behnam.github.com/python-lfp-reader/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2012  Behnam Esfahbod


"""Read and verity sections of a LFP file
"""

import struct
import json


################################
# General

class LfpReadError(Exception):
    """File data reading error"""

class LfpSection:
    """LFP file section"""

    NAME           = None
    MAGIC          = None
    MAGIC_LENGTH   = 12
    SIZE_LENGTH    = 4        # = 16 - MAGIC_LENGTH
    SHA1_LENGTH    = 45       # = len("sha1-") + (160 / 4)
    PADDING_LENGTH = 35       # = (4 * 16) - MAGIC_LENGTH - SIZE_LENGTH - SHA1_LENGTH

    _size = None
    _sha1 = None
    _data = None
    _dpos = None
    _inf  = None

    ################
    # Internals

    def __init__(self, inf):
        self._inf = inf
        self.read()

    def __repr__(self):
        if self._size > 0:
            return "%s(%sB)" % (self.NAME, self._size)
        else:
            return "%s()" % (self.NAME)

    @property
    def size(self): return self._size

    @property
    def sha1(self): return self._sha1

    @property
    def data(self):
        if self._size > 0 and self._data is None:
            self._inf.seek(self._dpos, 0)
            self._data = self._inf.read(self._size)
        return self._data

    ################
    # Loading

    def read(self):
        # Read and check magic
        magic = self._inf.read(self.MAGIC_LENGTH)
        if magic != self.MAGIC:
            raise LfpReadError("Invalid magic bytes for section %s!" % self.NAME)
        # Read size
        self._size = struct.unpack(">i", self._inf.read(self.SIZE_LENGTH))[0]
        if self._size > 0:
            # Read sha1
            self._sha1 = self._inf.read(self.SHA1_LENGTH)
            # Skip fixed null chars
            self._inf.read(self.PADDING_LENGTH)
            # Skip data
            self._dpos = self._inf.tell()
            self._inf.seek(self._size, 1)
            # Skip extra null chars
            ch = self._inf.read(1)
            while ch == '\0':
                ch = self._inf.read(1)
            self._inf.seek(-1, 1)
        return self

    ################
    # Exporting

    def export_data(self, exp_path):
        if self.data is None:
            raise LfpReadError("No data to export for section %s!" % self.NAME)
        with open(exp_path, 'wb') as exp_file:
            exp_file.write(self.data)


################################
# Section Types

class LfpHeader(LfpSection):
    """LFP file metadata"""
    NAME = "Header"
    MAGIC = "\x89LFP\x0D\x0A\x1A\x0A\x00\x00\x00\x01"

class LfpMeta(LfpSection):
    """LFP file metadata"""
    NAME = "Meta"
    MAGIC = "\x89LFM\x0D\x0A\x1A\x0A\x00\x00\x00\x00"

    _content = None

    @property
    def content(self):
        if self._content is None:
            self._content = json.loads(self.data)
        return self._content

class LfpChunk(LfpSection):
    """LFP file data chuck"""
    NAME = "Chunk"
    MAGIC = "\x89LFC\x0D\x0A\x1A\x0A\x00\x00\x00\x00"

