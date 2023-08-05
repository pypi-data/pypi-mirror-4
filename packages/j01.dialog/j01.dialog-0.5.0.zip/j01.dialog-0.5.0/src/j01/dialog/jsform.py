##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH and Contributors.
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
$Id: __init__.py 6 2006-04-16 01:28:45Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface

from z3c.template.template import getLayoutTemplate
from z3c.template.template import getPageTemplate

from j01.jsonrpc import jsform
from j01.jsonrpc import jsbutton
from j01.dialog import interfaces 
from j01.dialog.jsbutton import IDialogButtons


class DialogForm(jsform.JSONRPCForm):
    """Dialog JSONRPC form."""

    zope.interface.implements(interfaces.IDialogForm)

    layout = getLayoutTemplate(name='dialog')
    template = getPageTemplate()

    buttons = jsbutton.JSButtons()

    prefix = 'dialog'

    j01DialogTitle = None
    closeDialog = False
    nextURL = None
    contentTargetExpression = None

    def setNextURL(self, url, status, closeDialog=True):
        """Helper for set a nextURL including status message and closeDialog"""
        self.closeDialog = closeDialog
        super(DialogForm, self).setNextURL(url, status)

    def renderClose(self):
        """Return content if you need to render content after close."""
        return None

    def render(self):
        # knows what to return for the dialog parent
        if self.closeDialog:
            return self.renderClose()
        return self.template()


class DialogEditForm(DialogForm, jsform.JSONRPCEditForm):
    """Dialog JSONRPC edit form."""

    zope.interface.implements(interfaces.IDialogEditForm)

    buttons = jsbutton.JSButtons()

    closeOnApplyWithoutError = True

    def doHandleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        if changes:
            self.status = self.successMessage
            # close on apply without error
            if self.closeOnApplyWithoutError:
                self.closeDialog = True
        else:
            self.status = self.noChangesMessage
            # close on apply without error
            if self.closeOnApplyWithoutError:
                self.closeDialog = True
        return changes

    def doHandleCancel(self, action):
        self.closeDialog = True

    @jsform.jsonRPCButtonHandler(IDialogButtons['applyChanges'])
    def handleApply(self, action):
        self.doHandleApply(action)

    @jsform.jsonRPCButtonHandler(IDialogButtons['cancel'])
    def handleCancel(self, action):
        self.doHandleCancel(action)


class DialogAddForm(DialogForm, jsform.JSONRPCAddForm):
    """Dialog JSONRPC edit form."""

    zope.interface.implements(interfaces.IDialogAddForm)

    buttons = jsbutton.JSButtons()

    def doHandleAdd(self, action):
        # Note we, use the data from the request.form
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True
            self.closeDialog = True
        return obj

    def doHandleCancel(self, action):
        self.closeDialog = True

    @jsform.jsonRPCButtonHandler(IDialogButtons['add'])
    def handleAdd(self, action):
        self.doHandleAdd(action)

    @jsform.jsonRPCButtonHandler(IDialogButtons['cancel'])
    def handleCancel(self, action):
        self.doHandleCancel(action)


class DialogDeleteForm(DialogForm):
    """Dialog JSONRPC delete form."""

    zope.interface.implements(interfaces.IDialogDeleteForm)

    buttons = jsbutton.JSButtons()

    ignoreContext = True

    def doHandleDelete(self, action):
        raise NotImplementedError(
            'Subclass must implement doHandleDelete')

    def doHandleCancel(self, action):
        self.closeDialog = True

    @jsform.jsonRPCButtonHandler(IDialogButtons['delete'])
    def handleDelete(self, action):
        self.doHandleDelete(action)

    @jsform.jsonRPCButtonHandler(IDialogButtons['cancel'])
    def handleCancel(self, action):
        self.doHandleCancel(action)


class DialogConfirmForm(DialogForm):
    """Dialog JSONRPC confirm form."""

    zope.interface.implements(interfaces.IDialogConfirmForm)

    buttons = jsbutton.JSButtons()

    ignoreContext = True

    def doHandleConfirm(self, action):
        raise NotImplementedError('Subclass must implement doHandleConfirm')

    def doHandleCancel(self, action):
        self.closeDialog = True

    @jsform.jsonRPCButtonHandler(IDialogButtons['confirm'])
    def handleConfirm(self, action):
        self.doHandleConfirm(action)

    @jsform.jsonRPCButtonHandler(IDialogButtons['cancel'])
    def handleCancel(self, action):
        self.doHandleCancel(action)
