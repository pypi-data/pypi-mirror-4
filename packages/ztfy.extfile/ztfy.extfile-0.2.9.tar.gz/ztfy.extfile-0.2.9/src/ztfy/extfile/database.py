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

__docformat__ = "restructuredtext"

# import standard packages
import transaction

# import Zope3 interfaces
from zope.app.publication.zopepublication import ZopePublication
from zope.catalog.interfaces import ICatalog
from zope.component.interfaces import IComponentRegistry, ISite
from zope.intid.interfaces import IIntIds
from zope.processlifetime import IDatabaseOpenedWithRoot

# import local interfaces
from ztfy.extfile.interfaces import IBaseExtFileInfo
from ztfy.utils.interfaces import INewSiteManagerEvent

# import Zope3 packages
from zc.catalog.catalogindex import ValueIndex
from zope.catalog.catalog import Catalog
from zope.component import adapter, queryUtility
from zope.intid import IntIds
from zope.location import locate
from zope.site import hooks

# import local packages
from ztfy.utils.site import locateAndRegister


def updateDatabaseIfNeeded(context):
    """Check for missing objects at application startup"""
    try:
        sm = context.getSiteManager()
    except:
        return
    default = sm['default']
    # Check for required IIntIds utility
    intids = queryUtility(IIntIds)
    if intids is None:
        intids = default.get('IntIds')
        if intids is None:
            intids = IntIds()
            locate(intids, default)
            default['IntIds'] = intids
            IComponentRegistry(sm).registerUtility(intids, IIntIds)
    # Check for required catalog and index
    catalog = default.get('Catalog')
    if catalog is None:
        catalog = Catalog()
        locateAndRegister(catalog, default, 'Catalog', intids)
        IComponentRegistry(sm).registerUtility(catalog, ICatalog, 'Catalog')
    if catalog is not None:
        if 'filename' not in catalog:
            index = ValueIndex('filename', IBaseExtFileInfo, False)
            locateAndRegister(index, catalog, 'filename', intids)


@adapter(IDatabaseOpenedWithRoot)
def handleOpenedDatabase(event):
    db = event.database
    connection = db.open()
    root = connection.root()
    root_folder = root.get(ZopePublication.root_name, None)
    for site in root_folder.values():
        if ISite(site, None) is not None:
            hooks.setSite(site)
            updateDatabaseIfNeeded(site)
            transaction.commit()


@adapter(INewSiteManagerEvent)
def handleNewSiteManager(event):
    updateDatabaseIfNeeded(event.object)
