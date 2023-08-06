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
from cStringIO import StringIO
import gzip

# import Zope3 interfaces

# import local interfaces
from ztfy.file.interfaces import IArchiveExtractor

# import Zope3 packages
from zope.interface import implements

# import local packages
from ztfy.file.property import getMagicContentType
from ztfy.file.archive.tar import TarArchiveExtractor


class GZipArchiveExtractor(object):
    """GZip file format archive extractor"""

    implements(IArchiveExtractor)

    def getContents(self, data):
        if isinstance(data, tuple):
            data = data[0]
        gzip_file = gzip.GzipFile(fileobj=StringIO(data), mode='r')
        gzip_data = gzip_file.read(4096)
        mime_type = getMagicContentType(gzip_data)
        if mime_type == 'application/x-tar':
            tar = TarArchiveExtractor()
            tar.initialize(data, mode='r:gz')
            for element in tar.getContents():
                yield element
        else:
            next_data = gzip_file.read()
            while next_data:
                gzip_data += next_data
                next_data = gzip_file.read()
            yield (gzip_data, '')
