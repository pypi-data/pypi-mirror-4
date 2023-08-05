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
import pytz
from datetime import datetime

# import Zope3 interfaces

# import local interfaces
from hurry.workflow.interfaces import IWorkflowTransitionEvent
from ztfy.comment.interfaces import IComments
from ztfy.utils.request import getRequest
from ztfy.workflow.interfaces import IWorkflow, IWorkflowTarget, IWorkflowContent

# import Zope3 packages
from zope.component import adapter, getUtility
from zope.i18n import translate

# import local packages

from ztfy.workflow import _


@adapter(IWorkflowTarget, IWorkflowTransitionEvent)
def handleWorkflowTransition(object, event):
    request = getRequest()
    content = IWorkflowContent(object, None)
    if content is not None:
        content.state_date = datetime.now(pytz.UTC)
        content.state_principal = request.principal.id
    wf = getUtility(IWorkflow, IWorkflowTarget(object).workflow_name)
    if event.source is not None:
        comment = translate(_('Changed state: from %s to %s'), context=request) % (translate(wf.states.getTerm(event.source).title, context=request),
                                                                                   translate(wf.states.getTerm(event.destination).title, context=request))
    else:
        comment = translate(_('New state: %s'), context=request) % (translate(wf.states.getTerm(event.destination).title, context=request))
    if event.comment:
        comment += '\n%s' % event.comment
    comments = IComments(object)
    comments.addComment(body=comment,
                        renderer='zope.source.plaintext', tags=('__workflow__'))
