//-----------------------------------------------------------------------------
// j01.dialog javascript v 0.5.0
//-----------------------------------------------------------------------------

function j01DialogClose(url){
    dlgHolder = $('#j01DialogHolder');
    dlg = $('#j01Dialog');
    // unbind event handler
    $(window).unbind('resize');
    $(window).unbind('scroll');
    dlg.find('#j01DialogClose').unbind('click');
    $("#j01DialogOverlay").unbind("click").remove();
    $("#j01DialogHiddenIFrame").remove();
    dlg.hide();
    dlg.remove();
    dlgHolder.remove();
    document.onkeydown = "";
    if (typeof url !== 'undefined' && url){
        window.location = url;
        return false;
    }
}

function j01DialogCenter(dlg){
    var wh = $(window).height();
    var ww = $(window).width();
    var dh = dlg.height();
    var dw = dlg.width();
    if (wh < dh || ww < dw) {
        // don't center if dialog is bigger then the window.
        // this prevents that the dialog get re-positioned during scrolling
        return false;
    }
    // calculate position
    var top = wh/2 - dh/2 + $(window).scrollTop();
    var left = ww/2 - dw/2 + $(window).scrollLeft();
    // never use a negativ top or left value
    top = Math.max(top, 0);
    left = Math.max(left, 0);
    dlg.css({left: left +'px', top: top +'px'});
}

function j01DialogResize(dlg){
    // remove old size
    dlg.css({'width': '', 'height': ''});
    // get calculated new width
    width = dlg.width();
    height = dlg.height();
    // make sure the content is not smaller then the title
    closeWidth = Math.max($('#j01DialogClose', dlg).width(), 0);
    controlsWidth = Math.max($('#j01DialogControls', dlg).width(), 0);
    // needs a padding-right in title as workarround for the floating close div
    minWidth = closeWidth + controlsWidth;
    width = Math.max(width, minWidth);
    dlg.css({'width': dlg.width() +'px', 'height': dlg.height() +'px'});
    j01DialogCenter(dlg);
}

function j01DialogRenderContent(response) {
    // callback method which knows how to redirect, render content into a
    // dialog or content area
    var dlg  = $('#j01Dialog');
    var dlgContent = $('#j01DialogContent', dlg);
    if (response.message) {
        // show error message in dialog content
        dlgContent.empty();
        contentWrapper = $('<div id="j01DialogError"></div>');
        contentWrapper.append(response.message);
        dlgContent.html(contentWrapper);
        j01DialogResize(dlg);
    }else if (response.nextURL && response.closeDialog) {
        // handle redirect and support close dialog. note a plain redirect
        // with "window.location = response.nextURL;" whould not work if we
        // use urls like ../index.html#6/shortComments.html?j=1&c=r&_suid=..
        // including anchors if we enable history support
        j01DialogClose(response.nextURL);
        return false;
    }else if (response.nextURL) {
        // load nextURL into dialog
        proxy = getJSONRPCProxy(response.nextURL);
        proxy.addMethod('j01DialogContent', j01DialogRenderContent, 'j01DialogRenderContent');
        try {
            params = j01URLToArray(response.nextURL);
        } catch(err) {
            // j01URLToArray not available
            params  = false;
        }
        if (params) {
            proxy.j01DialogContent(params);
        }else{
            proxy.j01DialogContent();
        }
        return false;
    }else if (response.closeDialog && response.content) {
        // handle close dialog and content
        if (response.contentTargetExpression) {
            var contentTarget = $(response.contentTargetExpression);
        }else{
            var contentTarget = $('#content');
        }
        j01DialogClose();
        contentTarget.empty();
        contentTarget.html(response.content);
    }else if (response.closeDialog) {
        // handle close dialog without content
        j01DialogClose();
        return false;
    }else if (response.content) {
        // handle new dialog content
        dlgContent.empty();
        dlgContent.html(response.content);
        // apply close handler if new content contains j01DialogClose
        dlgContent.find('#j01DialogClose').click(function(e){
            j01DialogClose();
        });
        j01DialogResize(dlg);
    }
    $(window).bind('scroll', function(){
        // bind center to scroll event
        j01DialogCenter(dlg);
    });
};

// J01Dialog
var J01Dialog = function(settings) {
    this.settings = $.extend({
        j01DialogExpression: false,
        url: false,
        loadDialogWithJSONRPC: true,
        params: false
    }, settings);

    this.dlgHolder = false;
    this.dlg = false;
    this.hIFrame = false;
};

