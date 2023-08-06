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
from ztfy.i18n.browser.widget.interfaces import II18nTextAreaWidget
from ztfy.i18n.interfaces import II18nTextField
from ztfy.skin.layer import IZTFYBrowserLayer

# import Zope3 packages
from z3c.form.browser.textarea import TextAreaWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementsOnly, implementer

# import local packages
from ztfy.i18n.browser.widget.widget import I18nWidget, I18nWidgetProperty


class I18nTextAreaWidget(I18nWidget, TextAreaWidget):
    """I18n text input type implementation"""
    implementsOnly(II18nTextAreaWidget)

    original_widget = TextAreaWidget

    rows = I18nWidgetProperty('rows')
    cols = I18nWidgetProperty('cols')
    readonly = I18nWidgetProperty('readonly')
    onselect = I18nWidgetProperty('onselect')


@adapter(II18nTextField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def I18nTextAreaFieldWidget(field, request):
    """IFieldWidget factory for I18nTextWidget"""
    return FieldWidget(field, I18nTextAreaWidget(request))
