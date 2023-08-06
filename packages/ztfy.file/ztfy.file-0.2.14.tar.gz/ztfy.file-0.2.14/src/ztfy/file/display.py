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
from persistent import Persistent
from persistent.dict import PersistentDict
from PIL import Image as PIL_Image

# import Zope3 interfaces
from zope.annotation.interfaces import IAnnotations
from zope.app.file.interfaces import IImage
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

# import local interfaces
from ztfy.file.interfaces import DEFAULT_DISPLAYS
from ztfy.file.interfaces import IImageDisplay, IThumbnailGeometry, IThumbnailer, IImageModifiedEvent

# import Zope3 packages
from zope.app.file import Image
from zope.component import adapter, adapts, queryUtility, getAllUtilitiesRegisteredFor
from zope.event import notify
from zope.interface import implements
from zope.lifecycleevent import ObjectCreatedEvent, ObjectRemovedEvent
from zope.location import locate

# import local packages
try:
    from ztfy.extfile.blob import BlobImage
except:
    BlobImage = Image


IMAGE_DISPLAY_ANNOTATIONS_KEY = 'ztfy.file.display'

class ImageDisplayAdapter(object):
    """IImageDisplay adapter"""

    adapts(IImage)
    implements(IImageDisplay)

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        displays = annotations.get(IMAGE_DISPLAY_ANNOTATIONS_KEY)
        if displays is None:
            displays = annotations[IMAGE_DISPLAY_ANNOTATIONS_KEY] = PersistentDict()
        self.displays = displays

    @property
    def image(self):
        return self.context

    def getImageSize(self):
        width, height = self.context.getImageSize()
        if (width < 0) or (height < 0):
            # Not a web format => try to use PIL to get image size
            pil_image = PIL_Image.open(StringIO(self.context.data))
            width, height = pil_image.size
        return (width, height)

    def getDisplaySize(self, display, forced=False):
        if display == 'cthumb':
            return (DEFAULT_DISPLAYS[display], DEFAULT_DISPLAYS[display])
        width, height = self.getImageSize()
        if display in DEFAULT_DISPLAYS:
            h = w = DEFAULT_DISPLAYS[display]
            w_ratio = 1.0 * width / w
            h_ratio = 1.0 * height / h
        elif display.lower().startswith('w'):
            w = int(display[1:])
            w_ratio = 1.0 * width / w
            h_ratio = 0.0
        elif display.lower().startswith('h'):
            h = int(display[1:])
            h_ratio = 1.0 * height / h
            w_ratio = 0.0
        else:
            w, h = tuple([int(x) for x in display.split('x')])
            w_ratio = 1.0 * width / w
            h_ratio = 1.0 * height / h
        if forced:
            ratio = max(w_ratio, h_ratio)
        else:
            ratio = max(1.0, w_ratio, h_ratio)
        return (int(width / ratio), int(height / ratio))

    def getDisplayName(self, display=None, width=None, height=None):
        if display:
            if display == 'cthumb':
                return display
            return 'w%d' % self.getDisplaySize(display)[0]
        return '%dx%d' % (width, height)

    def createDisplay(self, display, format=None):
        # check if display is already here
        display = self.getDisplayName(display)
        if display in self.displays:
            return self.displays[display]
        # check display size with original image size
        width, height = self.getDisplaySize(display)
        if (width, height) == self.getImageSize():
            return self.image
        # look for thumbnailer
        thumbnailer = queryUtility(IThumbnailer)
        if thumbnailer is None:
            thumbnailers = sorted(getAllUtilitiesRegisteredFor(IThumbnailer), key=lambda x: x.order)
            if thumbnailers:
                thumbnailer = thumbnailers[0]
        # generate thumbnail
        if thumbnailer is not None:
            if display == 'cthumb':
                thumbnail = thumbnailer.createSquareThumbnail(self.image, DEFAULT_DISPLAYS[display], format=format)
            else:
                thumbnail = thumbnailer.createThumbnail(self.image, (width, height), format=format)
            if isinstance(thumbnail, tuple):
                thumbnail, format = thumbnail
            else:
                format = 'jpeg'
            if (width > 256) or (height > 256):
                img_factory = BlobImage
            else:
                img_factory = Image
            img = self.displays[display] = img_factory(thumbnail)
            notify(ObjectCreatedEvent(img))
            locate(img, self.context, '++display++%s.%s' % (display, format))
            return img
        return self.image

    def getDisplay(self, display, format=None):
        if '.' in display:
            display, format = display.split('.', 1)
        if display in self.displays:
            return self.displays[display]
        return self.createDisplay(display, format)

    def clearDisplay(self, display):
        if display in self.displays:
            img = self.displays[display]
            notify(ObjectRemovedEvent(img))
            del self.displays[display]

    def clearDisplays(self):
        [self.clearDisplay(display) for display in self.displays.keys()]


IMAGE_THUMBNAIL_ANNOTATIONS_KEY = 'ztfy.file.thumbnail'

class ThumbnailGeometry(Persistent):

    implements(IThumbnailGeometry)

    position = (None, None)
    size = (None, None)

    def __init__(self, position=None, size=None):
        if position is not None:
            self.position = position
        if size is not None:
            self.size = size


class ImageThumbnailGeometryAdapter(object):
    """ISquareThumbnail adapter"""

    adapts(IImage)
    implements(IThumbnailGeometry)

    def __init__(self, context):
        self.image = context
        annotations = IAnnotations(context)
        geometry = annotations.get(IMAGE_THUMBNAIL_ANNOTATIONS_KEY)
        if geometry is None:
            geometry = annotations[IMAGE_THUMBNAIL_ANNOTATIONS_KEY] = ThumbnailGeometry()
            self._getGeometry(geometry)
        self.geometry = geometry

    def _getGeometry(self, geometry):
        w, h = IImageDisplay(self.image).getDisplaySize('thumb')
        size = min(w, h)
        geometry.size = (size, size)
        if w > h:
            geometry.position = (int((w - size) / 2), 0)
        else:
            geometry.position = (0, int((h - size) / 2))

    def _getPosition(self):
        return self.geometry.position

    def _setPosition(self, value):
        if value != self.geometry.position:
            self.geometry.position = value
            IImageDisplay(self.image).clearDisplay('cthumb')

    position = property(_getPosition, _setPosition)

    def _getSize(self):
        return self.geometry.size

    def _setSize(self, value):
        if value != self.geometry.size:
            self.geometry.size = value
            IImageDisplay(self.image).clearDisplay('cthumb')

    size = property(_getSize, _setSize)


@adapter(IImage, IImageModifiedEvent)
def handleModifiedImage(image, event):
    IImageDisplay(image).clearDisplays()


@adapter(IImage, IObjectModifiedEvent)
def handleModifiedImageData(image, event):
    if 'data' in event.descriptions[0].attributes:
        IImageDisplay(image).clearDisplays()
