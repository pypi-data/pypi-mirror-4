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
__docformat__ = 'restructuredtext'

from z3c.jsonrpc.publisher import MethodPublisher


class J01DialogFormProcessor(MethodPublisher):
    """Can process a dialog form button handler via JSONRPC."""

    def j01Dialog(self):
        """Renders and returns an initial dialog including the dialog layout.
        """
        return self.context.__call__()

    def doUpdateRender(self):
        """Update, render and return dialog content as json data"""
        self.context.update()
        content = self.context.render()
        # read below if you run into an AttributeError with closeDialog
        closeDialog = self.context.closeDialog
        # note: if you run into an AttributeError e.g.
        # "xy object has no attribute 'closeDialog'" this means the previous
        # dialog didn't define closeDialog=True and was using a non dialog
        # page/form as nextURL
        contentTargetExpression = self.context.contentTargetExpression
        nextURL = self.context.nextURL
        return {'content':content,
                'closeDialog':closeDialog,
                'contentTargetExpression': contentTargetExpression,
                'nextURL': nextURL}

    def j01DialogContent(self):
        """Handles form processing and returns the form content without the
        dialog layout.
        """
        return self.doUpdateRender()

    def j01DialogFormProcessor(self):
        """Handles form processing and returns the form content without the
        dialog layout.
        """
        return self.doUpdateRender()
