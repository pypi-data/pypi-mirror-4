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
from z3c.language.switch.interfaces import IAvailableLanguagesVocabulary
from zope.schema.interfaces import IVocabularyFactory

# import local interfaces
from ztfy.i18n.interfaces import II18nManager, II18nManagerInfo

# import Zope3 packages
from zope.component import queryUtility
from zope.interface import implements, classProvides
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

# import local packages
from ztfy.utils import getParent


class I18nLanguagesVocabulary(SimpleVocabulary):
    """A vocabulary of available languages in a given context
    
    Available languages are searched for in this order :
     - look for the first I18nManager parent
     - look for I18n negociator utility
     - fallback to 'en'
    """

    implements(IAvailableLanguagesVocabulary)
    classProvides(IVocabularyFactory)

    def __init__(self, context):
        langs = []
        terms = []
        parent = getParent(context, II18nManager, allow_context=False)
        if parent is not None:
            info = II18nManagerInfo(parent, None)
            if info is not None:
                langs = info.availableLanguages
        if not langs:
            negotiator = queryUtility(INegotiatorManager)
            if negotiator is not None:
                langs = negotiator.offeredLanguages
        for lang in langs:
            terms.append(SimpleTerm(lang))
        terms.sort()
        super(I18nLanguagesVocabulary, self).__init__(terms)
