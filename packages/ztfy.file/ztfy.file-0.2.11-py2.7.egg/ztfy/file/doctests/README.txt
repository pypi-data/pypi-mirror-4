=================
ZTFY.file package
=================

Introduction
------------

This package is a set of interfaces, classes and adapters which make
handling many files-related functions easier inside Zope3 application
server.


File fields and properties
--------------------------

You can define several file-related interfaces fields via several classes
defined in ztfy.utils.schema module:

    >>> import zope.component
    >>> import zope.interface
    >>> from zope.interface import Interface
    >>> from zope.annotation.interfaces import IAnnotations, IAttributeAnnotatable
    >>> from ztfy.file.schema import FileField, ImageField, CthumbImageField

Before anything else we have to register a set of required adapters:

    >>> from zope.annotation.attribute import AttributeAnnotations
    >>> zope.component.provideAdapter(AttributeAnnotations)
    >>> from ztfy.file.adapter import FilePropertiesContainerAttributesAdapter
    >>> zope.component.provideAdapter(FilePropertiesContainerAttributesAdapter)

This adapter is actually used to define the list of attributes handling
file-like properties ; this is required for indexing.

FileField is an interface attribute used to store data of an external file
of any content type ; ImageField is used to store images ; CthumbImageField
is used to store images for which you want to be able to select a square part
to be used as a custom thumbnail.

    >>> class IDocumentInfo(Interface):
    ...     """Declare basic document interface"""
    ...     data = FileField(title=u'Document content',
    ...                      required=False)
    ...     illustration = ImageField(title=u'Document illustration',
    ...                               required=False)
    ...     thumbnail = CthumbImageField(title=u'Document thumbnail',
    ...                                  required=False)

We can then create a class to implement file properties:

    >>> from zope.interface import implements
    >>> from ztfy.file.property import FileProperty, ImageProperty
    >>> class Document(object):
    ...     implements(IDocumentInfo, IAttributeAnnotatable)
    ...     data = FileProperty(IDocumentInfo['data'])
    ...     illustration = ImageProperty(IDocumentInfo['illustration'])
    ...     thumbnail = ImageProperty(IDocumentInfo['thumbnail'])

We can then create a document:

    >>> import os
    >>> doc = Document()
    >>> doc.data is None
    True

You can then assign value to "data" field with a string value, which will be
converted automatically to a File object, or with an already existing File
object:

    >>> datafile = os.path.join(current_dir, '..', 'doctests', 'README.txt')
    >>> data = open(datafile).read()
    >>> doc.data = data
    >>> doc.data
    <zope.app.file.file.File object at ...>
    >>> doc.data.data.startswith('=================\nZTFY.file package\n=================')
    True

Content type is determined by the python-magic library, if this one is available.
Otherwise, content type is determined by file name, so the exact content type may vary
according to availability of magic library.

When libmagic determines a "text/*" content type, which is currently not very reliable,
content-type is re-evaluated based on given filename extension via the mimetypes package.
In this case, the property data can be provided as a tuple containing the real data and
the file name:

    >>> doc.data.contentType
    'text/x-python'
    >>> doc.data = (data, 'README.txt')
    >>> doc.data
    <zope.app.file.file.File object at ...>
    >>> doc.data.data.startswith('=================\nZTFY.file package\n=================')
    True
    >>> doc.data.contentType
    'text/plain'

To access a file property from an URL, you can use the "++file++" namespace
followed by the name of the given attribute ; so "++file++data" in this
example.

Now let's use an image for another property:

    >>> imgfile = os.path.join(current_dir, '..', 'doctests', 'TFNA0908-D7.05726.jpg')
    >>> img = open(imgfile).read()
    >>> doc.illustration = img
    >>> doc.illustration
    <zope.app.file.image.Image object at ...>
    >>> doc.illustration.contentType
    'image/jpeg...'
    >>> doc.illustration.getSize()
    126239
    >>> doc.illustration.getImageSize()
    (800, 543)


Custom file class properties
----------------------------

The FileProperty and ImageProperty properties accept a specific argument,
'klass', which is the class of files and images which should be used to
manage external files ; their defaults are File and Image classes defined in
zope.app.file package.
You can define these arguments to use your own class ; for example, the
ztfy.extfile package provides an alternative implementation to store external
files outside of the ZODB (locally on the filesystem, on a remote server
via SSH, NFS... or as blobs).
The only requirement is that the given classes must implement IFile or
IImage interfaces.


