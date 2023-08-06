##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
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


from zope.publisher.interfaces.browser import IBrowserPage


class IDialogPage(IBrowserPage):
    """Dialog Page."""


class IDialogIFrame(IDialogPage):
    """Dialog page using an IFrame for load the real content."""


class IDialogForm(IDialogPage):
    """Dialog form."""


class IDialogAddForm(IDialogForm):
    """Dialog add form."""


class IDialogEditForm(IDialogForm):
    """Dialog edit form."""


class IDialogDeleteForm(IDialogPage):
    """Dialog delete form."""


class IDialogConfirmForm(IDialogPage):
    """Dialog confirm form."""
