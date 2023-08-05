### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2011 Thierry Florac <tflorac AT ulthar.net>
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
from hurry.workflow.interfaces import IWorkflowState
from zope.app.publication.zopepublication import ZopePublication
from zope.catalog.interfaces import ICatalog
from zope.component.interfaces import IComponentRegistry, ISite
from zope.dublincore.interfaces import IZopeDublinCore
from zope.intid.interfaces import IIntIds
from zope.processlifetime import IDatabaseOpenedWithRoot

# import local interfaces
from ztfy.utils.interfaces import INewSiteManagerEvent
from ztfy.workflow.interfaces import IWorkflowTarget

# import Zope3 packages
from zc.catalog.catalogindex import ValueIndex, DateTimeValueIndex
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
    catalog = default.get('WorkflowCatalog')
    if catalog is None:
        catalog = Catalog()
        locateAndRegister(catalog, default, 'WorkflowCatalog', intids)
        IComponentRegistry(sm).registerUtility(catalog, ICatalog, 'WorkflowCatalog')
    if catalog is not None:
        if 'wf_id' not in catalog:
            index = ValueIndex('getId', IWorkflowState, True)
            locateAndRegister(index, catalog, 'wf_id', intids)
        if 'wf_state' not in catalog:
            index = ValueIndex('getState', IWorkflowState, True)
            locateAndRegister(index, catalog, 'wf_state', intids)
        if 'wf_name' not in catalog:
            index = ValueIndex('workflow_name', IWorkflowTarget, False)
            locateAndRegister(index, catalog, 'wf_name', intids)
        if 'creation_date' not in catalog:
            index = DateTimeValueIndex('created', IZopeDublinCore, False)
            locateAndRegister(index, catalog, 'creation_date', intids)
        if 'modification_date' not in catalog:
            index = DateTimeValueIndex('modified', IZopeDublinCore, False)
            locateAndRegister(index, catalog, 'modification_date', intids)
        if 'effective_date' not in catalog:
            index = DateTimeValueIndex('effective', IZopeDublinCore, False)
            locateAndRegister(index, catalog, 'effective_date', intids)
        if 'expiration_date' not in catalog:
            index = DateTimeValueIndex('expires', IZopeDublinCore, False)
            locateAndRegister(index, catalog, 'expiration_date', intids)


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
