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

# import local interfaces
from ztfy.i18n.interfaces import II18nManagerInfo

# import Zope3 packages
from z3c.form import form, field, button

# import local packages
from zope.traversing.browser import absoluteURL

from ztfy.i18n import _


class I18nManagerEditForm(form.EditForm):
    """Edit form for I18nManagerInfo properties"""
    form.extends(form.EditForm)
    fields = field.Fields(II18nManagerInfo)

    @button.buttonAndHandler(_("Cancel"), name="cancel")
    def handleCancel(self, action):
        self.request.response.redirect('%s/@@manageLanguages.html' % absoluteURL(self.context,self.request))
