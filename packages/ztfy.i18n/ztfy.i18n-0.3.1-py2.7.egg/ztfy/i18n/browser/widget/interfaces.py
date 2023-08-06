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
from z3c.form.interfaces import IWidget, ITextWidget, ITextAreaWidget, IFileWidget, ISelectWidget
from zope.schema import List

# import local interfaces
from ztfy.file.browser.widget.interfaces import IHTMLWidget

# import Zope3 packages

# import local packages

from ztfy.i18n import _


class ILanguageSelectWidget(ISelectWidget):
    """Language selection widget"""


class II18nWidget(IWidget):
    """I18n base widget"""

    langs = List(title=_("Languages"),
                 description=_("List of languages supported by the given widget"),
                 required=True)


class II18nTextWidget(II18nWidget, ITextWidget):
    """I18n text widget"""


class II18nTextAreaWidget(II18nWidget, ITextAreaWidget):
    """I18n textarea widget"""


class II18nHTMLWidget(II18nWidget, IHTMLWidget):
    """I18n HTML textarea widget"""


class II18nFileWidget(II18nWidget, IFileWidget):
    """I18n file widget"""


class II18nImageWidget(II18nFileWidget):
    """I18n image widget"""


class II18nCthumbImageWidget(II18nImageWidget):
    """I18n image widget with square thumb"""
