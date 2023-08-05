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
from zope.app.file.interfaces import IFile
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.schema.interfaces import IText, IBytes, IVocabularyTokenized

# import local interfaces

# import Zope3 packages
from zope.interface import Interface, Attribute
from zope.schema import TextLine, Text, Int, Choice, Tuple, Set, Object, Bytes

# import local packages

from ztfy.file import _


#
# File container interface
#

class IFilePropertiesContainer(Interface):
    """Marker interface used to define contents owning file properties"""


class IFilePropertiesContainerAttributes(Interface):
    """Interface used to list attributes handling file properties"""

    attributes = Set(title=_("File attributes"),
                     description=_("List of attributes handling file objects"),
                     required=False,
                     value_type=TextLine())


#
# File field interface
#

class IHTMLField(IText):
    """HTML field interface"""


class IFileField(IBytes):
    """File object field interface"""


class IImageField(IFileField):
    """Image file object field interface"""


class ICthumbImageField(IImageField):
    """Image file object with cthumb interface"""


#
# Extended file interface
#

class ILanguageVocabulary(IVocabularyTokenized):
    """Marker interface for file languages vocabulary"""


class IExtendedFile(IFile):
    """An IFile interface with new attributes"""

    title = TextLine(title=_("Title"),
                     description=_("Full file title"),
                     required=False)

    description = Text(title=_("Description"),
                       description=_("Full description, which can be displayed by several presentation templates"),
                       required=False)

    savename = TextLine(title=_("Save file as..."),
                        description=_("Default name under which the file can be saved"),
                        required=False)

    language = Choice(title=_("Language"),
                      description=_("File content's main language"),
                      required=False,
                      vocabulary='ZTFY languages')


#
# Image thumbnailer interface
#

class IThumbnailGeometry(Interface):
    """Base interface for IThumbnailGeometry infos"""

    position = Tuple(title=_("Thumbnail position"),
                     description=_("Position of the square thumbnail, from original image coordinates"),
                     required=False,
                     value_type=Int(),
                     min_length=2,
                     max_length=2)

    size = Tuple(title=_("Thumbnail size"),
                 description=_("Size of square thumbnail, from original image coordinates"),
                 required=False,
                 value_type=Int(),
                 min_length=2,
                 max_length=2)


class IThumbnailer(Interface):
    """A thumbnailer is a utility used to generate image thumbnails"""

    order = Attribute(_("Thumbnailer choice order"))

    def createThumbnail(self, image, size, format=None):
        """Create a thumbnail for the given image
        
        Size is given as an (w,h) tuple
        """

    def createSquareThumbnail(self, image, size, source=None, format=None):
        """Create a square thumbnail from a selection on the given image
        
        Source is given as a (x,y, w,h) tuple
        """


class ICthumbImageFieldData(Interface):
    """Cthumb image field data"""

    value = Attribute(_("Image field value"))

    geometry = Object(title=_("Value geometry"),
                      schema=IThumbnailGeometry)


#
# Image display interface
#

DEFAULT_DISPLAYS = {
                   'thumb':  128,
                   'cthumb': 128
                  }

class IImageDisplayInfo(Interface):
    """Image display interface properties"""

    def getImageSize(self):
        """Get original image size"""

    def getDisplaySize(self, display, forced=False):
        """Get size for the given display
        
        If forced is True, the display can be larger than
        the original source image.
        """

    def getDisplayName(self, display=None, width=None, height=None):
        """Get matching name for the given size or display"""

    def getDisplay(self, display, format=None):
        """Get requested display
        
        Display can be specified via :
         - a name
         - a width, with wXXX
         - a height, with hXXX
         - a size, with XXXxYYY
        """


class IImageDisplayWriter(Interface):
    """Image display writing interface"""

    def clearDisplay(self, display):
        """Clear selected display"""

    def clearDisplays(self):
        """Clear all generated displays"""


class IImageDisplay(IImageDisplayInfo, IImageDisplayWriter):
    """Marker interface for image display
    
    Displays are used to generate images thumbnails, as long
    as the requested size is smaller than the original image size
    """


class IImageTag(Interface):
    """Generate HTML <img> tags for an image or display"""

    def getTag(self, display=None, alt=None, title=None, width=None, height=None, **kw):
        """Generate HTML tag for given display"""


class IImageModifiedEvent(IObjectModifiedEvent):
    """Event fired when an image property is modified"""


#
# Archives management
#

class IArchiveExtractor(Interface):
    """Archive contents extractor"""

    def initialize(self, data, mode='r'):
        """Initialize extractor for given data"""

    def getContents(self):
        """Get list of archive contents
        
        Each result item is a tuple containing data and file name
        """
