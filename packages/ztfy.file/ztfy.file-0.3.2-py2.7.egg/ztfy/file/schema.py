### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008 Thierry Florac <tflorac AT ulthar.net>
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

# import Zope3 interfaces

# import local interfaces
from ztfy.file.interfaces import IHTMLField, IFileField, IImageField, ICthumbImageField

# import Zope3 packages
from zope.interface import implements
from zope.schema import Text, Bytes

# import local packages


class HTMLField(Text):
    """Custom field used to handle HTML properties"""

    implements(IHTMLField)


class FileField(Bytes):
    """Custom field used to handle file-like properties"""

    implements(IFileField)

    def _validate(self, value):
        pass


class ImageField(FileField):
    """Custom field used to handle image-like properties"""

    implements(IImageField)


class CthumbImageField(ImageField):
    """Custom field used to handle images with cthumb selection"""

    implements(ICthumbImageField)
