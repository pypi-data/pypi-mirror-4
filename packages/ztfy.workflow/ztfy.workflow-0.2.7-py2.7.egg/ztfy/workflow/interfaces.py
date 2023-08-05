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
from zope.schema.interfaces import IVocabularyTokenized

# import local interfaces
from hurry.workflow.interfaces import IWorkflow as IWorkflowBase
from ztfy.comment.interfaces import ICommentable

# import Zope3 packages
from zope.interface import Interface, invariant, Invalid
from zope.schema import Datetime, Choice, Tuple, TextLine, Object

# import local packages
from ztfy.security.schema import Principal

from ztfy.workflow import _


class IWorkflow(IWorkflowBase):
    """Marker interface for custom workflows extending IWorkflow"""

    states = Object(schema=IVocabularyTokenized)

    published_states = Tuple(title=_("Published states"),
                             description=_("Tuple of published and potentially visible workflow states"),
                             required=False,
                             value_type=TextLine())


class IWorkflowTarget(ICommentable):
    """Marker interface for contents handled by a workflow"""

    workflow_name = Choice(title=_("Workflow name"),
                           description=_("Name of a registered workflow utility used by this workflow"),
                           required=True,
                           vocabulary="ZTFY workflows")


class IWorkflowContentInfo(Interface):
    """Interface used to define common workflow properties"""

    state_date = Datetime(title=_("State date"),
                          description=_("Date when the current state was defined"))

    state_principal = Principal(title=_("State principal"),
                                description=_("Name of the principal who defined the current state"))

    publication_date = Datetime(title=_("Publication date"),
                                description=_("Date when content was accepted to publication by the publisher, entered in ISO format"),
                                required=False)

    first_publication_date = Datetime(title=_("First publication date"),
                                      description=_("Date when content was accepted to publication by the publisher for the first time"),
                                      required=False)

    publication_effective_date = Datetime(title=_("Publication start date and time"),
                                          description=_("Date and time from which content will be visible"),
                                          required=True,
                                          default=None)

    publication_expiration_date = Datetime(title=_("Publication end date and time"),
                                           description=_("Date and time until which content will be visible"),
                                           required=False,
                                           default=None)

    @invariant
    def expireAfterEffective(self):
        if self.publication_expiration_date is not None:
            if self.publication_effective_date is None:
                raise Invalid(_("Can't define publication end date without publication start date"))
            if self.publication_expiration_date <= self.publication_effective_date:
                raise Invalid(_("Publication end date must be null or defined after publication's start date"))

    def isPublished():
        """Is the context published or not ?"""

    def isVisible():
        """Is the context visible according to current workflow state and security context ?"""


class IWorkflowContent(IWorkflowContentInfo):
    """Marker interface for workflow contents"""


class ITransition(Interface):
    """Marker interface for standard transitions"""


class ITransitionTarget(Interface):
    """Get transition link target"""

    def absoluteURL():
        """Get absolute URL for adapted context and request"""
