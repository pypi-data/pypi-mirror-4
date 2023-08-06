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
from z3c.form.interfaces import IFieldWidget

# import local interfaces
from ztfy.i18n.browser.widget.interfaces import II18nTextWidget
from ztfy.i18n.interfaces import II18nTextLineField
from ztfy.skin.layer import IZTFYBrowserLayer

# import Zope3 packages
from z3c.form.widget import FieldWidget
from z3c.form.browser.text import TextWidget
from zope.component import adapter
from zope.interface import implementsOnly, implementer

# import local packages
from ztfy.i18n.browser.widget.widget import I18nWidget, I18nWidgetProperty


class I18nTextWidget(I18nWidget, TextWidget):
    """I18n text input type implementation"""
    implementsOnly(II18nTextWidget)

    original_widget = TextWidget

    maxlength = I18nWidgetProperty('maxlength')
    size = I18nWidgetProperty('size')

    def updateWidget(self, widget, language):
        super(I18nTextWidget, self).updateWidget(widget, language)
        widget.maxlength = widget.field.max_length


@adapter(II18nTextLineField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def I18nTextFieldWidget(field, request):
    """IFieldWidget factory for I18nTextWidget"""
    return FieldWidget(field, I18nTextWidget(request))
