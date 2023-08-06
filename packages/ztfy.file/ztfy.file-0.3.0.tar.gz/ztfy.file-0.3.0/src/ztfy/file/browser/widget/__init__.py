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
from z3c.form.interfaces import IFieldWidget, NOT_CHANGED
from zope.schema.interfaces import IField

# import local interfaces
from ztfy.file.browser.widget.interfaces import IHTMLWidget, IHTMLWidgetSettings, IFileWidget, IImageWidget, ICthumbImageWidget
from ztfy.file.interfaces import IThumbnailGeometry, IImageDisplay
from ztfy.skin.layer import IZTFYBrowserLayer

# import Zope3 packages
from z3c.form.browser.file import FileWidget as FileWidgetBase
from z3c.form.browser.textarea import TextAreaWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter, queryMultiAdapter
from zope.interface import implementer, implementsOnly
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.file.browser import ztfy_file
from ztfy.jqueryui import jquery_fancybox, jquery_tinymce

from ztfy.file import _


MCE_OPT_PREFIX = "mce_"
MCE_OPT_PREFIX_LEN = len(MCE_OPT_PREFIX)

class HTMLWidget(TextAreaWidget):
    """HTML input widget"""

    implementsOnly(IHTMLWidget)

    cols = 80
    rows = 12

    title = _("Click textarea to activate HTML editor !")

    mce_mode = 'none'
    mce_editor_selector = 'tiny_mce'
    mce_theme = 'advanced'
    mce_plugins = 'safari,pagebreak,style,layer,table,save,advhr,advimage,advlink,emotions,iespell,inlinepopups,insertdatetime,preview,media,searchreplace,print,contextmenu,paste,directionality,fullscreen,noneditable,visualchars,nonbreaking,xhtmlxtras,template'
    mce_theme_advanced_buttons1 = 'bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,styleselect,formatselect,fontselect,fontsizeselect'
    mce_theme_advanced_buttons2 = 'cut,copy,paste,pastetext,pasteword,|,search,replace,|,bullist,numlist,|,outdent,indent,blockquote,|,undo,redo,|,link,unlink,anchor,image,cleanup,help,code,|,insertdate,inserttime,preview,|,forecolor,backcolor'
    mce_theme_advanced_buttons3 = 'tablecontrols,|,hr,removeformat,visualaid,|,sub,sup,|,charmap,emotions,iespell,media,advhr,|,print,|,ltr,rtl,|,fullscreen'
    mce_theme_advanced_buttons4 = 'insertlayer,moveforward,movebackward,absolute,|,styleprops,|,cite,abbr,acronym,del,ins,attribs,|,visualchars,nonbreaking,template,pagebreak'
    mce_theme_advanced_toolbar_location = 'top'
    mce_theme_advanced_toolbar_align = 'left'
    mce_theme_advanced_statusbar_location = 'bottom'
    mce_theme_advanced_resizing = True

    def render(self):
        jquery_tinymce.need()
        return TextAreaWidget.render(self)

    @property
    def options(self):
        options = {}
        attrs = dir(self)
        for attr in (a for a in attrs if a.startswith(MCE_OPT_PREFIX)):
            value = getattr(self, attr, None)
            value = value == True and 'true' or value == False and 'false' or value
            if value is not None:
                options[attr[MCE_OPT_PREFIX_LEN:]] = value
        adapter = queryMultiAdapter((self.field, self.form, self.request), IHTMLWidgetSettings)
        if adapter is not None:
            attrs = dir(adapter)
            for attr in (a for a in attrs if a.startswith(MCE_OPT_PREFIX)):
                value = getattr(adapter, attr, None)
                value = value == True and 'true' or value == False and 'false' or value
                if value is not None:
                    options[attr[MCE_OPT_PREFIX_LEN:]] = value
        return options

    @property
    def options_as_text(self):
        return ';'.join(('%s=%s' % (a, v) for a, v in self.options.items()))

@adapter(IField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def HTMLFieldWidget(field, request):
    """IFieldWidget factory for HTMLField"""
    return FieldWidget(field, HTMLWidget(request))


class FileWidget(FileWidgetBase):
    """File input widget"""

    implementsOnly(IFileWidget)

    downloadable = FieldProperty(IFileWidget['downloadable'])

    @property
    def current_value(self):
        if self.form.ignoreContext:
            return None
        return self.field.get(self.context)

    @property
    def deletable(self):
        if self.required:
            return False
        if self.value is NOT_CHANGED:
            return bool(self.current_value)
        else:
            return bool(self.value)

    @property
    def deleted(self):
        if self.lang:
            name, _ignore = self.name.split(':')
            return self.request.form.get(name + '_' + self.lang + '__delete', None) == 'on'
        return self.request.form.get(self.name + '__delete', None) == 'on'

@adapter(IField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def FileFieldWidget(field, request):
    """IFieldWidget factory for FileField"""
    return FieldWidget(field, FileWidget(request))


class ImageWidget(FileWidget):
    """Image input widget"""

    implementsOnly(IImageWidget)

    def render(self):
        jquery_fancybox.need()
        return super(ImageWidget, self).render()

@adapter(IField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def ImageFieldWidget(field, request):
    """IFieldWidget factory for ImageField"""
    return FieldWidget(field, ImageWidget(request))


class CthumbImageWidget(ImageWidget):
    """Image input widget with cthumb selection"""

    implementsOnly(ICthumbImageWidget)

    def render(self):
        try:
            self.widget_value = self.current_value
        except:
            self.widget_value = None
        ztfy_file.need()
        return super(CthumbImageWidget, self).render()

    @property
    def adapter(self):
        return IImageDisplay(self.widget_value, None)

    @property
    def geometry(self):
        return IThumbnailGeometry(self.widget_value, None)

    @property
    def position(self):
        if self.lang:
            name, _ignore = self.name.split(':')
            return (int(round(float(self.request.form.get(name + '_' + self.lang + '__x', 0)))),
                    int(round(float(self.request.form.get(name + '_' + self.lang + '__y', 0)))))
        return (int(round(float(self.request.form.get(self.name + '__x', 0)))),
                int(round(float(self.request.form.get(self.name + '__y', 0)))))

    @property
    def size(self):
        if self.lang:
            name, _ignore = self.name.split(':')
            return (int(round(float(self.request.form.get(name + '_' + self.lang + '__w', 0)))),
                    int(round(float(self.request.form.get(name + '_' + self.lang + '__h', 0)))))
        return (int(round(float(self.request.form.get(self.name + '__w', 0)))),
                int(round(float(self.request.form.get(self.name + '__h', 0)))))

@adapter(IField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def CthumbImageFieldWidget(field, request):
    """IFieldWidget factory for ImageField"""
    return FieldWidget(field, CthumbImageWidget(request))