J01Dialog.prototype.setupOverlay = function() {
    // set overlay
    var self = this;
    var j01DialogOverlay = $('#j01DialogOverlay');
    if (j01DialogOverlay.length == 0){ 
        j01DialogOverlay = $('<div id="j01DialogOverlay"></div>');
        $(document.body).append(j01DialogOverlay);
        j01DialogOverlay.click(function(e){
            self.hideDialog(e);
        });
    }
};

J01Dialog.prototype.tearDownOverlay = function() {
    $("#j01DialogOverlay").unbind("click").remove();
};

J01Dialog.prototype.setupModel = function() {
    if (jQuery.browser.msie && jQuery.browser.version < 7) {//if IE 6
        if (!this.hIFrame) {
            this.hIFrame = $('<iframe id="j01DialogHiddenIFrame" scrolling="no" frameborder="0" style="position:absolute; top:0px; left:0px;-moz-opacity:0.7; opacity:0.7;filter:alpha(opacity=70);background:#fff;"></iframe>');
            this.hIFrame.appendTo(document.body);                 
        }
    }
};

J01Dialog.prototype.tearDownModel = function() {
    if (this.hIFrame)    
        this.hIFrame.remove();
};

J01Dialog.prototype.setupCloseByEscKey = function() {
    // apply ESC key
    var self = this;
    document.onkeydown = function(e){
        if(!e){
            e = window.event;
        }
        keycode = e.keyCode ? e.keyCode : e.which;  
        if(keycode == 27){
            self.hideDialog();
        }   
    };
};

// TODO: make this a global method
J01Dialog.prototype.getPageSize = function(win, doc) {
    var xScroll;
    if (win.innerHeight && win.scrollMaxX) {    
        xScroll = win.innerWidth + win.scrollMaxX;
    } else if (doc.body.scrollWidth > doc.body.offsetWidth){ // all but Explorer Mac
        xScroll = doc.body.scrollWidth;
    } else { // Explorer Mac...would also work in Explorer 6 Strict, Mozilla and Safari
        xScroll = doc.body.offsetWidth;
    }
    var yScroll;
    if (win.innerHeight && win.scrollMaxY) {    
        yScroll = win.innerHeight + win.scrollMaxY;
    } else if (doc.body.scrollHeight > doc.body.offsetHeight){ // all but Explorer Mac
        yScroll = doc.body.scrollHeight;
    } else { // Explorer Mac...would also work in Explorer 6 Strict, Mozilla and Safari
        yScroll = doc.body.offsetHeight;
    }

    var winWidth, winHeight;
    if (win.innerHeight) {  // all except Explorer
        if(doc.documentElement.clientWidth){
            winWidth = doc.documentElement.clientWidth;
        } else {
            winWidth = win.innerWidth;
        }
        winHeight = win.innerHeight;
    } else if (doc.documentElement && doc.documentElement.clientHeight) { // Explorer 6 Strict Mode
        winWidth = doc.documentElement.clientWidth;
        winHeight = doc.documentElement.clientHeight;
    } else if (doc.body) { // other Explorers
        winWidth = doc.body.clientWidth;
        winHeight = doc.body.clientHeight;
    }
    
    // for small pages with total height less then height of the viewport
    var pageWidth, pageHeight;
    if(yScroll == 0){
        pageHeight = winHeight;
    } else { 
        pageHeight = yScroll;
    }

    // for small pages with total width less then width of the viewport
    if(xScroll == 0){ 
        pageWidth = winWidth;        
    } else {
        pageWidth = xScroll;
    }

    return [pageWidth, pageHeight];
};

J01Dialog.prototype.centerDialog = function() {
    var wh = $(window).height();
    var ww = $(window).width();
    var dh = this.dlg.height();
    var dw = this.dlg.width();
    if (wh < dh || ww < dw) {
        // don't center if dialog is bigger then the window.
        // this prevents that the dialog get re-positioned during scrolling
        return false;
    }
    var top = wh/2 - dh/2 + $(window).scrollTop();
    var left = ww/2 - dw/2 + $(window).scrollLeft();
    // never use a negativ top or left value
    top = Math.max(top, 0);
    left = Math.max(left, 0);
    this.dlg.css({left: left +'px', top: top +'px'});
    if (this.hIFrame) {
        this.hIFrame.css({top: top +"px", left: left +"px"});
    }
};

