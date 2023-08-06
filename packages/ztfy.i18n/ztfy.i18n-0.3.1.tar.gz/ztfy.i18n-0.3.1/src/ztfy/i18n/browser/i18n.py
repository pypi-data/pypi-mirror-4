### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
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

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces
from z3c.language.session.interfaces import ILanguageSession

# import local interfaces

# import Zope3 packages
from zope.publisher.browser import BrowserView
from zope.traversing.browser import absoluteURL

# import local packages


class I18nLanguageView(BrowserView):

    def setLanguage(self):
        lang = self.request.form.get('language')
        if lang:
            ILanguageSession(self.request).setLanguage(lang)
        self.request.response.redirect(absoluteURL(self.context, self.request))
