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

# import Zope3 interfaces
from ztfy.workflow.browser.viewlet.interfaces import IWorkflowViewletManager, IWorkflowTransitionsViewlet

# import local interfaces
from hurry.workflow.interfaces import IWorkflowInfo
from ztfy.workflow.interfaces import IWorkflow, IWorkflowTarget, ITransitionTarget

# import Zope3 packages
from z3c.template.template import getPageTemplate
from zope.component import queryUtility, queryMultiAdapter
from zope.interface import implements
from zope.viewlet.manager import WeightOrderedViewletManager
from zope.viewlet.viewlet import ViewletBase

# import local packages


class WorkflowViewletManager(WeightOrderedViewletManager):

    implements(IWorkflowViewletManager)


class WorkflowTransitionsViewlet(ViewletBase):

    implements(IWorkflowTransitionsViewlet)

    def _getTransitions(self):
        _transitions = []
        target = IWorkflowTarget(self.context, None)
        if target is None:
            return _transitions
        wf = queryUtility(IWorkflow, target.workflow_name)
        if wf is None:
            return _transitions
        info = IWorkflowInfo(self.context)
        ids = info.getManualTransitionIds()
        return [t for t in (wf.getTransitionById(id) for id in ids)
                        if t.user_data.get('view')]

    def update(self):
        self.transitions = self._getTransitions()

    render = getPageTemplate()

    def getURL(self, transition):
        target = queryMultiAdapter((self.context, self.request, transition), ITransitionTarget)
        if target is not None:
            return target.absoluteURL()
        else:
            return transition.user_data.get('view')