J01Dialog.prototype.resizeIFrame = function(iframe) {
    var self = this;
    $(iframe).unbind('load');
    arrayPageSize = self.getPageSize(iframe.contentWindow, iframe.contentWindow.document);
    w = arrayPageSize[0];
    h = arrayPageSize[1];
    self.showFrameDialog(w, h);
    $(iframe).load(function(){
        self.resizeIFrame(iframe);
    });
};

J01Dialog.prototype.loadDialog = function(url) {
    // load content by ajax or JSON-RPC
    // load dialog
    if (this.settings.j01DialogExpression) {
        return $(this.settings.j01DialogExpression);
    }
    // take url from settings
    if (!url || url === 'undefined') {
        var url = this.settings.url;
    }
    // url could still be false
    if (url && this.settings.loadDialogWithJSONRPC) {
        proxy = getJSONRPCProxy(url);
        proxy.addMethod('j01Dialog', false, 'j01Dialog');
        if (this.settings.params) {
            var params = this.settings.params;
        }else {
            var params = {};
        }
        try {
            params = j01URLToArray(url, params);
        }catch(err) {
            // j01URLToArray not available
            params = false;
        }
        if (params) {
            var content = proxy.j01Dialog(params);
        }else{
            var content = proxy.j01Dialog();
        }
        if (content.message) {
            if (content.data && content.data.i18nMessage) {
                alert(content.data.i18nMessage);
            }else{
                alert(content.message);
            }
            return false;
        }else{
            return $(content);
        }
    }else if (url) {
        if (url.indexOf("?") > -1) {
            url += "&random=" + (new Date().getTime());
        }else{
            url += "?random=" + (new Date().getTime());
        }
        var content = $.ajax({url: url, async: false}).responseText;
        return $(content);
    }else {
        alert("No url or expression given for load dialog");
        return false;
    }
};

J01Dialog.prototype.showDialog = function() {
    // use j01ResizeDialog and use dlg and probably hIFrame as argument,
    // or even better use findHIFrame
    this.dlg.css({'width': '', 'height': ''});
    // set calculated new width
    width = this.dlg.width();
    height = this.dlg.height();
    this.dlg.css({'width': this.dlg.width() +'px',
                  'height': this.dlg.height() +'px'});

    // XXX: animation seems to be broken in jquery 1.8.0 and 1.8.1
    // this.dlg.animate({opacity: 'show'}, 'slow');
    this.dlg.show();
    var top = $(window).height()/2 - this.dlg.height()/2 + $(window).scrollTop();
    var left = $(window).width()/2 - this.dlg.width()/2 + $(window).scrollLeft();
    // never use a negativ top or left value
    top = Math.max(top, 0);
    left = Math.max(left, 0);
    this.dlg.css({'left': left +'px', 'top': top +'px'});
    if (this.hIFrame) {
        this.hIFrame.css({top: top +'px', left: left +'px',
                          width: width +'px', height: height +'px'});
    }
};

J01Dialog.prototype.showFrameDialog = function(width, height) {
    var self = this;
    // use j01ResizeDialog and use dlg as argument,
    // find iframe if available
    // moz does not apply the correct mesured height, give it a bit more
    $('iframe#j01DialogIFrame', this.dlg).css({'width': width +'px',
                                               'height': height +22 +'px'});
    // XXX: animation seems to be broken in jquery 1.8.0 and 1.8.1
    //this.dlg.animate({opacity: 'show'}, 'slow');
    this.dlg.show();
    var top = $(window).height()/2 - this.dlg.height()/2 + $(window).scrollTop();
    var left = $(window).width()/2 - this.dlg.width()/2 + $(window).scrollLeft();
    // never use a negativ top or left value
    top = Math.max(top, 0);
    left = Math.max(left, 0);
    this.dlg.css({'left': left +'px', 'top': top +'px'});
    if (this.hIFrame) {
        this.hIFrame.css({top: top +'px', left: left +'px',
                          width: width +'px', height: height +'px'});
    }
    // apply onload function
    $('iframe#j01DialogIFrame', this.dlg).load(function(){
        self.resizeIFrame(this)
    });
};

