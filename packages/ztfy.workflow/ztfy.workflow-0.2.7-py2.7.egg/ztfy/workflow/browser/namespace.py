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
from zope.traversing.interfaces import TraversalError

# import local interfaces
from hurry.workflow.interfaces import IWorkflowState, InvalidTransitionError
from ztfy.workflow.interfaces import IWorkflow, IWorkflowTarget

# import Zope3 packages
from zope.component import getUtility, queryMultiAdapter
from zope.interface import Interface
from zope.traversing import namespace

# import local packages


class WorkflowNamespaceTraverser(namespace.view):
    """Workflow namespace traverser"""

    def traverse(self, name, ignored):
        try:
            workflow = getUtility(IWorkflow, IWorkflowTarget(self.context).workflow_name)
            state = IWorkflowState(self.context).getState()
            transition = workflow.getTransition(state, name)  # raise InvalidTransactionError if NOK
            view_name = transition.user_data.get('view')
            if view_name is not None:
                view = queryMultiAdapter((self.context, self.request), Interface, view_name)
                if view is not None:
                    view.transition = transition
                    return view
        except InvalidTransitionError, e:
            view = queryMultiAdapter((e, self.request), Interface, 'index.html')
            if view is not None:
                return view
        raise TraversalError("++wf++%s" % name)
