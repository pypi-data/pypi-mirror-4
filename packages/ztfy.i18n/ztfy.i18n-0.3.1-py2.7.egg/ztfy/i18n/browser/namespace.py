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
from z3c.language.switch.interfaces import II18n
from zope.traversing.interfaces import TraversalError
from zope.app.file.interfaces import IFile

# import local interfaces

# import Zope3 packages
from zope.traversing import namespace

# import local packages


class I18nFilePropertyTraverser(namespace.view):
    """Simple file property traverser"""

    def traverse(self, name, ignored):
        if '.' in name:
            name = name.split('.', 1)[0]
        if ':' in name:
            name, lang = name.split(':')
            result = II18n(self.context).getAttribute(name, language=lang)
        else:
            result = II18n(self.context).queryAttribute(name, request=self.request)
        if not IFile.providedBy(result):
            raise TraversalError("++i18n++%s" % name)
        return result
