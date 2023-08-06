### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################


# import standard packages
import bz2

# import Zope3 interfaces

# import local interfaces
from ztfy.file.interfaces import IArchiveExtractor

# import Zope3 packages
from zope.interface import implements

# import local packages
from ztfy.file.property import getMagicContentType
from ztfy.file.archive.tar import TarArchiveExtractor


CHUNK_SIZE = 4096


class BZip2ArchiveExtractor(object):
    """BZip2 file format archive extractor"""

    implements(IArchiveExtractor)

    def initialize(self, data):
        if isinstance(data, tuple):
            data = data[0]
        self.data = data
        self.bz2 = bz2.BZ2Decompressor()

    def getContents(self):
        position = 0
        compressed = self.data[position:position + CHUNK_SIZE]
        decompressed = self.bz2.decompress(compressed)
        while (not decompressed) and (position < len(self.data)):
            compressed = self.data[position:position + CHUNK_SIZE]
            decompressed = self.bz2.decompress(compressed)
            position += CHUNK_SIZE
        mime_type = getMagicContentType(decompressed[:CHUNK_SIZE])
        if mime_type == 'application/x-tar':
            tar = TarArchiveExtractor()
            tar.initialize(self.data, mode='r:bz2')
            for element in tar.getContents():
                yield element
        else:
            while position < len(self.data):
                compressed = self.data[position:position + CHUNK_SIZE]
                decompressed += self.bz2.decompress(compressed)
                position += CHUNK_SIZE
            yield (decompressed, '')
