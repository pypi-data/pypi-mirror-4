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
from hurry.workflow.interfaces import IWorkflowState
from zope.tales.interfaces import ITALESFunctionNamespace

# import local interfaces
from ztfy.workflow.interfaces import IWorkflow, IWorkflowTarget, IWorkflowContent
from ztfy.workflow.tal.interfaces import IWorkflowTalesAPI

# import Zope3 packages
from zope.component import queryUtility
from zope.i18n import translate
from zope.interface import implements

# import local packages
from ztfy.utils.traversing import getParent

from ztfy.workflow import _


class WorkflowTalesAdapter(object):

    implements(IWorkflowTalesAPI, ITALESFunctionNamespace)

    def __init__(self, context):
        self.context = context

    def setEngine(self, engine):
        self.request = engine.vars['request']

    def status(self):
        target = IWorkflowTarget(self.context, None)
        if target is None:
            return translate(_("None"), context=self.request)
        wf = queryUtility(IWorkflow, target.workflow_name)
        if wf is None:
            return translate(_("None"), context=self.request)
        state = IWorkflowState(self.context).getState()
        return translate(wf.states.getTerm(state).title, context=self.request)

    def published(self):
        if self.context is None:
            return False
        content = getParent(self.context, IWorkflowTarget)
        if content is None:
            return True
        return IWorkflowContent(content).isPublished()

    def visible(self):
        if self.context is None:
            return False
        content = getParent(self.context, IWorkflowTarget)
        if content is None:
            return True
        return IWorkflowContent(content).isVisible()
