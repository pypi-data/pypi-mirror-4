======
README
======

here are some quick hints till we have a better documentation.

- the dialog library:

  - is responsible for render a dialog and load it's initial content

  - is not responsible for load additional content after inititial content
    get loaded

  - uses DOM element ids which can be used for custom JS access e.g. load
    content into an existing dialog

  - can close the dialog by click on the close link
  
  - can close the dialog by click on the overlay

  - offers a close method which can be used for close existing dialogs
  
  - offers methods for load additional content into an open dialog

- dialog are pages with a dialog layout. The page and the layout do not have
  html and body tags

- dialog can be loaded with ajax or JSON-RPC, by default JSON-RPC is used

- we have to register the templates within the JSON-RPC and the browser layer
  since we can load the pages with JSON-RPC

- after a dialog get loaded and if additional content get loaded e.g. a form
  submit, only the inner content of the dialog get replaced without the layout
  
  This is realy simple within our pagelet pattern because
  
  - initial dialog load (JSON or ajax) uses page.__call__() whihc renders the
    dialog layout
    
  - additional content get loaded by JSON-RPC by calling update/render and
    will skip calling __call__. This will skip the layout rendering. See
    z3c.pagelet for more information.

- works with built in JSON-RPC pages and form given from j01.jsonrpc. This
  allows to handle forms and reload content into the dialog out fo the box.

- the dialog layout can be changed. You can change the dialo layout and the
  relevant CSS file simply by register new files for your layer

- loading content in an existing dialog is not part of the dialog implementation
  the dialog content page is responsible to use linsk or buttons to reload
  additional content into an existing dialog. 


testing
-------

Just test some imports for now:

  >>> from zope.publisher.browser import TestRequest
  >>> from j01.dialog import interfaces
  >>> from j01.dialog import jspage
  
  >>> class Content(object):
  ...     pass
  >>> content = Content()
  >>> request = TestRequest()
  >>> dialogPage = jspage.DialogPage(content, request)
  >>> interfaces.IDialogPage.providedBy(dialogPage)
  True
