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
from z3c.form.interfaces import IDataConverter, NOT_CHANGED
from z3c.language.negotiator.interfaces import INegotiatorManager

# import local interfaces
from ztfy.i18n.browser.widget.interfaces import II18nWidget
from ztfy.i18n.interfaces import II18nManager, II18nManagerInfo

# import Zope3 packages
from z3c.form.widget import Widget
from z3c.form.browser.widget import HTMLFormElement
from zope.component import queryUtility
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from zope.security.proxy import removeSecurityProxy

# import local packages
from ztfy.i18n.browser import ztfy_i18n
from ztfy.utils.traversing import getParent


class I18nWidgetProperty(object):
    """Base class for I18n widgets properties"""

    def __init__(self, name):
        self.__name = name

    def __get__(self, instance, klass):
        return instance.__dict__.get(self.__name, None)

    def __set__(self, instance, value):
        instance.__dict__[self.__name] = value
        for widget in instance.widgets.values():
            setattr(widget, self.__name, value)


class I18nWidget(HTMLFormElement, Widget):
    """Base class for all I18n widgets"""

    implements(II18nWidget)

    langs = FieldProperty(II18nWidget['langs'])
    original_widget = None

    # IHTMLCoreAttributes properties
    klass = "i18n-widget"
    style = I18nWidgetProperty('style')
    # IHTMLEventsAttributes properties
    onclick = I18nWidgetProperty('onclick')
    ondblclick = I18nWidgetProperty('ondblclick')
    onmousedown = I18nWidgetProperty('onmousedown')
    onmouseup = I18nWidgetProperty('onmouseup')
    onmouseover = I18nWidgetProperty('onmouseover')
    onmousemove = I18nWidgetProperty('onmousemove')
    onmouseout = I18nWidgetProperty('onmouseout')
    onkeypress = I18nWidgetProperty('onkeypress')
    onkeydown = I18nWidgetProperty('onkeydown')
    onkeyup = I18nWidgetProperty('onkeyup')
    # IHTMLFormElement properties
    disabled = I18nWidgetProperty('disabled')
    tabindex = I18nWidgetProperty('tabindex')
    onfocus = I18nWidgetProperty('onfocus')
    onblur = I18nWidgetProperty('onblur')
    onchange = I18nWidgetProperty('onchange')

    def update(self):
        super(I18nWidget, self).update()
        manager = getParent(self.context, II18nManager)
        if manager is not None:
            self.langs = II18nManagerInfo(manager).availableLanguages
        else:
            manager = queryUtility(INegotiatorManager)
            if manager is not None:
                self.langs = manager.offeredLanguages
            else:
                self.langs = ['en', ]
        self.widgets = {}
        for lang in self.langs:
            widget = self.widgets[lang] = self.original_widget(self.request)
            self.initWidget(widget, lang)
        for lang in self.langs:
            widget = self.widgets[lang]
            self.updateWidget(widget, lang)
            widget.update()

    def initWidget(self, widget, language):
        widget.id = str('%s.%s' % (self.name, language))
        widget.form = self.form
        widget.mode = self.mode
        widget.ignoreContext = self.ignoreContext
        widget.ignoreRequest = self.ignoreRequest
        widget.field = self.field.value_type
        widget.name = str('%s:list' % self.name)
        widget.label = self.label
        widget.lang = language

    def updateWidget(self, widget, language):
        widget.value = self.getValue(language)

    def getWidget(self, language):
        widget = self.widgets[language]
        return widget.render()

    def getValue(self, language):
        self.value = removeSecurityProxy(self.value)
        if not isinstance(self.value, dict):
            converter = IDataConverter(self)
            try:
                self.value = converter.toFieldValue(self.value)
            except:
                self.value = {}
        return self.value.get(language)

    def hasValue(self, language):
        return bool(self.getValue(language))

    def render(self):
        ztfy_i18n.need()
        return super(I18nWidget, self).render()
