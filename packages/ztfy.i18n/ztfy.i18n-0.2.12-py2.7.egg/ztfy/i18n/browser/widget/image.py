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

# import local interfaces
from ztfy.file.interfaces import IThumbnailGeometry, IImageDisplay, ICthumbImageFieldData
from ztfy.i18n.browser.widget.interfaces import II18nImageWidget, II18nCthumbImageWidget
from ztfy.i18n.interfaces import II18nImageField, II18nCthumbImageField
from ztfy.skin.layer import IZTFYBrowserLayer

# import Zope3 packages
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer, implementsOnly

# import local packages
from ztfy.i18n.browser.widget.file import I18nFileWidget
from ztfy.file.browser import ztfy_file_cthumb
from ztfy.file.browser.widget import ImageWidget, CthumbImageWidget


class I18nImageWidget(I18nFileWidget):
    """I18n image input type implementation"""
    implementsOnly(II18nImageWidget)

    original_widget = ImageWidget


class I18nCthumbImageWidget(I18nImageWidget):
    """I18n image input with square thumbnails implementation"""
    implementsOnly(II18nCthumbImageWidget)

    original_widget = CthumbImageWidget

    def update(self):
        super(I18nCthumbImageWidget, self).update()
        self.widget_value = self.field.get(self.context)

    def render(self):
        ztfy_file_cthumb.need()
        return super(I18nCthumbImageWidget, self).render()

    def getAdapter(self, lang):
        return IImageDisplay(self.widget_value.get(lang), None)

    def getGeometry(self, lang):
        return IThumbnailGeometry(self.widget_value.get(lang), None)

    def getPosition(self, lang):
        name, _ignore = self.name.split(':')
        return (int(self.request.form.get(name + '_' + lang + '__x', 0)),
                int(self.request.form.get(name + '_' + lang + '__y', 0)))

    def getSize(self, lang):
        name, _ignore = self.name.split(':')
        return (int(self.request.form.get(name + '_' + lang + '__w', 0)),
                int(self.request.form.get(name + '_' + lang + '__h', 0)))

    def hasValue(self, language):
        value = self.getValue(language)
        if ICthumbImageFieldData.providedBy(value):
            value = value.value
        if value is NOT_CHANGED:
            return bool(self.current_value.get(language))
        else:
            return bool(value)


@adapter(II18nImageField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def I18nImageFieldWidget(field, request):
    """IFieldWidget factory for I18nImageWidget"""
    return FieldWidget(field, I18nImageWidget(request))


@adapter(II18nCthumbImageField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def I18nCthumbImageFieldWidget(field, request):
    """IFieldWidget factory for I18nCthumbImageWidget"""
    return FieldWidget(field, I18nCthumbImageWidget(request))
