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
$Id: wizard.py 2908 2012-05-10 14:44:41Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
from zope.publisher.interfaces import NotFound

from z3c.jsonrpc.interfaces import IMethodPublisher
from z3c.template.template import getLayoutTemplate
from z3c.template.template import getPageTemplate

from j01.jsonrpc import jsform
from j01.jsonrpc import jsbutton

from j01.wizard import interfaces
from j01.wizard.button import WizardButtonActions
from j01.wizard.button import IJSONRPCWizardButtons
from j01.wizard.button import IDialogWizardButtons


j01DialogContentAdHocLink = """
<script type="text/javascript">
  $('a.j01DialogContentAdHocLink').j01DialogContent();
</script>
"""


j01LoadContentAdHocLink = """
<script type="text/javascript">
  $('a.j01LoadContentAdHocLink').j01LoadContent();
</script>
"""



class WizardBase(jsform.JSONRPCForm):
    """Wiard base class"""

    layout = getLayoutTemplate()
    template = getPageTemplate()

    buttons = jsbutton.JSButtons()

    nextURL = None
    contentTargetExpression = None

    # wizard
    adjustStep = True
    finishURL = None

    # menu and links inclduing JQuery selector
    cssActive = 'selected'
    cssInActive = None
    cssMenuLink = None

    # for internal use
    __name__ = None
    steps = None
    step = None

    @property
    def fields(self):
        return self.step.fields

    @property
    def widgets(self):
        return self.step.widgets

    def publishTraverse(self, request, name):
        """Used if traversed with jsonrpc request"""
        view = zope.component.queryMultiAdapter((self, request), name=name)
        if view is None or not IMethodPublisher.providedBy(view):
            # this means the name is a step name we like to traverse to
            # Remove HTML ending
            if '.' in name:
                rawName = name.rsplit('.', 1)[0]
            else:
                rawName = name
            if self.steps is None:
                self.steps = self.setUpSteps()
            step = self.getStep(rawName)
            if step is not None:
                # this allows to open the dialog with a current step by
                # using wizard/stepname as url
                self.step = step
                return self
            else:
                # not such step found
                raise NotFound(self, name, request)
        else:
            # jsonrpc form processing
            return view

    def browserDefault(self, request):
        """Used if traversed with browser request"""
        if self.steps is None:
            self.steps = self.setUpSteps()
        if self.step is None:
            # setup step and return wizard
            self.step = self.setUpStep()
        return self, ()

    # steps and step setup
    def setUpSteps(self):
        """Return a list of steps."""
        raise NotImplementedError("Subclass must implement setUpSteps")

    def filterSteps(self):
        """Make sure to only select available steps and we give a name."""
        self.steps = [step for step in self.steps if step.available]

    def orderSteps(self):
        # order steps by it's weight
        self.steps = sorted(self.steps, key=lambda step: step.weight)

    def setUpStep(self):
        """Kowns how to setup the current step"""
        # return first not completed step
        for step in self.steps:
            if step.completed == False:
                return step
        # fallback to first step if all steps completed
        return self.steps[0]

    def getStep(self, name):
        """Returns a step by its' name"""
        for step in self.steps:
            if step.__name__ == name:
                return step

    def setStep(self, name, doUpdate=True):
        """Set an available step and optional update"""
        # ensure steps
        self.updateSteps()
        # set the given step
        for step in self.steps:
            if step.__name__ == name:
                self.step = step
                if doUpdate:
                    self.step.update()

    # conditions
    @property
    def completed(self):
        for step in self.steps:
            if not step.completed:
                return False
        return True

    @property
    def isFirstStep(self):
        """See interfaces.IDialogWizard"""
        return self.step and self.step.__name__ == self.steps[0].__name__

    @property
    def isLastStep(self):
        """See interfaces.IDialogWizard"""
        return self.step and self.step.__name__ == self.steps[-1].__name__

    @property
    def showBackButton(self):
        """Ask the step."""
        return self.step and self.step.showBackButton

    @property
    def showNextButton(self):
        """Ask the step."""
        return self.step and self.step.showNextButton

    @property
    def showCompleteButton(self):
        """Ask the step."""
        return self.step.showCompleteButton

    # step menu
    @property
    def stepMenu(self):
        items = []
        append = items.append
        lenght = len(self.steps)-1
        for idx, step in enumerate(self.steps):
            firstStep = False
            lastStep = False
            if step.visible:
                isSelected = self.step and self.step.__name__ == step.__name__
                cssClass = isSelected and self.cssActive or self.cssInActive
                if idx == 0:
                    firstStep = True
                if idx == lenght:
                    lastStep = True
                append({
                    'name': step.__name__,
                    'title': step.label or step.__name__,
                    'number': str(idx+1),
                    'url': '%s/%s' % (self.pageURL, step.__name__),
                    'selected': self.step.__name__ == step.__name__,
                    'class': cssClass,
                    'aCSS': self.cssMenuLink,
                    'first': firstStep,
                    'last': lastStep
                    })
        return items

    # step navigation
    def getBackStep(self):
        if len(self.steps) > 1:
            idx = self.steps.index(self.step)
            if idx > 0:
                step = self.steps[idx-1]
                return step
        return None

    def getNextStep(self):
        if len(self.steps) > 1:
            idx = self.steps.index(self.step)
            if idx < len(self.steps):
                step = self.steps[idx+1]
                return step
        return None

    def goToBack(self):
        # set back step
        step = self.getBackStep()
        if step is not None:
            self.step = step

    def goToNext(self):
        # set next step
        step = self.getNextStep()
        if step is not None:
            self.step = step

    # step processing
    def doAdjustStep(self):
        # Make sure all previous steps got completed. If not, redirect to the 
        # last uncomplete step
        if not self.adjustStep:
            return False
        for step in self.steps:
            if step is self.step:
                # no previous step is not completed current step seems fine
                break
            if step.completed == False:
                # prepare redirect to not completed step and return True
                self.step = step
                return True
        # or return False
        return False

    def doBack(self, action):
        if self.step.doBack(action):
            self.goToBack()

    def doNext(self, action):
        if self.step.doNext(action):
            self.goToNext()

    def doComplete(self, action):
        if self.step.doComplete(action):
            # do finsih after step get completed is completed
            self.doFinish()

    def doFinish(self):
        """Setup nextURL if finishURL is given."""
        if self.finishURL:
            self.nextURL = self.finishURL

    # update processing
    def updateSteps(self):
        if self.steps is None:
            # publishTraverse did not setup our steps
            self.steps = self.setUpSteps()

    def updateStep(self):
        if self.step is None:
            # publishTraverse did not setup our steps
            self.step = self.setUpStep()
        # adjust step before we start processing actions
        adjusted = self.doAdjustStep()
        self.step.update()
        if adjusted:
            self.step.notifyIncompleteStep()

    def updateActions(self):
        self.actions = WizardButtonActions(self, self.request, self.context)
        self.actions.update()
        self.actions.execute()

    def update(self):
        # setup steps
        self.updateSteps()
        # order and filter steps
        self.filterSteps()
        self.orderSteps()
        # setup and update step
        self.updateStep()
        # get current step before action get executed
        oldStep = self.step
        # update and execute wizard action
        self.updateActions()
        if self.step != oldStep:
            # step get changed by action handling e.g. next, back button
            # setup and filter steps again
            self.updateSteps()
            # update new step
            self.updateStep()

    def render(self):
        # our current step knows what we render
        return self.step.render()


