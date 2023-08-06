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
from zope.annotation.interfaces import IAnnotations
from zope.location.interfaces import ISublocations

# import local interfaces
from ztfy.file.interfaces import IFilePropertiesContainer, IFilePropertiesContainerAttributes

# import Zope3 packages
from zc.set import Set
from zope.component import adapts
from zope.interface import implements

# import local packages


FILE_PROPERTIES_ANNOTATIONS_KEY = 'ztfy.file.container.attributes'

class FilePropertiesContainerAttributesAdapter(object):
    """File properties container attributes adapter"""

    adapts(IFilePropertiesContainer)
    implements(IFilePropertiesContainerAttributes)

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        attributes = annotations.get(FILE_PROPERTIES_ANNOTATIONS_KEY)
        if attributes is None:
            attributes = annotations[FILE_PROPERTIES_ANNOTATIONS_KEY] = Set()
        self.attributes = attributes


class FilePropertiesContainerSublocationsAdapter(object):
    """File properties container sub-locations adapter"""

    adapts(IFilePropertiesContainer)
    implements(ISublocations)

    def __init__(self, context):
        self.context = context

    def sublocations(self):
        return (v for v in (getattr(self.context, attr, None) for attr in IFilePropertiesContainerAttributes(self.context).attributes)
                        if v is not None)
