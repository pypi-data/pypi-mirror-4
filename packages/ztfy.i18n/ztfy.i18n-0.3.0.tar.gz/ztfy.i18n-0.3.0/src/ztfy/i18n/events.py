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
from zope.catalog.interfaces import ICatalog
from zope.lifecycleevent.interfaces import IObjectCopiedEvent, IObjectAddedEvent, IObjectRemovedEvent

# import local interfaces
from ztfy.i18n.interfaces import II18nFilePropertiesContainer, II18nFilePropertiesContainerAttributes

# import Zope3 packages
from ZODB.blob import Blob
from zope.lifecycleevent import ObjectRemovedEvent
from zope.component import adapter, getUtilitiesFor
from zope.event import notify
from zope.location import locate

# import local packages
from ztfy.extfile.blob import BaseBlobFile
from ztfy.utils import catalog


@adapter(II18nFilePropertiesContainer, IObjectAddedEvent)
def handleAddedI18nFilePropertiesContainer(object, event):
    # When a file properties container is added, we must index it's attributes
    if not hasattr(object, '_v_copied_file'):
        return
    for _name, catalog_util in getUtilitiesFor(ICatalog):
        for attr in II18nFilePropertiesContainerAttributes(object).attributes:
            for value in getattr(object, attr, {}).values():
                if value is not None:
                    locate(value, object, value.__name__)
                    catalog.indexObject(value, catalog_util)
    delattr(object, '_v_copied_file')


@adapter(II18nFilePropertiesContainer, IObjectRemovedEvent)
def handleRemovedI18nFilePropertiesContainer(object, event):
    # When a file properties container is removed, we must unindex it's attributes
    for _name, catalog_util in getUtilitiesFor(ICatalog):
        for attr in II18nFilePropertiesContainerAttributes(object).attributes:
            for value in getattr(object, attr, {}).values():
                if value is not None:
                    notify(ObjectRemovedEvent(value))
                    catalog.unindexObject(value, catalog_util)


@adapter(II18nFilePropertiesContainer, IObjectCopiedEvent)
def handleCopiedI18nFilePropertiesContainer(object, event):
    # When a file properties container is copied, we have to tag it for indexation
    # Effective file indexation will be done only after content have been added to it's new parent container
    object._v_copied_file = True
    # We also have to update object's blobs to avoid losing contents...
    source = event.original
    for attr in II18nFilePropertiesContainerAttributes(source).attributes:
        for key, value in getattr(source, attr, {}).items():
            if isinstance(value, BaseBlobFile):
                getattr(object, attr)[key]._blob = Blob()
                getattr(object, attr)[key].data = value.data