class JSONRPCWizard(WizardBase, jsform.JSONRPCForm):
    """JSONRPC wizard implementation

    A JSONRPC wizard uses steps for render the content.

    Compared to the z3c.wizard implementation we will not traverse from the
    wizard to the steps the wizard itself represents (renders) the step as it
    whould be the wizard content.

    We also not directly use a redirect concept, we simply use the j01.jsonrpc
    javascript nextURL handling concept which forces to load the next url page.

    We simply call a wizard like any other page or form and the wizard renders
    the content from the current step. This means all steps allways uses the
    same url (wizard url) and renders depending on it's current step different
    content. This requires that we mark our response with a no caching header.

    All steps will get loaded with our JSONRPC buttons. The step itself is
    a simple JSONRPCForm with an enhanced step handling API. Just use our
    default JSONRPCStep class as base class for your own steps as you whould
    use a simple z3c.form class for your forms. Just take care that we will
    setup our buttons and actions not like in z3c.form. See j01.jsonrpc form
    more information about button setup. 

    """

    zope.interface.implements(interfaces.IJSONRPCWizard)

    # wizard values
    cssMenuLink = 'j01LoadContentAdHocLink'

    @property
    def menuJavaScript(self):
        return j01DialogContentAdHocLink

    @jsform.jsonRPCButtonHandler(IJSONRPCWizardButtons['back'])
    def handleBack(self, action):
        self.doBack(action)

    @jsform.jsonRPCButtonHandler(IJSONRPCWizardButtons['next'])
    def handleNext(self, action):
        self.doNext(action)

    @jsform.jsonRPCButtonHandler(IJSONRPCWizardButtons['complete'])
    def handleComplete(self, action):
        self.doComplete(action)


class DialogWizard(WizardBase, jsform.JSONRPCForm):
    """Dialog wizard implementation
    
    A dialog wizard provides the dialog layout and uses steps for
    render the dialog content.

    Compared to the z3c.wizard implementation we will not traverse from the
    wizard to the steps the wizard itself represents (renders) the step as it
    whould be the wizard content.

    We also not directly use a redirect concept, we simply use the j01.dialog
    javascript nextURL handling concept which forces to load the next url page.

    We simply call a wizard like any other page or form and the wizard renders
    the content from the current step. This means all steps allways uses the
    same url (wizard url) and renders depending on it's current step different
    content. This requires that we mark our response with a no caching header.

    All steps will get loaded with our j01.dialog buttons. The step itself is
    a simple DialogForm with an enhanced step handling API. Just use our
    default DialogStep class as base class for your own steps as you whould
    use a simple z3c.form class for your forms. Just take care that we will
    setup our buttons and actions not like in z3c.form. See j01.jsonrpc form
    more information about button setup. 

    """

    zope.interface.implements(interfaces.IDialogWizard)

    layout = getLayoutTemplate(name='dialog')

    # dialog
    prefix = 'dialog'

    j01DialogTitle = None
    closeDialog = False

    # wizard values
    cssMenuLink = 'j01DialogContentAdHocLink'

    @property
    def menuJavaScript(self):
        return j01LoadContentAdHocLink

    @jsform.jsonRPCButtonHandler(IDialogWizardButtons['back'])
    def handleBack(self, action):
        self.doBack(action)

    @jsform.jsonRPCButtonHandler(IDialogWizardButtons['next'])
    def handleNext(self, action):
        self.doNext(action)

    @jsform.jsonRPCButtonHandler(IDialogWizardButtons['complete'])
    def handleComplete(self, action):
        self.doComplete(action)

    def doFinish(self):
        """Close dialog after doComplete if finishURL is given."""
        self.closeDialog = True
        super(DialogWizard, self).doFinish()

    def renderClose(self):
        """Return content if you need to render content after close."""
        return self.step.renderClose()

    def render(self):
        # knows what to return for the dialog parent
        if self.closeDialog:
            return self.renderClose()
        return super(DialogWizard, self).render()