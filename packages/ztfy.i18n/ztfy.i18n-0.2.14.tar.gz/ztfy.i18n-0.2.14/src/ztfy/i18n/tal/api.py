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
from z3c.language.negotiator.interfaces import INegotiatorManager
from z3c.language.switch.interfaces import II18n
from zope.tales.interfaces import ITALESFunctionNamespace

# import local interfaces
from ztfy.i18n.interfaces import II18nManager, II18nManagerInfo, \
                                 II18nAttributesAware
from ztfy.i18n.tal.interfaces import II18nTalesAPI

# import Zope3 packages
from zope.component import queryUtility
from zope.i18n import translate
from zope.interface import implements

# import local packages
from ztfy.utils import getParent


class I18nTalesAdapter(object):

    implements(II18nTalesAPI, ITALESFunctionNamespace)

    def __init__(self, context):
        self.context = context
        self._i18n = II18n(getParent(self.context, II18nAttributesAware), None)

    def setEngine(self, engine):
        self.request = engine.vars['request']

    def __getattr__(self, attribute):
        if self._i18n is not None:
            value = self._i18n.queryAttribute(attribute, language=self.request.get('language'), request=self.request)
        else:
            value = getattr(self.context, attribute, '')
        if value is None:
            value = ''
        return value

    def translate(self):
        return translate(self.context, context=self.request)

    def langs(self):
        if self._i18n is not None:
            default_language = self._i18n.getDefaultLanguage()
            languages = self._i18n.getAvailableLanguages()
            return sorted(languages, key=lambda x: x == default_language and '__' or x)
        i18n = getParent(self.context, II18nManager)
        if i18n is not None:
            info = II18nManagerInfo(i18n)
            default_language = info.defaultLanguage
            return sorted(info.availableLanguages, key=lambda x: x == default_language and '__' or x)
        negotiator = queryUtility(INegotiatorManager)
        if negotiator is not None:
            default_language = negotiator.serverLanguage
            return sorted(negotiator.offeredLanguages, key=lambda x: x == default_language and '__' or x)
        return (u'en',)

    def user_lang(self):
        if self._i18n is not None:
            return self._i18n.getPreferedLanguage()
        return u'en'

    def default_lang(self):
        if self._i18n is not None:
            return self._i18n.getDefaultLanguage()
        return u'en'
