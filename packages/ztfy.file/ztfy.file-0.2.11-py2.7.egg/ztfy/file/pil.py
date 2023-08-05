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
from cStringIO import StringIO
from PIL import Image, ImageFilter

# import Zope3 interfaces

# import local interfaces
from ztfy.file.interfaces import IThumbnailGeometry, IThumbnailer, DEFAULT_DISPLAYS

# import Zope3 packages
from zope.interface import implements

# import local packages


class PILThumbnailer(object):

    implements(IThumbnailer)

    order = 50

    def createThumbnail(self, image, size, format=None):
        img = Image.open(StringIO(image.data))
        new = StringIO()
        if not format:
            format = img.format
        format = format.upper()
        if format not in ('GIF', 'JPEG', 'PNG'):
            format = 'JPEG'
        img.resize(size, Image.ANTIALIAS).filter(ImageFilter.SHARPEN).save(new, format)
        return new.getvalue(), format.lower()

    def createSquareThumbnail(self, image, size, source=None, format=None):
        img = Image.open(StringIO(image.data))
        if not format:
            format = img.format
        format = format.upper()
        if format not in ('GIF', 'JPEG', 'PNG'):
            format = 'JPEG'
        img_width, img_height = img.size
        thu_width, thu_height = size, size
        ratio = max(img_width * 1.0 / thu_width, img_height * 1.0 / thu_height)
        if source:
            x, y, w, h = source
        else:
            geometry = IThumbnailGeometry(image)
            (x, y), (w, h) = geometry.position, geometry.size
        box = (int(x * ratio), int(y * ratio), int((x + w) * ratio), int((y + h) * ratio))
        new = StringIO()
        img.crop(box).resize((DEFAULT_DISPLAYS['cthumb'], DEFAULT_DISPLAYS['cthumb']), Image.ANTIALIAS).filter(ImageFilter.SHARPEN).save(new, format)
        return new.getvalue(), format.lower()
