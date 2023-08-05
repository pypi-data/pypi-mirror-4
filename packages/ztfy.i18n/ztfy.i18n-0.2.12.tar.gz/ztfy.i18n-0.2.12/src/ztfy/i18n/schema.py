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
from zope.schema.interfaces import RequiredMissing

# import local interfaces
import ztfy.i18n.interfaces

# import Zope3 packages
from zope.interface import implements
from zope.schema import Dict, TextLine, Text, Choice

# import local packages
from ztfy.file.schema import FileField, ImageField, CthumbImageField


class Language(Choice):
    """A custom language selector field"""

    implements(ztfy.i18n.interfaces.ILanguageField)

    def __init__(self, *args, **kw):
        super(Language, self).__init__(vocabulary='ZTFY languages', *args, **kw)


_marker = dict()

class DefaultValueDict(dict):
    """A custom dictionnary handling a default value"""

    implements(ztfy.i18n.interfaces.IDefaultValueDict)

    def __init__(self, default=None, *args, **kw):
        super(DefaultValueDict, self).__init__(*args, **kw)
        self._default = default

    def __delitem__(self, key):
        super(DefaultValueDict, self).__delitem__(key)
        self._p_changed = True

    def __setitem__(self, key, value):
        super(DefaultValueDict, self).__setitem__(key, value)
        self._p_changed = True

    def __missing__(self, key):
        return self._default

    def clear(self):
        super(DefaultValueDict, self).clear()
        self._p_changed = True

    def update(self, b):
        super(DefaultValueDict, self).update(b)
        self._p_changed = True

    def setdefault(self, key, failobj=None):
        if not self.has_key(key):
            self._p_changed = True
        return super(DefaultValueDict, self).setdefault(key, failobj)

    def pop(self, key, *args):
        self._p_changed = True
        return super(DefaultValueDict, self).pop(key, *args)

    def popitem(self):
        self._p_changed = True
        return super(DefaultValueDict, self).popitem()

    def get(self, key, default=None):
        result = super(DefaultValueDict, self).get(key, _marker)
        if result is _marker:
            if default is not None:
                result = default
            else:
                result = self._default
        return result

    def copy(self):
        result = DefaultValueDict(default=self._default, **self)
        return result


class I18nField(Dict):
    """Base class for I18n schema fields
    
    A I18n field is a mapping object for which keys are languages and values are
    effective values of the given attribute.
    Selected values can be returned selectively (for editing), or automatically
    (to be displayed in an HTML page) based on user's browser's language settings
    """

    implements(ztfy.i18n.interfaces.II18nField)

    def __init__(self, default_language=None, key_type=None, value_type=None, default=None, **kw):
        super(I18nField, self).__init__(key_type=TextLine(), value_type=value_type, default=DefaultValueDict(default), **kw)
        self._default_language = default_language

    def _validate(self, value):
        super(I18nField, self)._validate(value)
        if self.required:
            if self.default:
                return
            if not value:
                raise RequiredMissing
            for lang in value.values():
                if lang:
                    return
            raise RequiredMissing


class I18nTextLine(I18nField):
    """Schema field used to define an I18n textline property"""

    implements(ztfy.i18n.interfaces.II18nTextLineField)

    def __init__(self, key_type=None, value_type=None,
                 value_constraint=None, value_min_length=0, value_max_length=None, **kw):
        super(I18nTextLine, self).__init__(value_type=TextLine(constraint=value_constraint,
                                                               min_length=value_min_length,
                                                               max_length=value_max_length,
                                                               required=False), **kw)


class I18nText(I18nField):
    """Schema field used to define an I18n text property"""

    implements(ztfy.i18n.interfaces.II18nTextField)

    def __init__(self, key_type=None, value_type=None,
                 value_constraint=None, value_min_length=0, value_max_length=None, **kw):
        super(I18nText, self).__init__(value_type=Text(constraint=value_constraint,
                                                       min_length=value_min_length,
                                                       max_length=value_max_length,
                                                       required=False), **kw)


class I18nHTML(I18nText):
    """Schema field used to define an I18n HTML text property"""

    implements(ztfy.i18n.interfaces.II18nHTMLField)


class I18nFile(I18nField):
    """Schema field used to define an I18n file property
    
    I18n files are used when a single file should be provided in several
    languages. For example, you can publish articles in your own language, but
    with a set of PDF summaries available in several languages
    """

    implements(ztfy.i18n.interfaces.II18nFileField)

    def __init__(self, key_type=None, value_type=None,
                 value_constraint=None, value_min_length=0, value_max_length=None, **kw):
        super(I18nFile, self).__init__(value_type=FileField(constraint=value_constraint,
                                                            min_length=value_min_length,
                                                            max_length=value_max_length,
                                                            required=False), **kw)

    def _validate(self, value):
        return


class I18nImage(I18nFile):
    """Schema field used to define an I18n image property"""

    implements(ztfy.i18n.interfaces.II18nImageField)

    def __init__(self, key_type=None, value_type=None,
                 value_constraint=None, value_min_length=0, value_max_length=None, **kw):
        super(I18nFile, self).__init__(value_type=ImageField(constraint=value_constraint,
                                                             min_length=value_min_length,
                                                             max_length=value_max_length,
                                                             required=False), **kw)


class I18nCthumbImage(I18nImage):
    """Schema field used to define an I18n image property handling square thumbnails"""

    implements(ztfy.i18n.interfaces.II18nCthumbImageField)

    def __init__(self, key_type=None, value_type=None,
                 value_constraint=None, value_min_length=0, value_max_length=None, **kw):
        super(I18nFile, self).__init__(value_type=CthumbImageField(constraint=value_constraint,
                                                                   min_length=value_min_length,
                                                                   max_length=value_max_length,
                                                                   required=False), **kw)