Images displays
---------------

As soon as you have an image (as a content property or not), you can create
thumbnails, which are called 'displays' in the context of this package.
A thumbnailer is a utility which can create a thumbnail from a given image ;
different implementations can be created, the default one is based on PIL.
For GIF, JPEG and PNG images, thumbnails are defined in the original image
format ; otherwise, thumbnails are defined in JPEG.

Thumbnails size can be define via:
 - a width, as 'w300'
 - a height, as 'h200'
 - a box, as '300x200'
As soon as a size is given, the thumbnail is created to fit inside a box of
the given size, always keeping image's initial aspect ratio. Let's setup a
few components and adapters:

    >>> zope.interface.alsoProvides(doc.illustration, IAttributeAnnotatable)

    >>> from ztfy.file.interfaces import IThumbnailer, IImageDisplay
    >>> from ztfy.file.pil import PILThumbnailer
    >>> pil_thumbnailer = PILThumbnailer()
    >>> zope.component.provideUtility(pil_thumbnailer, IThumbnailer)
    >>> from ztfy.file.display import ImageDisplayAdapter
    >>> zope.component.provideAdapter(ImageDisplayAdapter)
    >>> adapter = IImageDisplay(doc.illustration)
    >>> adapter
    <ztfy.file.display.ImageDisplayAdapter object at ...>
    >>> adapter.getDisplaySize('w128')
    (128, 86)
    >>> adapter.getDisplaySize('h86')
    (126, 86)
    >>> adapter.getDisplaySize('128x86')
    (126, 86)

Note that because of rounded values, returned values can be slightly different
according to given input settings...

    >>> adapter.getDisplayName('w128')
    'w128'
    >>> adapter.getDisplayName('h86')
    'w126'
    >>> adapter.getDisplayName('128x86')
    'w126'
    >>> adapter.getDisplayName(width=128, height=86)
    '128x86'
    >>> display = adapter.getDisplay('w128')
    >>> display
    <zope.app.file.image.Image object at ...>
    >>> display.getImageSize()
    (128, 86)

As specified, generated thumbnails are persistents and stored inside image's
annotations:

    >>> IAnnotations(doc.illustration)['ztfy.file.display'].keys()
    ['w128']
    >>> IAnnotations(doc.illustration)['ztfy.file.display']['w128'] is display
    True

You can remove all generated displays via the "clearDisplay(display)" and
"clearDisplays()" methods:

    >>> adapter.clearDisplays()
    >>> IAnnotations(doc.illustration)['ztfy.file.display'].keys()
    []

As you may have noticed, a thumbnail is nothing more than another 'normal'
image, on which you can get other thumbnails...


Images square thumbnails
------------------------

In some cases, it can be useful to create square thumbnails based on a
selection made on the initial image ; the CthumbImageField automatically
handles selection for z3c.form based forms.
The IThumbnailGeometry interface defines position and size of this selection ;
coordinates are given in a system matching an image's thumbnail of 128 pixels
width or height (whichever is highest).
Default position and size are always defined, based on a centered selection.

    >>> from ztfy.file.display import ImageThumbnailGeometryAdapter
    >>> zope.component.provideAdapter(ImageThumbnailGeometryAdapter)
    >>> from ztfy.file.interfaces import IThumbnailGeometry
    >>> geometry = IThumbnailGeometry(doc.illustration)
    >>> geometry
    <ztfy.file.display.ImageThumbnailGeometryAdapter object at ...>
    >>> geometry.position
    (21, 0)
    >>> geometry.size
    (86, 86)
    >>> geometry.position = (0,0)
    >>> geometry.position
    (0, 0)
    >>> geometry.size = (20,20)
    >>> geometry.size
    (20, 20)

This special square thumbnail is mainly available as a specific display
called 'cthumb', which is always of 128 pixels in width and height:

    >>> display = adapter.getDisplay('cthumb')
    >>> display.getImageSize()
    (128, 128)


Getting displays via URLs
-------------------------

When a display is defined, you can get it via the "++display++" namespace ;
for example, you can use a relative URL like "++file++illustration/++display++cthumb.jpeg"
to get access to the square thumbnail associated with the illustration field
of the document specified in this sample.
