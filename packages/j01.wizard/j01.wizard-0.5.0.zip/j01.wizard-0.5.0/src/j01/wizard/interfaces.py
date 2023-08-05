##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH and Contributors.
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
"""
$Id: interfaces.py 3048 2012-09-02 05:33:38Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.i18nmessageid
import zope.interface
import zope.schema
import zope.location.interfaces

import z3c.pagelet.interfaces

import j01.jsonrpc.interfaces
import j01.dialog.interfaces

_ = zope.i18nmessageid.MessageFactory('p01')


class IBackButton(j01.jsonrpc.interfaces.IJSButton):
    """A button that forces to go to the previous step."""


class INextButton(j01.jsonrpc.interfaces.IJSButton):
    """A button that forces to go to the next step."""


class IStep(z3c.pagelet.interfaces.IPagelet):
    """Step base interface"""

    available = zope.schema.Bool(
        title=u'Available',
        description=u'Marker for available step',
        default=True,
        required=False)

    visible = zope.schema.Bool(
        title=u'Show step in wizard step menu',
        description=u'Show step in wizard step menu',
        default=True,
        required=False)

    showRequired = zope.schema.Bool(
        title=u'Show required label',
        description=u'Show required label',
        default=True,
        required=False)

    weight = zope.schema.Int(
        title=u'Step weight in wizard',
        description=u'Step weight in wizard',
        default=0,
        required=False)

    completed = zope.schema.Bool(
        title=u'Completed',
        description=u'Marker for completed step',
        default=False,
        required=False)

    handleApplyOnBack = zope.schema.Bool(
        title=u'Handle apply changes on back',
        description=u'Handle apply changes on back will force validation',
        default=False,
        required=False)

    handleApplyOnNext = zope.schema.Bool(
        title=u'Handle apply changes on next',
        description=u'Handle apply changes on next will force validation',
        default=True,
        required=False)

    handleApplyOnComplete = zope.schema.Bool(
        title=u'Handle apply changes on complete',
        description=u'Handle apply changes on complete will force validation',
        default=True,
        required=False)

    showSaveButton = zope.schema.Bool(
        title=u'Show save button',
        description=u'Show save button',
        default=True,
        required=False)

    showBackButton = zope.schema.Bool(
        title=u'Show back button',
        description=u'Back button condition',
        default=True,
        required=False)

    showNextButton = zope.schema.Bool(
        title=u'Show next button',
        description=u'Next button condition',
        default=True,
        required=False)

    showCompleteButton = zope.schema.Bool(
        title=u'Show complete button',
        description=u'Complete button condition',
        default=True,
        required=False)

    def goToStep(stepName):
        """Redirect to step by name."""

    def goToNext():
        """Redirect to next step."""

    def goToBack():
        """Redirect to back step."""

    def applyChanges(data):
        """Generic form save method taken from z3c.form.form.EditForm."""

    def doHandleApply(action):
        """Extract data and calls applyChanges."""

    def doBack(action):
        """Process back action and return True on sucess."""

    def doNext(action):
        """Process next action and return True on sucess."""

    def doComplete(action):
        """Process complete action and return True on sucess."""

    def update():
        """Update the step."""

    def render():
        """Render the step content w/o wrapped layout."""

    def __call__():
        """Compute a response body including the layout"""


class IJSONRPCStep(IStep, j01.jsonrpc.interfaces.IJSONRPCForm):
    """JSONRPC step form."""


class IDialogStep(IStep, j01.dialog.interfaces.IDialogForm):
    """Dialog step form."""


class IWizard(zope.interface.Interface):
    """Wizard base interface"""

    firstStepAsDefault = zope.schema.Bool(
        title=u'Show first step as default',
        description=u'Show first step or first not completed step as default',
        default=True,
        required=True)

    adjustStep = zope.schema.Bool(
        title=u'Adjust step',
        description=u'Force fallback (redirect) to last incomplete step',
        default=True,
        required=False)

    confirmationPageName = zope.schema.ASCIILine(
        title=u'Confirmation page name',
        description=u'The confirmation page name shown after completed',
        default=None,
        required=False)

    cssActive = zope.schema.ASCIILine(
        title=u'Active step menu CSS class',
        description=u'The active step menu CSS class',
        default='selected',
        required=False)

    cssInActive = zope.schema.ASCIILine(
        title=u'In-Active step menu item CSS class',
        description=u'The in-active step menu item CSS class',
        default=None,
        required=False)

    stepInterface = zope.interface.Attribute('Step lookup interface.')

    steps = zope.interface.Attribute(
        """List of one or more IStep (can be lazy).""")

    stepMenu = zope.interface.Attribute("""Step menu info.""")

    step = zope.schema.Object(
        title=u'Current step',
        description=u'Current step',
        schema=IDialogStep)

    completed = zope.schema.Bool(
        title=u'Completed',
        description=u'Marker for completed step',
        default=False,
        required=False)

    isFirstStep = zope.schema.Bool(
        title=u'Is first step',
        description=u'Is first step',
        default=False,
        required=False)

    isLastStep = zope.schema.Bool(
        title=u'Is last step',
        description=u'Is last step',
        default=False,
        required=False)

    def doAdjustStep():
        """Ensure that we can't traverse to more then the first not completed 
        step.
        """

    def getDefaultStep():
        """Can return the first or first not completed step as default."""

    def doAdjustStep():
        """Make sure all previous steps got completed. If not, redirect to the 
        last uncomplete step.
        """

    def updateActions():
        """Update wizard actions."""

    def publishTraverse(request, name):
        """Traverse to step by it's name."""

    def browserDefault(request):
        """The default step is our browserDefault traversal step."""

    def goToStep(stepName):
        """Redirect to the step by name."""

    def goToBack():
        """Redirect to next step if previous get sucessfuly processed."""

    def goToNext():
        """Redirect to next step if previous get sucessfuly processed."""

    def doBack(action):
        """Process something if back action get exceuted."""

    def doNext(action):
        """Process something if next action get exceuted."""

    def doComplete(action):
        """Process something if complete action get exceuted."""

    def doFinish():
        """Process something on complete wizard."""

    def update():
        """Adjust step and update actions."""


class IJSONRPCWizard(IWizard, j01.jsonrpc.interfaces.IJSONRPCPage):
    """JSONRPC wizard form."""


class IDialogWizard(IWizard, j01.dialog.interfaces.IDialogPage):
    """Dialog wizard form."""
