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
$Id:$
"""

import zope.interface
import zope.i18nmessageid

from j01.jsonrpc import jsbutton

_ = zope.i18nmessageid.MessageFactory('p01')

    
class DialogButton(jsbutton.JSONRPCButton):
    """JSON-RPC button.
    
    This button requires the following javascript files:

    - z3c.xmlhttp.js
    - z3c.jsonrpcproxy.js
    - jquery.js >= 1.7.0
    - j01.dialog.js

    NOTE: The form using this button must contain the form tag. If the form
    tag doesn't get rendered within each new request, the button click handler
    will get applied more then once to the form and doesn't work.

    """

    callback = 'j01DialogRenderContent'
    urlGetter = None

    def getInputEnterJavaScript(self, form, request):
        """Returns the input enter JavaScript code."""
        formId = form.id.replace('.', '\\\.')
        url = self.getURL(form, request)
        return """
            $('#%s').on('keypress', 'input', function(event){
                c = event.which ? event.which : event.keyCode;
                if (c == 13) {
                    var data = $('#%s').j01FormToArray('%s');
                    proxy = getJSONRPCProxy('%s');
                    proxy.addMethod('j01DialogFormProcessor', %s);
                    proxy.j01DialogFormProcessor(data);
                }
            });
            """ % (formId, formId, self.__name__, url, self.callback)

    def getJavaScript(self, action, request):
        # replace dotted id with '\\.' See jquery.com for details
        formId = action.form.id.replace('.', '\\\.')
        url = self.getURL(action.form, request)
        return """
            $('#%s').on('click', '#%s', function(){
                var data = $('#%s').j01FormToArray('%s');
                proxy = getJSONRPCProxy('%s');
                proxy.addMethod('j01DialogFormProcessor', %s);
                proxy.j01DialogFormProcessor(data);
            });
            """ % (formId, action.id, formId, self.__name__, url, self.callback)


class ShowDialogButton(jsbutton.JSButton):
    """Button which knows how to load and render dialog form via JSON-RPC
    
    This button requires the following javascript files:

    - z3c.xmlhttp.js
    - z3c.jsonrpcproxy.js
    - jquery.js
    - j01.dialog.js

    NOTE: The form using this button must contain the form tag. If the form
    tag doesn't get rendered within each new request, the button click handler
    will get applied more then once to the form and doesn't work.

    """

    urlGetter = None

    def __init__(self, *args, **kwargs):
        # apply optional urlGetter
        if 'urlGetter' in kwargs:
            self.urlGetter = kwargs['urlGetter']
            del kwargs['urlGetter']
        super(ShowDialogButton, self).__init__(*args, **kwargs)

    def getInputEnterJavaScript(self, form, request):
        """Returns the input enter JavaScript code."""
        formId = form.id.replace('.', '\\\.')
        url = self.getURL(form, request)
        return """
            $('#%s').on('keypress', 'input', function(event){
                c = event.which ? event.which : event.keyCode;
                if (c == 13) {
                    var data = $('#%s').j01FormToArray('%s');
                    j01Dialog({'params': data, 'url':'%s'});
                    event.preventDefault();
                    return false;
                }
            });
            """ % (formId, formId, self.__name__, url)

    def getJavaScript(self, action, request):
        # replace dotted id with '\\.' See jquery.com for details
        formId = action.form.id.replace('.', '\\\.')
        url = self.getURL(action.form, request)
        return """
            $('#%s').on('click', '#%s', function(event){
                var data = $('#%s').j01FormToArray('%s');
                j01Dialog({'params': data, 'url':'%s'});
                event.preventDefault();
                return false;
            });
            """ % (formId, action.id, formId, self.__name__, url)


class DialogContentButton(jsbutton.JSONRPCButton):
    """Button which will load and render content into an existing dialog via
    JSON-RPC.
    
    This button requires the following javascript files:

    - z3c.xmlhttp.js
    - z3c.jsonrpcproxy.js
    - jquery.js
    - j01.dialog.js

    NOTE: The form using this button must contain the form tag. If the form
    tag doesn't get rendered within each new request, the button click handler
    will get applied more then once to the form and doesn't work.

    """

    callback = 'j01DialogRenderContent'

    def __init__(self, *args, **kwargs):
        # Provide a dialogURLGetter method
        if 'urlGetter' not in kwargs:
            raise ValueError("Must define a urlGetter methode.")
        super(DialogContentButton, self).__init__(*args, **kwargs)

    def getInputEnterJavaScript(self, form, request):
        """Returns the input enter JavaScript code."""
        # replace dotted id with '\\.' See jquery.com for details
        formId = form.id.replace('.', '\\\.')
        url = self.getURL(form, request)
        return """
            $('#%s').on('keypress', 'input', function(event){
                if(!e){e = window.event;}
                key = event.which ? event.which : event.keyCode;
                if (key == 13) {
                    proxy = getJSONRPCProxy('%s');
                    proxy.addMethod('j01DialogContent', %s);
                    proxy.j01DialogContent();
                }
            });
            """ % (formId, url, self.callback)

    def getJavaScript(self, action, request):
        # replace dotted id with '\\.' See jquery.com for details
        formId = action.form.id.replace('.', '\\\.')
        url = self.getURL(action.form, request)
        return """
            $('#%s').on('click', '#%s', function(event){
                proxy = getJSONRPCProxy('%s');
                proxy.addMethod('j01DialogContent', %s);
                proxy.j01DialogContent();
            });
            """ % (formId, action.id, url, self.callback)


class DialogCloseButton(jsbutton.JSButton):
    """JSON-RPC close dialog button without reloading content.
    
    This button requires the following javascript files:

    - z3c.xmlhttp.js
    - z3c.jsonrpcproxy.js
    - jquery.js
    - j01.dialog.js
    
    Note, you can also use the default DialogButton and implement a close 
    handler. This is sometimes a better solution if the content should be
    updated after the dialog get closed. This button will NOT call the server
    and NOT render content. This button will just close the dialog.

    """

    def getURL(self, form, request):
        """Returns the url based on urlGetter or the form url"""
        if self.urlGetter is not None:
            return self.urlGetter(form)

    def getInputEnterJavaScript(self, form, request):
        """Returns the input enter JavaScript code."""
        formId = form.id.replace('.', '\\\.')
        url = self.getURL(form, request)
        if url is not None:
            url = "'%s'" % url
        else:
            url = ''
        return """
            $('#%s').on('keypress', 'input', function(event){
                if(!e){e = window.event;}
                key = event.which ? event.which : event.keyCode;
                if (key == 13) {
                    j01DialogClose(%s);
                    return false;
                }
            })
            """ % (formId, url)

    def getJavaScript(self, action, request):
        formId = action.form.id.replace('.', '\\\.')
        url = self.getURL(action.form, request)
        if url is not None:
            url = "'%s'" % url
        else:
            url = ''
        return """
            $('#%s').on('click', '#%s', function(){
                j01DialogClose(%s);
            });
            """ % (formId, action.id, url)


# default buttons
class IDialogButtons(zope.interface.Interface):

    add = DialogButton(
        title=_(u'Add')
        )

    applyChanges = DialogButton(
        title=_(u'Apply')
        )

    cancel = DialogButton(
        title=_(u'Cancel')
        )

    close = DialogCloseButton(
        title=_(u'Close')
        )

    delete = DialogButton(
        title=_(u'Delete')
        )

    confirm = DialogButton(
        title=_(u'Confirm')
        )