J01Dialog.prototype.setupDialog = function(url) {
    // render dialog
    var self = this;
    this.dlg = this.loadDialog(url);
    if (!this.dlg) {
        return false;
    }
    this.setupOverlay();
    isIFrame = false;
    if (this.dlg.find('iframe').get(0)) {
        isIFrame = true;
    }
    this.dlg.hide();
    // setup dialog container
    this.dlgHolder = $('#j01DialogHolder');
    if (this.dlgHolder.length == 0){ 
        this.dlgHolder = $('<div id="j01DialogHolder"></div>');
        $(document.body).append(this.dlgHolder);   
    }
    this.dlgHolder.append(this.dlg);
    // apply control handler
    $('#j01DialogClose', this.dlg).click( function(e){
        self.doClose(e);
    });
    // setup iframe
    this.setupModel();
    this.setupCloseByEscKey();

    if (isIFrame) {
        this.showFrameDialog(this.dlg.width(), this.dlg.height());
    }else {
        this.showDialog();
    }
    $(window).bind('resize', function(){
        self.centerDialog();
    })
    $(window).bind('scroll', function(){
        self.centerDialog();
    })
};

J01Dialog.prototype.hideDialog = function() {
    $(window).unbind( 'resize');
    $(window).unbind( 'scroll');
    this.dlg.find('#j01DialogControls').unbind('click');
    this.tearDownOverlay();
    this.dlg.hide();
    this.dlg.remove();
    this.dlgHolder.remove();
    this.tearDownModel();
    document.onkeydown = "";
    return false;
};

J01Dialog.prototype.doClose = function(e) {
    var self = this;
    var sourceobj=window.event? window.event.srcElement : e.target;
    if (/Close/i.test(sourceobj.getAttribute("title"))) {
       self.hideDialog();
    }
    return false;
};

/**
 * j01LoadContent without delegation (not recommended)
 * this plugin does not re bind handlers for new loaded content
 */
(function($) {
$.fn.j01Dialog = function(settings) {
    // setup loader with given settings
    return this.each(function(){
        // apply event handler to links
        $(this).click(function(event){
            var dialog = new J01Dialog(settings);
            var url = $(this).attr('href');
            dialog.setupDialog(url);
            event.preventDefault();
            return false;
        });
    });
};
})(jQuery);

/**
 * j01DialogOn (only recommended for non click events on links)
 * This method does not get the href as url from <a> tag. You must
 * define j01DialogExpression or a url in settings.
 */
(function($) {
$.fn.j01DialogOn = function(events, selector, settings) {
    // apply delegated event handler
    return this.on(events, selector, function(event){
        // XXX: implement j01DialogExpression or url value check
        var dialog = new J01Dialog(settings);
        dialog.setupDialog(dialog.settings.url);
        event.preventDefault();
        return false;
    });
};
})(jQuery);

/**
 * j01DialogOnClick uses delegation pattern (recommended) and works on new
 * loaded content
 */
(function($) {
$.fn.j01DialogOnClick = function(selector, settings) {
    // apply delegated event handler to click event
    if(typeof selector === "object"){
        // only settings given, use default selector and adjust settings
        var settings = selector;
        var selector = 'a.j01DialogLink';
    }else if(typeof selector === "undefined"){
        // non argument given, use default selector
        var selector = 'a.j01DialogLink';
    }
    return this.on('click', selector, function(event){
        var dialog = new J01Dialog(settings);
        if ($(this).is('a')){
            var url = $(this).attr('href');
        }else{
            var url = dialog.settings.url;
        }
        dialog.setupDialog(url);
        event.preventDefault();
        return false;
    });
};
})(jQuery);

//j01Dialog without any event handler (non JQuery)
function j01Dialog(settings) {
    // setup and resize
    var dialog = new J01Dialog(settings);
    dialog.setupDialog(dialog.settings.url);
    dialog.centerDialog();
};



(function($) {
$.fn.j01DialogContent = function (settings) {
    settings = $.extend({
        targetContainerExpression: '#j01DialogContent',
        callback: j01DialogRenderContent,
        requestId: 'j01DialogContent'
    }, settings);

    // load content from server via jsonrpc
    function loadContent(self) {
        url = $(self).attr('href');
        proxy = getJSONRPCProxy(url);
        proxy.addMethod('j01DialogContent', settings.callback, settings.requestId);
        try {
            params = j01URLToArray(url);
        } catch(err) {
            // j01URLToArray not available
            params  = false;
        }
        if (params) {
            proxy.j01DialogContent(params);
        }else{
            proxy.j01DialogContent();
        }
    }

    // apply event handler to links
    return this.each(function(){
        $(this).click(function(){
            loadContent(this);
            return false;
        });
    });
};
})(jQuery);
