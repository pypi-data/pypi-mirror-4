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
import zipfile

# import Zope3 interfaces

# import local interfaces
from ztfy.file.interfaces import IArchiveExtractor

# import Zope3 packages
from zope.component import queryUtility
from zope.interface import implements

# import local packages
from ztfy.file.property import getMagicContentType


class ZipArchiveExtractor(object):
    """ZIP file format archive extractor"""

    implements(IArchiveExtractor)

    def initialize(self, data, mode='r'):
        if isinstance(data, tuple):
            data = data[0]
        self.zip_data = zipfile.ZipFile(StringIO(data), mode=mode)

    def getContents(self):
        members = self.zip_data.infolist()
        for member in members:
            filename = member.filename
            content = self.zip_data.read(filename)
            mime_type = getMagicContentType(content[:4096])
            extractor = queryUtility(IArchiveExtractor, name=mime_type)
            if extractor is not None:
                extractor.initialize(content)
                for element in extractor.getContents():
                    yield element
            else:
                yield (content, filename)
