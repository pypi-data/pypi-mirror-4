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


# import Zope3 interfaces

# import local interfaces
from hurry.query.interfaces import IQuery
from hurry.workflow.interfaces import IWorkflowVersions, IWorkflowState

# import Zope3 packages
from zope.component import getUtility
from zope.interface import implements

# import local packages
from hurry.query import And
from hurry.query.value import In, Eq
from hurry.workflow.workflow import WorkflowVersions as WorkflowVersionsBase


WF_STATE_INDEX = ('WorkflowCatalog', 'wf_state')
WF_IDS_INDEX = ('WorkflowCatalog', 'wf_id')


class WorkflowVersions(WorkflowVersionsBase):
    """Utility used to handle content versions"""

    implements(IWorkflowVersions)

    def getVersions(self, state=None, id=None, object=None):
        assert (state is not None) or (id is not None) or (object is not None)
        query = getUtility(IQuery)
        request = []
        if state is not None:
            if isinstance(state, tuple):
                request.append(In(WF_STATE_INDEX, state))
            else:
                request.append(Eq(WF_STATE_INDEX, state))
        if id is not None:
            request.append(Eq(WF_IDS_INDEX, id))
        elif object is not None:
            state = IWorkflowState(object, None)
            if state is not None:
                request.append(Eq(WF_IDS_INDEX, state.getId()))
        return query.searchResults(And(*request))

    def getVersionsWithAutomaticTransitions(self):
        return ()

    def hasVersion(self, state, id):
        return bool(self.getVersions(state, id))

    def hasVersionId(self, id):
        query = getUtility(IQuery)
        return bool(query.searchResults(Eq(WF_IDS_INDEX, id)))
