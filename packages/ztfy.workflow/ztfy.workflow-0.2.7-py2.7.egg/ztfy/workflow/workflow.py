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
from zope.security.interfaces import NoInteraction, Unauthorized

# import local interfaces
from hurry.workflow.interfaces import IWorkflowInfo, IWorkflowState, ConditionFailedError
from ztfy.workflow.interfaces import IWorkflow, IWorkflowTarget, ITransition, ITransitionTarget

# import Zope3 packages
from zope.component import adapts, getUtility
from zope.event import notify
from zope.interface import Interface, implements
from zope.lifecycleevent import ObjectModifiedEvent
from zope.security.management import getInteraction
from zope.traversing.browser import absoluteURL

# import local packages
from hurry.workflow.workflow import nullCheckPermission, WorkflowTransitionEvent, WorkflowVersionTransitionEvent
from hurry.workflow.workflow import Workflow as WorkflowBase
from hurry.workflow.workflow import WorkflowInfo as WorkflowInfoBase, WorkflowState as WorkflowStateBase


class WorkflowStateAdapter(WorkflowStateBase):
    """Workflow state adapter implementing ILocation"""

    adapts(IWorkflowTarget)
    implements(IWorkflowState)


class WorkflowInfoAdapter(WorkflowInfoBase):
    """Enhanced IWorkflowInfo adapter handling several registered workflows"""

    adapts(IWorkflowTarget)
    implements(IWorkflowInfo)

    @property
    def name(self):
        return IWorkflowTarget(self.context).workflow_name

    def fireTransition(self, transition_id, comment=None, side_effect=None,
                       check_security=True):
        state = IWorkflowState(self.context)
        wf = getUtility(IWorkflow, self.name)
        # this raises InvalidTransitionError if id is invalid for current state
        transition = wf.getTransition(state.getState(), transition_id)
        # check whether we may execute this workflow transition
        try:
            interaction = getInteraction()
        except NoInteraction:
            checkPermission = nullCheckPermission
        else:
            if check_security:
                checkPermission = interaction.checkPermission
            else:
                checkPermission = nullCheckPermission
        if not checkPermission(
            transition.permission, self.context):
            raise Unauthorized(self.context,
                               'transition: %s' % transition_id,
                               transition.permission)
        # now make sure transition can still work in this context
        if not transition.condition(self, self.context):
            raise ConditionFailedError
        # perform action, return any result as new version
        result = transition.action(self, self.context)
        if result is not None:
            if transition.source is None:
                IWorkflowState(result).initialize()
            # stamp it with version
            state = IWorkflowState(result)
            state.setId(IWorkflowState(self.context).getId())
            # execute any side effect:
            if side_effect is not None:
                side_effect(result)
            event = WorkflowVersionTransitionEvent(result, self.context,
                                                   transition.source,
                                                   transition.destination,
                                                   transition, comment)
        else:
            if transition.source is None:
                IWorkflowState(self.context).initialize()
            # execute any side effect
            if side_effect is not None:
                side_effect(self.context)
            event = WorkflowTransitionEvent(self.context,
                                            transition.source,
                                            transition.destination,
                                            transition, comment)
        # change state of context or new object
        state.setState(transition.destination)
        notify(event)
        # send modified event for original or new object
        if result is None:
            notify(ObjectModifiedEvent(self.context))
        else:
            notify(ObjectModifiedEvent(result))
        return result

    def getFireableTransitionIdsToward(self, state):
        wf = getUtility(IWorkflow, self.name)
        result = []
        for transition_id in self.getFireableTransitionIds():
            transition = wf.getTransitionById(transition_id)
            if transition.destination == state:
                result.append(transition_id)
        return result

    def _getTransitions(self, trigger):
        # retrieve all possible transitions from workflow utility
        wf = getUtility(IWorkflow, self.name)
        transitions = wf.getTransitions(IWorkflowState(self.context).getState())
        # now filter these transitions to retrieve all possible
        # transitions in this context, and return their ids
        return [transition for transition in transitions
                                          if transition.trigger == trigger]


class Workflow(WorkflowBase):
    """Custom workflow class"""

    implements(IWorkflow)

    def __init__(self, transitions, states, published_states=()):
        super(Workflow, self).__init__(transitions)
        self.states = states
        self.published_states = published_states


class WorkflowTransitionTargetAdapter(object):

    adapts(Interface, Interface, ITransition)
    implements(ITransitionTarget)

    def __init__(self, context, request, transition):
        self.context = context
        self.request = request
        self.transition = transition

    def absoluteURL(self):
        return '%s/++wf++%s' % (absoluteURL(self.context, self.request),
                                self.transition.transition_id)
