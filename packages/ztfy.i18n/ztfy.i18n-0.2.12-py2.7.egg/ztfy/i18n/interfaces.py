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
from zope.schema.interfaces import IDict, IChoice

# import local interfaces

# import Zope3 packages
from zope.interface import Interface, invariant, Invalid
from zope.schema import TextLine, List, Choice, Set

# import local packages

from ztfy.i18n import _


#
# I18n dict utility interface
#

class IDefaultValueDictReader(Interface):
    """Default value dict reading methods"""

    def __missing__(key):
        """Get default value when specified key is missing from dict"""

    def get(key, default=None):
        """Get given key from dict, or default if key is missing"""

    def keys():
        """Get dict keys"""

    def values():
        """Get dict values"""

    def items():
        """Get dict items"""

    def copy():
        """Return an exact copy of the given dict, including default value"""


class IDefaultValueDictWriter(Interface):
    """Default value dict writing methods"""

    def __delitem__(key):
        """Delete specified key from dict"""

    def __setitem__(key, value):
        """Set specified key with specified value"""

    def clear():
        """Remove all dict values"""

    def update(b):
        """Update dict with values from specified dict"""

    def setdefault(key, failobj=None):
        """Get given key from dict or set it with specified value"""

    def pop(key, *args):
        """Remove given key from dict and return its value"""

    def popitem():
        """Pop last item from dict"""


class IDefaultValueDict(IDefaultValueDictReader, IDefaultValueDictWriter):
    """Default value dict marker interface"""


#
# I18nFile container interface
#

class II18nFilePropertiesContainer(Interface):
    """Marker interface used to define contents owning i18n file properties"""


class II18nFilePropertiesContainerAttributes(Interface):
    """Interface used to list attributes handling file properties"""

    attributes = Set(title=_("File attributes"),
                     description=_("List of attributes handling I18n file objects"),
                     required=False,
                     value_type=TextLine())


#
# Define I18n fields interfaces
#

class ILanguageField(IChoice):
    """Marker interface used to identify I18n language field"""


class II18nField(IDict):
    """Marker interface used to identify I18n properties"""


class II18nTextLineField(II18nField):
    """Marker interface used to identify I18n textline properties"""


class II18nTextField(II18nField):
    """Marker interface used to identify I18n text properties"""


class II18nHTMLField(II18nField):
    """Marker interface used to identify I18n HTML properties"""


class II18nFileField(II18nField):
    """Marker interface used to identify schema fields holding I18n files"""


class II18nImageField(II18nFileField):
    """Marker interface used to identify schema fields holding I18n images"""


class II18nCthumbImageField(II18nImageField):
    """Marker interface used to identify schema fields holding I18n images with square thumbnails"""


#
# Define I18n languages management interfaces
#

class I18nError(Exception):
    """This exception is raised when errors occurs during I18n operations"""


class II18nManagerInfo(Interface):
    """This interface is used to define available languages
    
    Available languages is a subset of languages provided by language negociator.
    If no negociator is registered, selection fallbacks to 'en'
    """

    availableLanguages = List(title=_("Available languages"),
                              description=_("List of languages available to translate contents properties"),
                              required=True,
                              value_type=Choice(vocabulary="ZTFY I18n languages"))

    defaultLanguage = Choice(title=_("Default language"),
                             description=_("Default language used to display context ; required fields only apply to default language"),
                             required=True,
                             vocabulary="ZTFY I18n languages")

    @invariant
    def defaultInLanguages(self):
        if self.defaultLanguage not in self.availableLanguages:
            raise Invalid(_("Default language '%(language)s' must be included in the list of available languages") % { 'language': self.defaultLanguage })


class II18nManager(Interface):
    """Marker interface used to identify I18n managers"""


class II18nAttributesAware(Interface):
    """Marker interface used to identify contents with I18n attributes"""
