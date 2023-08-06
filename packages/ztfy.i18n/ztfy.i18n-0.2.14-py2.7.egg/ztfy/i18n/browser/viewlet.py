### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2013 Thierry Florac <tflorac AT ulthar.net>
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
from z3c.language.switch.interfaces import II18n

# import local interfaces

# import Zope3 packages

# import local packages
from ztfy.skin.viewlets.header.title import TitleViewlet


class I18nTitleViewlet(TitleViewlet):
    """I18n title viewlet"""

    @property
    def title(self):
        try:
            title = self.__parent__.title
        except AttributeError:
            title = II18n(self.context, None).queryAttribute('title', request=self.request)
        return title
