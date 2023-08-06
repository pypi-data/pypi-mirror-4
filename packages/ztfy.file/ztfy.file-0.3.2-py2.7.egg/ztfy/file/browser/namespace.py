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
from zope.traversing.interfaces import TraversalError

# import local interfaces
from ztfy.file.interfaces import IImageDisplay

# import Zope3 packages
from zope.traversing import namespace

# import local packages


class FilePropertyTraverser(namespace.attr):
    """Simple file property traverser"""

    def traverse(self, name, ignored):
        if '.' in name:
            name = name.split('.', 1)[0]
        result = getattr(self.context, name)
        if not IFile.providedBy(result):
            raise TraversalError("++file++%s" % name)
        return result


class DisplayPropertyTraverser(namespace.attr):
    """Image display property traverser"""

    def traverse(self, name, ignored):
        display = IImageDisplay(self.context, None)
        if display is None:
            raise TraversalError("++display++%s" % name)
        if '.' in name:
            name, format = name.split('.', 1)
        else:
            format = None
        return display.getDisplay(name, format)
