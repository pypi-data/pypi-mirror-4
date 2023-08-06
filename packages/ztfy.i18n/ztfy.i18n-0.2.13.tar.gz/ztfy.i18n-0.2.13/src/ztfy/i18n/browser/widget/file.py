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
from ztfy.i18n.browser.widget.interfaces import II18nFileWidget
from ztfy.i18n.interfaces import II18nFileField
from ztfy.skin.layer import IZTFYBrowserLayer

# import Zope3 packages
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer, implementsOnly

# import local packages
from ztfy.file.browser.widget import FileWidget
from ztfy.i18n.browser.widget.widget import I18nWidget, I18nWidgetProperty


class I18nFileWidget(I18nWidget, FileWidget):
    """I18n text input type implementation"""
    implementsOnly(II18nFileWidget)

    original_widget = FileWidget

    headers = I18nWidgetProperty('headers')
    filename = I18nWidgetProperty('filename')

    @property
    def current_value(self):
        if self.form.ignoreContext:
            return {}
        return self.field.get(self.context)

    def hasValue(self, language):
        value = self.getValue(language)
        if value is NOT_CHANGED:
            return bool(self.current_value.get(language))
        else:
            return bool(value)

    def deletable(self, language):
        if self.required:
            return False
        return self.hasValue(language)


@adapter(II18nFileField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def I18nFileFieldWidget(field, request):
    """IFieldWidget factory for I18nFileWidget"""
    return FieldWidget(field, I18nFileWidget(request))
