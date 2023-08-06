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
from datetime import datetime
from fanstatic import Library, Resource

# import Zope3 interfaces
from transaction.interfaces import ITransactionManager
from zope.dublincore.interfaces import IZopeDublinCore

# import local interfaces
from ztfy.extfile.interfaces import IBaseBlobFile

# import Zope3 packages
import zope.datetime

# import local packages
from ztfy.jqueryui import jquery_imgareaselect
from zope.security.proxy import removeSecurityProxy


library = Library('ztfy.file', 'resources')

ztfy_file = Resource(library, 'js/ztfy.file.js', minified='js/ztfy.file.min.js',
                     depends=[jquery_imgareaselect], bottom=True)


class FileView(object):

    def show(self):
        """This is just a refactoring of original zope.app.file.browser.file.FileView class,
        which according to me didn't handle last modification time correctly...
        """
        if self.request is not None:
            header = self.request.response.getHeader('Content-Type')
            if header is None:
                self.request.response.setHeader('Content-Type', self.context.contentType)
            self.request.response.setHeader('Content-Length', self.context.getSize())
        try:
            modified = IZopeDublinCore(self.context).modified
        except TypeError:
            modified = None
        if modified is None or not isinstance(modified, datetime):
            return self.context.data
        header = self.request.getHeader('If-Modified-Since', None)
        lmt = long(zope.datetime.time(modified.isoformat()))
        if header is not None:
            header = header.split(';')[0]
            try:
                mod_since = long(zope.datetime.time(header))
            except:
                mod_since = None
            if mod_since is not None:
                if lmt <= mod_since:
                    self.request.response.setStatus(304)
                    return ''
        self.request.response.setHeader('Last-Modified', zope.datetime.rfc1123_date(lmt))
        if IBaseBlobFile.providedBy(self.context):
            # Commit transaction to avoid uncommitted blobs error while generating display
            ITransactionManager(removeSecurityProxy(self.context)).get().commit()
            return self.context.getBlob(mode='c')
        else:
            return self.context.data
