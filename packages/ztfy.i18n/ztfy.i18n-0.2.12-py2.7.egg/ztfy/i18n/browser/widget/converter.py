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
from z3c.form.interfaces import IWidget, NOT_CHANGED
from z3c.language.switch.interfaces import II18n

# import local interfaces
from ztfy.i18n.interfaces import II18nField, II18nFileField

# import Zope3 packages
from z3c.form.converter import BaseDataConverter, FieldWidgetDataConverter
from zope.component import adapts

# import local packages


class I18nFieldDataConverter(BaseDataConverter):
    """Base data converter for I18n fields"""

    adapts(II18nField, IWidget)

    def toWidgetValue(self, value):
        return value

    def toFieldValue(self, value):
        result = {}
        langs = self.widget.langs
        for index, lang in enumerate(langs):
            converter = FieldWidgetDataConverter(self.widget.widgets[lang])
            result[lang] = converter.toFieldValue(value[index])
        return result


class I18nFileFieldDataConverter(I18nFieldDataConverter):
    """File data converter for I18n fields"""

    adapts(II18nFileField, IWidget)

    def toFieldValue(self, value):
        result = {}
        langs = self.widget.langs
        for index, lang in enumerate(langs):
            widget = self.widget.widgets[lang]
            if widget.deleted:
                result[lang] = None
            else:
                converter = FieldWidgetDataConverter(widget)
                field_value = converter.toFieldValue(value[index])
                if isinstance(field_value, tuple) and (field_value[0] is NOT_CHANGED):
                    field_value = field_value[0]
                if field_value:
                    result[lang] = field_value
                elif not widget.ignoreContext:
                    result[lang] = II18n(self.widget.context).getAttribute(self.widget.field.getName(), language=lang)
                else:
                    result[lang] = None
        return result
