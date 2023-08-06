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
from z3c.form.interfaces import ITextAreaWidget, IFileWidget as IFileWidgetBase

# import local interfaces
from ztfy.file.interfaces import IThumbnailGeometry

# import Zope3 packages
from zope.interface import Interface
from zope.schema import Bool, Dict, Text, TextLine

# import local packages

from ztfy.file import _


class IHTMLWidgetSettings(Interface):
    """HTML widget styling interface"""

    plugins = TextLine(title=_("TinyMCE plugins"),
                       readonly=True)

    style_formats = Text(title=_("TinyMCE style_formats setting"),
                         readonly=True)

    invalid_elements = TextLine(title=_("TinyMCE invalid_elements setting"),
                                readonly=True)


class IHTMLWidget(ITextAreaWidget):
    """IHTMLField widget"""

    options = Dict(title=_("TinyMCE editor options"),
                       readonly=True)

    options_as_text = Text(title=_("String output of TinyMCE editor options"),
                           readonly=True)


class IFileWidget(IFileWidgetBase):
    """IFile base widget"""

    downloadable = Bool(title=_("Content can be downloaded ?"),
                        description=_("It True, current file content can be downloaded"),
                        required=True,
                        default=True)

    deletable = Bool(title=_("Content can be deleted ?"),
                     description=_("If True, current file content can be deleted"),
                     required=True,
                     readonly=True,
                     default=False)

    deleted = Bool(title=_("Content is deleted ?"),
                   description=_("If True, we ask for content to be deleted..."),
                   required=True,
                   readonly=True,
                   default=False)


class IImageWidget(IFileWidget):
    """IImage base widget"""


class ICthumbImageWidget(IImageWidget, IThumbnailGeometry):
    """IImage widget with cthumb selection"""
