### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2009 Thierry Florac <tflorac AT ulthar.net>
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
from zope.annotation.interfaces import IAnnotations
from zope.location.interfaces import ISublocations

# import local interfaces
from ztfy.i18n.interfaces import I18nError, II18nManager, II18nManagerInfo, II18nAttributesAware
from ztfy.i18n.interfaces import II18nFilePropertiesContainer, II18nFilePropertiesContainerAttributes

# import Zope3 packages
from zc.set import Set
from zope.component import adapts, queryUtility
from zope.interface import implements

# import local packages
from ztfy.i18n.schema import DefaultValueDict
from ztfy.utils.request import queryRequest
from ztfy.utils.traversing import getParent

from ztfy.i18n import _


_marker = DefaultValueDict()

class I18nLanguagesAdapter(object):
    """Adapter class for II18nManager interface"""

    adapts(II18nManager)
    implements(II18nManagerInfo)

    def __init__(self, context):
        self.context = context
        self._i18n = getParent(context, II18nManager, allow_context=False)
        self._negotiator = queryUtility(INegotiatorManager)

    def _getAvailableLanguages(self):
        result = getattr(self.context, '_available_languages', _marker)
        if result is _marker:
            if self._i18n is not None:
                result = II18nManagerInfo(self._i18n).availableLanguages
            elif self._negotiator is not None:
                result = self._negotiator.offeredLanguages
            else:
                result = [u'en', ]
        return result

    def _setAvailableLanguages(self, languages):
        self.context._available_languages = languages

    availableLanguages = property(_getAvailableLanguages, _setAvailableLanguages)

    def _getDefaultLanguage(self):
        result = getattr(self.context, '_default_language', _marker)
        if result is _marker:
            if self._i18n is not None:
                result = II18nManagerInfo(self._i18n).defaultLanguage
            elif self._negotiator is not None:
                result = self._negotiator.serverLanguage
            else:
                result = u'en'
        return result

    def _setDefaultLanguage(self, language):
        self.context._default_language = language

    defaultLanguage = property(_getDefaultLanguage, _setDefaultLanguage)


class I18nAttributesAdapter(object):
    """Adapter class for II18nAttributesAware interface"""

    adapts(II18nAttributesAware)
    implements(II18n)

    def __init__(self, context):
        self.context = context
        self._i18n = getParent(context, II18nManager)
        self._negotiator = queryUtility(INegotiatorManager)

    def getDefaultLanguage(self):
        if self._i18n is not None:
            return II18nManagerInfo(self._i18n).defaultLanguage
        elif self._negotiator is not None:
            return self._negotiator.serverLanguage
        else:
            return u'en'

    def setDefaultLanguage(self, language):
        raise I18nError, _("""Default language is defined by I18nManager properties""")

    def addLanguage(self, language, *args, **kw):
        raise I18nError, _("""Use I18nManager properties to handle languages list""")

    def removeLanguage(self, language):
        raise I18nError, _("""Use I18nManager properties to handle languages list""")

    def getAvailableLanguages(self):
        if self._i18n is not None:
            return II18nManagerInfo(self._i18n).availableLanguages
        elif self._negotiator is not None:
            return self._negotiator.offeredLanguages
        else:
            return [u'en', ]

    def getPreferedLanguage(self, request=None):
        languages = self.getAvailableLanguages()
        if request is None:
            request = queryRequest()
        if (request is not None) and (self._negotiator is not None):
            return self._negotiator.getLanguage(languages, request)
        return u'en'

    def getAttribute(self, name, language=None, request=None, query=False):
        result = getattr(self.context, name, _marker)
        if not isinstance(result, DefaultValueDict):
            return result
        if language is None:
            language = self.getPreferedLanguage(request)
        if query:
            return result.get(language, _marker)
        return result.get(language, None)

    def queryAttribute(self, name, language=None, default=None, request=None):
        result = self.getAttribute(name, language, request, query=True)
        if (result is _marker) or (result is None) or (result == ''):
            language = self.getDefaultLanguage()
            result = self.getAttribute(name, language, request, query=True)
        if result is not _marker:
            return result
        return default

    def setAttribute(self, attribute, value, language=None):
        if language is None:
            language = self.getDefaultLanguage()
        current_value = getattr(self.context, attribute)
        if isinstance(current_value, DefaultValueDict):
            current_value[language] = value

    def setAttributes(self, language, **kw):
        for key in kw:
            self.setAttribute(key, kw[key], language)


I18N_FILE_PROPERTIES_ANNOTATIONS_KEY = 'ztfy.i18n.file.container.attributes'

class I18nFilePropertiesContainerAttributesAdapter(object):
    """File properties container attributes adapter"""

    adapts(II18nFilePropertiesContainer)
    implements(II18nFilePropertiesContainerAttributes)

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        attributes = annotations.get(I18N_FILE_PROPERTIES_ANNOTATIONS_KEY)
        if attributes is None:
            attributes = annotations[I18N_FILE_PROPERTIES_ANNOTATIONS_KEY] = Set()
        self.attributes = attributes


class I18nFilePropertiesContainerSublocationsAdapter(object):
    """File properties container sub-locations adapter"""

    adapts(II18nFilePropertiesContainer)
    implements(ISublocations)

    def __init__(self, context):
        self.context = context

    def sublocations(self):
        for attr in II18nFilePropertiesContainerAttributes(self.context).attributes:
            for value in (v for v in getattr(self.context, attr, {}).values() if v is not None):
                yield value
