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
from z3c.form.interfaces import IFieldWidget

# import local interfaces
from ztfy.i18n.browser.widget.interfaces import ILanguageSelectWidget
from ztfy.i18n.interfaces import ILanguageField
from ztfy.skin.layer import IZTFYBrowserLayer

# import Zope3 packages
from z3c.form.widget import FieldWidget
from z3c.form.browser import widget
from z3c.form.browser.select import SelectWidget
from zope.component import adapter
from zope.i18n import translate
from zope.interface import implements, implementer

# import local packages

from ztfy.i18n import _


class LanguageSelectWidget(SelectWidget):

    implements(ILanguageSelectWidget)

    noValueMessage = _("(no selected language)")

    @property
    def items(self):
        """See z3c.form.interfaces.IWidget."""
        items = []
        if (not self.required or self.prompt) and self.multiple is None:
            message = self.noValueMessage
            if self.prompt:
                message = self.promptMessage
            items.append({
                'id': self.id + '-novalue',
                'value': self.noValueToken,
                'content': message,
                'selected': self.value == []
            })
        for index, term in enumerate(sorted(self.terms, key=lambda x: translate(x.title, context=self.request))):
            selected = self.isSelected(term)
            id = '%s-%i' % (self.id, index)
            content = translate(term.title, context=self.request, default=term.title)
            items.append({'id':id, 'value':term.token, 'content':content, 'selected':selected})
        return items


@adapter(ILanguageField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def LanguageSelectFieldWidget(field, request):
    return FieldWidget(field, LanguageSelectWidget(request))
