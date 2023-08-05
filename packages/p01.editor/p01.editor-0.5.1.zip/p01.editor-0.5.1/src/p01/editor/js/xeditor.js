// editor implementation using contentEditable and a marker for
// editable elements

var activeXEditor = null;
var activeXEditorLinkURL = null;
var activeXEditorLinkTarget = null;
var activeXEditorMediaData = null;
var activeXEditorFlashData = null;

function insertXEditorHTML(sHTML) {
    activeXEditor.insertHTML(sHTML);
}
function pasteXEditorHTML(sHTML) {
    activeXEditor.pasteHTML(sHTML);
}
function insertXEditorLink(url, t) {
    activeXEditor.insertLink(url, t);
}
function updateXEditorMedia(sHTML) {
    activeXEditor.updateMedia(sHTML);
}
function updateXEditorFlash(sHTML) {
    activeXEditor.updateMedia(sHTML);
}

(function($){
    // xEditor class
    var xEditor = function(element, settings) {
        $.extend(this, {
            settings: settings,
            createDOM: function() {
                this.textarea = element;
                var fieldName = $(this.textarea).attr('name');
                this.container = document.createElement("div");
                this.iframe = document.createElement("iframe");
                this.input = document.createElement("input");
                $(this.textarea).addClass('xEditorTextarea');
                $(this.textarea).attr('name', fieldName + "EditorTextarea");
                $(this.textarea).hide();
                $(this.input).attr({
                    type: 'hidden',
                    name: fieldName,
                    value: $(this.textarea).attr('value') // old textarea value
                });
                $(this.iframe).addClass('xEditorIFrame');
                $(this.iframe).attr('frameBorder', 'no');
                $(this.container).addClass(settings.containerClass);
                this.toolbar = new xEditorToolbar(this);
                $(this.container).append(this.toolbar.itemsList);
                $(this.container).append(this.iframe);
                $(this.container).append(this.input);
                $(this.container).hide();
                $(this.textarea).after(this.container).remove();
            },

            writeDocument: function() {
                // HTML template into which the HTML Editor content is inserted
                var documentTemplate = ""
                documentTemplate += "<html>"
                documentTemplate += "<head>"
                documentTemplate += "INSERT:STYLESHEET:END"
                documentTemplate += "</head>"
                documentTemplate += "<body>"
                documentTemplate += "INSERT:CONTENT:END"
                documentTemplate += "</body>"
                documentTemplate += "</html>";
                // Insert dynamic variables/content into document
                // IE needs stylesheet to be written inline
                if ($.browser.msie) {
                    documentTemplate = documentTemplate.replace(
                        /INSERT:STYLESHEET:END/,
                        '<link rel="stylesheet" type="text/css" href="' + settings.stylesURL + '"></link>');
                }else{
                    documentTemplate = documentTemplate.replace(/INSERT:STYLESHEET:END/, "");
                }
                documentTemplate = documentTemplate.replace(/INSERT:CONTENT:END/, $(this.input).val());
                // prevent memory leak based on body
                $(this.iframe.contentWindow.document.body).remove();
                this.iframe.contentWindow.document.open();
                this.iframe.contentWindow.document.write(documentTemplate);
                this.iframe.contentWindow.document.close();
                // In Firefox stylesheet needs to be loaded separate to other
                // HTML, because if it's loaded inline it causes Firefox to have
                // problems with an empty document
                if (!$.browser.msie) {
                    $(this.iframe.contentWindow.document).find('head').append(
                        $(this.iframe.contentWindow.document.createElement("link")).attr({
                            "rel": "stylesheet",
                            "type": "text/css",
                            "href": settings.stylesURL
                        })
                    );
                }
                this.removeChunk();
            },

            makeEditable: function(resubmited) {
                var self = this;

                if (!resubmited) {
                    setTimeout((function(){self.makeEditable(true)}), 250);
                    return false;
                }
                var body = $(this.iframe.contentWindow.document).find("body");
                try {
                    body.attr("contentEditable", true)
                } catch (e) {
                    // mozilla can't immediately change designMode on newly 
                    // created iframes
                    setTimeout((function(){self.makeEditable(true)}), 250);
                    return false;
                }

                this.convertSPANs(false);

                $(this.container).show();
                $(this.textarea).show();
                // document event
                $(this.iframe.contentWindow.document).bind('mousedown', function(e){
                    self.onMouseDown(e);
                });
                $(this.iframe.contentWindow.document).bind('mouseup', function(e){
                    self.onMouseUp(e);
                });
                $(this.iframe.contentWindow.document).bind('keyup', function(e){
                    self.onKeyUp(e);
                });
                $(this.iframe.contentWindow.document).bind('keydown',function(e){
                    self.onKeyDown(e);
                });
                $(this.iframe.contentWindow.document).bind('cut',function(e){
                    self.onCut(e);
                });
                $(this.iframe.contentWindow.document.body).bind('paste',function(e){
                    self.onPaste(e);
                });
                $(this.iframe.contentWindow.document.body).bind('blur',function(e){
                    self.onBlur(e);
                });
                this.locked = false;
            },

            onKeyDown: function(e) {
                if (this.cleaning) {
                    return;
                }
                if (!this.arrUndo[0]) {
                    // init undo
                    this.saveForUndo();
                }
                var self = this;
                var keyCode = e.which;
                var shiftKey = e.shiftKey;
                var ctrlKey = e.ctrlKey;
                if (this.wysiwyg) {
                    // wysiwyg mode
                    switch(keyCode) {
                        case 86:
                            if(ctrlKey){
                                // ctrl-v, 
                                // cache original content and cleanup in onKeyUp
                                var body = $(this.iframe.contentWindow.document).find("body");
                                self.textBeforePaste = body.html();
                            }
                            break;
                        default:
                            break;
                    }
                }
            },

            onKeyUp: function(e) {
                if (this.textBeforePaste) {
                    this.pasteProcessor();
                    this.makeEditable();
                    this.resizeContent();
                }
                this.toolbar.checkState(this);
            },

            onMouseDown: function(e) {
                if (this.locked) {
                    return;
                }
            },

            onMouseUp: function(e) {
                if (this.locked) {
                    return;
                }
                this.resizeContent();
                this.toolbar.checkState(this);
            },

            onCut: function(e) {
                this.saveForUndo();
            },

            onPaste: function(e) {
                // cache original content
                var body = $(this.iframe.contentWindow.document).find("body");
                this.textBeforePaste = body.html();
                // The real paste happens after this method get processed. 
                // Let's use a timeout and hope the paste happens since then
                var self = this;
                setTimeout(function(){
                    self.pasteProcessor();
                    self.makeEditable();
                    self.resizeContent();
                }, 250);
            },

            onBlur: function(e) {
                this.updateEditor(e);
                this.toolbar.resetButtonStates();
            },

            resizeContent: function() {
                // resize if smaller then 200px otherwise skip it
                if (this.wysiwyg) {
                    var ih = $(this.iframe).height();
                    var body = $(this.iframe.contentWindow.document).find("body");
                    var sh = body.prop('scrollHeight');
                    if (ih != sh || ih < 200) {
                        if ($.browser.msie) {
                            // ie 9.0, or it will grow each time
                            sh = sh - 10;
                        }
                        if (sh < 200) {
                            sh = 200;
                        }
                        $(this.iframe).height(sh);
                        $(this.container).height(sh + 27);
                        this.isResized = true;
                        this.toolbar.setButtonState('resize', 1);
                    }
                }else{
                    var ta = $(this.textarea);
                    var th = $(this.textarea).height();
                    var sh = ta.prop('scrollHeight');
                    if (th != sh || sh < 200) {
                        sh = sh + 10;
                        if (sh < 200) {
                            sh = 200;
                        }
                        ta.height(sh);
                        $(this.container).height(sh + 27);
                        this.isResized = true;
                        this.toolbar.setButtonState('resize', 1);
                    }
                }
            },

            pasteProcessor: function() {
                if (this.textBeforePaste && this.settings.siteURL) {
                    var textBefore = this.textBeforePaste;
                    var body = $(this.iframe.contentWindow.document).find("body");
                    var textAfter = body.html();
                    proxy = getJSONRPCProxy(this.settings.siteURL);
                    proxy.addMethod(this.settings.doPasteMethodName);
                    // doXEditorPaste
                    var newText = proxy[this.settings.doPasteMethodName](textBefore, textAfter);
                    if (!newText) {
                        newText = textBefore;
                    }
                    // set new or original text
                    body.html(newText);
                    this.textBeforePaste = null;
                }
            },

            modifyFormSubmit: function() {
                var self = this;
                var form = $(this.container).parents('form');
                form.submit(function() {
                    self.updateEditor();
                    return false;
                });
            },

            switchMode: function() {
                if (!this.locked) {
                    this.locked = true;
                    // switch to textarea
                    if (this.wysiwyg) {
                        this.updateEditor();
                        $(this.textarea).val($(this.input).val());
                        $(this.iframe).after(this.textarea).remove();
                        this.toolbar.disable();
                        this.wysiwyg = false;
                        this.locked = false;
                        this.resizeContent();
                    }
                    // switch to wysiwyg
                    else {
                        this.updateEditor();
                        $(this.textarea).after(this.iframe).remove();
                        this.writeDocument();
                        this.toolbar.enable();
                        this.wysiwyg = true;
                        this.makeEditable();
                        this.resizeContent();
                    }
                }
            },

            removeAll: function() {
                if (this.wysiwyg) {
                    this.saveForUndo();
                    $(this.iframe.contentWindow.document).find("body").html('');
                    $(this.iframe).height(200);
                    $(this.container).height(227);
                }
            },

            doInsertHTML: function(sHTML) {
                if (this.wysiwyg) {
                    this.saveForUndo();
                    var body = $(this.iframe.contentWindow.document).find("body");
                    if (!body.children().size()) {
                        body.html(sHTML);
                    }
                    else if (this.setFocus()) {
                        // insert given html content into selected location
                        var selection, range;
                        if (this.iframe.contentWindow.document.selection) {
                            selection = this.iframe.contentWindow.document.selection;
                            var range = selection.createRange();
                            range.collapse(false);
                            range.pasteHTML(sHTML);
                        }else{
                            this.iframe.contentWindow.focus();
                            selection = this.iframe.contentWindow.getSelection();
                            range = selection.getRangeAt(0);
                            range.collapse(false);
                            var docFrag = range.createContextualFragment(sHTML);
                            range.collapse(true);
                            var lastNode = docFrag.childNodes[docFrag.childNodes.length-1];
                            range.insertNode(docFrag);
                            // collaps to the end
                            selection.collapseToEnd();
                            if (lastNode.nodeType == Node.TEXT_NODE) {
                                range = this.iframe.contentWindow.document.createRange();
                                range.setStart(lastNode, lastNode.nodeValue.length);
                                range.setEnd(lastNode, lastNode.nodeValue.length);
                                oSel = this.iframe.contentWindow.getSelection();
                                oSel.removeAllRanges();
                                oSel.addRange(range);
                                oSel.collapseToEnd();
                                var comCon=range.commonAncestorContainer;
                                if(comCon && comCon.parentNode) {
                                    try {
                                        comCon.parentNode.normalize();
                                    }catch(e) {}
                                }
                            }
                        }
                    }
                }
            },

            // insert html WITHOUT paste processor concept (trusted clipboard)
            insertHTML: function(sHTML) {
                if (this.wysiwyg) {
                    // insert HTML including makeEditable and resize call
                    this.doInsertHTML(sHTML);
                    this.makeEditable();
                    this.resizeContent();
                }
            },

            // insert html WITH paste processor concept (copy/paste or textarea)
            pasteHTML: function(sHTML) {
                if (this.wysiwyg) {
                    var body = $(this.iframe.contentWindow.document).find("body");
                    // use paste processor concept
                    this.textBeforePaste = body.html();
                    this.doInsertHTML(sHTML);
                    this.pasteProcessor();
                    this.makeEditable();
                    this.resizeContent();
                }
            },

            insertLink: function(url, t) {
                if (this.wysiwyg) {
                    this.setFocus();
                    var txt = $(this.iframe).getSelectedText();
                    if (txt == "") {
                        return;
                    }
                    this.saveForUndo();
                    if (url) {
                        this.iframe.contentWindow.document.execCommand("CreateLink", false, url);
                        var node = $(this.iframe).getSelectedNode();
                        if (!node.is('A')) {
                            if (node.parent().is('A')){
                                node = node.parent();
                            }else{
                                node = node.parent().find('a')
                            }
                        }
                        if (node && t) {
                            // apply target if any
                            node.attr('target', t);
                        }else{
                            node.removeAttr('target');
                        }
                        this.toolbar.setButtonState('link', 4);
                    }else{
                        this.iframe.contentWindow.document.execCommand("Unlink", false, null);
                        this.toolbar.setButtonState('link', 1);
                        return;
                    }
                }
            },

            updateMedia: function(sHTML) {
                if (this.wysiwyg) {
                    this.setFocus();
                    this.saveForUndo();
                    var node = $(this.iframe).getSelectedNode();
                    node.after(sHTML).remove();
                }
            },

            openJ01Dialog: function(url) {
                // setup j01Dialog
                var dialog = new J01Dialog();
                dialog.setupDialog(url);
                dialog.centerDialog();
            },

            getEditableRangeAndNode: function() {
                if (!this.wysiwyg) {
                    return false;
                }
                var type = false;
                var range = false;
                var node = false;
                if (this.iframe.contentWindow.document.selection) {
                    // ie
                    var selection = this.iframe.contentWindow.document.selection;
                    type = selection.type
                    range = selection.createRange();
                    try {
                        if (selection.type == 'None' || selection.type == 'Text') {
                            var node = range.parentElement();
                        }else{
                            var node = range.item(0);
                        }
                    }catch (e) {
                        return false;
                    }
                }
                // moz
                else {
                    try {
                        var selection = this.iframe.contentWindow.getSelection();
                        range = selection.getRangeAt(0);
                        node = range.commonAncestorContainer;
                    }
                    catch (e) {
                        return false;
                    }
                }
                if (!node) {
                    return;
                }
                return {'type':type, 'range':range, 'node':$(node)};
            },

            isEditable: function() {
                var arr = this.getEditableRangeAndNode();
                if (arr) {
                    return true;
                }else{
                    return false;
                }
            },

            // bookmark the selection before we leave the selected content
            bookmarkSelection: function() {
                var arr = this.getEditableRangeAndNode();
                if (arr.range) {
                    if (arr.type == "None" || arr.type == "Text") {
                      this.rangeBookmark = arr.range;
                      this.controlBookmark = null;
                    } else {
                      this.controlBookmark = arr.range;
                      this.rangeBookmark = null;
                    }
                    return arr.node;
                }else{
                    return false;
                }
            },

            setFocus: function() {
                if (this.iframe.contentWindow.document.selection) {
                    // IE needs more to do
                    this.iframe.contentWindow.focus();
                    try {
                        if(this.rangeBookmark!=null) {
                            var oSel= this.iframe.contentWindow.document.selection;
                            var oRange = oSel.createRange();
                            var bmRange = this.rangeBookmark;
                            if(bmRange.parentElement()) {
                                oRange.moveToElementText(bmRange.parentElement());
                                oRange.setEndPoint("StartToStart", bmRange);
                                oRange.setEndPoint("EndToEnd", bmRange);
                                oRange.select();
                            return true;
                            }
                        } else if(this.controlBookmark!=null) {
                            var oSel = this.iframe.contentWindow.document.body.createControlRange();
                            oSel.add(this.controlBookmark);
                            oSel.select();
                            return true;
                        }
                    } catch(e) {
                        return false;
                    }
                }else{
                    // focus() is enoug for firefox
                    this.iframe.contentWindow.focus();
                    return true;
                }
            },

            convertSPANs: function(replaceSpans) {
                // convert spans to semantics in mozilla
                // this is required beacuse moz can only handle styled span in
                // execCommand
                if (!$.browser.msie) {
                    var iframe = this.iframe;
                    this.saveForUndo();
                    if (replaceSpans) {
                        // Replace styled spans with their semantic equivalent
                        var spans = $(iframe.contentWindow.document).find('span');
                        if(spans.length) {
                            spans.each(function() {
                                var children = $(this).contents();
                                var replacementElement = null;
                                var parentElement = null;
                                var style = "";
                                if ($(this).attr("style") != undefined){
                                    style = $(this).attr("style").replace(/\s*/gi, '');
                                }
                                // Detect type of span style
                                switch (style) {
                                    case "font-style:italic;":
                                        parentElement = replacementElement = iframe.contentWindow.document.createElement("em");
                                        break;
        
                                    case "font-weight:bold;":
                                        parentElement = replacementElement = iframe.contentWindow.document.createElement("strong");
                                        break;
        
                                    case "font-weight:bold;font-style:italic;":
                                        emElement = iframe.contentWindow.document.createElement('em');
                                        strongElement = iframe.contentWindow.document.createElement('strong');
                                        $(emElement).append(strongElement);
                                        parentElement = emElement;
                                        replacementElement = strongElement;
                                        break;
        
                                    case "font-style:italic;font-weight:bold;":
                                        emElement = iframe.contentWindow.document.createElement('em');
                                        strongElement = iframe.contentWindow.document.createElement('strong');
                                        $(emElement).append(strongElement);
                                        parentElement = emElement;
                                        replacementElement = strongElement;
                                        break;
        
                                    default:
                                        break;
                                }
                                children.each(function() {
                                    $(replacementElement).append(this);
                                });
                                $(this).before(parentElement);
                                $(this).remove();
                            });
                        }
                    }
                    else {
                        // replace em and strong tags with styled spans
                        $(iframe.contentWindow.document).find('em').each(function() {
                            var children = $(this).contents();
                            var span = iframe.contentWindow.document.createElement('span');
                            $(span).css('font-style', 'italic');
                            children.each(function() {
                                $(span).append(this);
                            });
                            $(this).after(span).remove();
                        });
    
                        $(iframe.contentWindow.document).find('strong').each(function() {
                            var children = $(this).contents();
                            var span = iframe.contentWindow.document.createElement('span');
                            $(span).css('font-weight', 'bold');
                            children.each(function() {
                                $(span).append(this);
                            });
                            $(this).after(span).remove();
                        });
                    }
                }
            },

            removeChunk: function() {
                // remove chunk added after click delete or
                // backspace button. Not sure where this comes from
                var body = $(this.iframe.contentWindow.document).find("body");
                var html = body.html();
                // remove leading and trailing whitespace
                html = html.replace(/^\s*/, "");
                html = html.replace(/\s*$/, "");
                // remove more then one empty space
                html = html.replace(/\s+/g, " ");
                // remove &nbsp;
                //html = html.replace(/(&nbsp;)*/g, "");
                html = html.replace(/^(&nbsp;)*/, "");
                html = html.replace(/(&nbsp;)+$/, "");
                $(this.iframe.contentWindow.document).find("body").html(html);
            },

            cleanSource: function() {
                this.cleaning = true;
                var html = "";
                this.convertSPANs(true);

                if (this.wysiwyg) {
                    var body = $(this.iframe.contentWindow.document).find("body");
                    html = body.html();
                }else {
                    html = $(this.textarea).val();
                }

                $.each(settings.undesiredTags, function(tag, action) {
                    $(html).find(tag).each(function() {
                        switch(action) {
                            case 'remove':
                                $(this).remove();
                                break;
                            case 'extractContent':
                                var parentTag = $(this);
                                parentTag.contents().each(function() {
                                    parentTag.before(this);
                                });
                                parentTag.remove();
                                break;
                            default:
                                $(this).remove();
                                break;
                        }
                    });
                });

                // replace new line
                html = html.replace(/\r\n/, "\n");
                // remove leading and trailing whitespace
                html = html.replace(/^\s*/, "");
                html = html.replace(/\s*$/, "");
                // remove more then one empty space
                html = html.replace(/\s+/g, " ");
                // remove &nbsp;
                //html = html.replace(/(&nbsp;)*/g, "");
                html = html.replace(/^(&nbsp;)*/, "");
                html = html.replace(/(&nbsp;)+$/, "");
                // remove comments
                html = html.replace(/<--.*-->/, "");
                // Remove style attribute inside any tag
                html = html.replace(/ style="[^"]*"/g, "");
                // replace improper BRs
                html = html.replace(/<br>/g, "<br />");
                html = html.replace(/<BR>/g, "<BR />");
                // remove BRs right before the end of blocks
                html = html.replace(/<br \/>\s*<\/(h1|h2|h3|h4|h5|h6|li|p)/g, "</$1");
                // Shift the <br /> at the end of an inline element just after it
                html = html.replace(/(<br \/>)*\s*(<\/[^>]*>)/g, "$2$1");
                // replace improper IMGs
                html = html.replace(/(<img [^>]+[^\/])>/g, "$1 />");
                html = html.replace(/(<IMG [^>]+[^\/])>/g, "$1 />");
                // Remove empty tags
                html = html.replace(/(<[^\/]>|<[^\/][^>]*[^\/]>)\s*<\/[^>]*>/g, "");

                if (this.wysiwyg) {
                    $(this.iframe.contentWindow.document).find("body").html(html);
                }
                else {
                    $(this.textarea).val(html);
                }
                $(this.input).val(html);
                this.cleaning = false;
            },

            updateEditor: function() {
                if (this.wysiwyg) {
                    this.cleanSource();
                }
                else {
                    $(this.input).val($(this.textarea).val());
                }
            },

            saveForUndo: function() {
                // arrUndo[0] allways contains the latest iframe content
                if (this.wysiwyg) {
                    var html = $(this.iframe.contentWindow.document.body).html();
                    if(this.arrUndo[0] == html) {
                        return;
                    }
                    // make place for latest content in arrUndo[0]
                    for(var i=20; i>1; i--){
                        this.arrUndo[i-1] = this.arrUndo[i-2];
                    }
                    // save for undo
                    this.arrUndo[0] = html;
                    //clear redo list
                    this.arrRedo = [];
                    this.toolbar.setButtonState('redo', 5);
                }
            },

            doUndo: function() {
                // arrUndo[0] allways contains the latest iframe content
                if (this.wysiwyg) {
                    if(!this.arrUndo[0]) {
                        return;
                    }
                    // first add the current html to redo
                    var html = $(this.iframe.contentWindow.document.body).html();
                    for(var i=20; i>1; i--) {
                        this.arrRedo[i-1] = this.arrRedo[i-2];
                    }
                    this.arrRedo[0] = html;

                    // get undo content and use as content
                    sHTML = this.arrUndo[0];
                    $(this.iframe.contentWindow.document.body).html(sHTML);
                    // move all items from arrUndo one down
                    for(var i=0; i<19; i++) {
                        this.arrUndo[i] = this.arrUndo[i+1];
                    }
                    this.arrUndo[19] = null;
                    var state = this.arrUndo[0]?1:5;
                    this.resizeContent();
                    this.toolbar.setButtonState('undo', state);
                    this.toolbar.setButtonState('redo', 1);
                }
            },

            doRedo: function() {
                // arrRedo[0] allways contains the latest undo content
                if (this.wysiwyg) {
                    if(!this.arrRedo[0]) {
                        return;
                    }

                    // first add the current html to undo
                    var html = $(this.iframe.contentWindow.document.body).html();
                    for(var i=20; i>1; i--) {
                        this.arrUndo[i-1] = this.arrUndo[i-2];
                    }
                    this.arrUndo[0] = html;

                    // get redo content and use as content
                    sHTML = this.arrRedo[0];
                    $(this.iframe.contentWindow.document.body).html(sHTML);
                    // move all items from arrRedo one down
                    for(var i=0; i<19; i++) {
                        this.arrRedo[i] = this.arrRedo[i+1];
                    }
                    this.arrRedo[19] = null;
                    var state = this.arrRedo[0]?1:5;
                    this.resizeContent();
                    this.toolbar.setButtonState('redo', state);
                    this.toolbar.setButtonState('undo', 1);
                }
            },

            init: function(settings) {
                // detects if designMode is available
                if (typeof(document.designMode) != "string" && document.designMode != "off"){
                    return;
                }
                this.arrUndo = [];
                this.arrRedo = [];
                this.locked = true;
                this.cleaning = false;
                this.isResized = false;
                this.wysiwyg = true;
                this.rangeBookmark = null;
                this.controlBookmark = null;
                this.textBeforePaste = null;
                this.createDOM();
                this.writeDocument();
                this.makeEditable();
                this.modifyFormSubmit();
                this.toolbar.setButtonState('resize', 4);
            }               
        });
        this.init();
    };

    // xEditorToolbar
    var xEditorToolbar = function(editor) {
        $.extend(this, {
            createDOM: function() {
                var self = this;
                // create toolbar ul element
                this.itemsList = document.createElement("ul");
                $(this.itemsList).addClass("xEditorToolbar");

                // create toolbar items
                $.each(this.xEditor.settings.toolbarItems, function(i, name) {
                    self.addButton(name);
                });
            },

            // set button state, 1=normal, 2=over 3=down 4=active 5=disable
            addButton: function(btnName) {
                if (btnName == '|') {
                    var menuItem = $(document.createElement("li"));
                    var div = $('<div class="spacer"></div>');
                    var imgSrc = this.xEditor.settings.imgURL +'/spacer.gif';
                    var img = $('<img unselectable="on" src="'+imgSrc+'" />');
                    div.append(img);
                    menuItem.append(div);
                    $(this.itemsList).append(menuItem);
                }else{
                    try {
                        var btn = $.xEditorToolbarItems[btnName];
                    }catch(e){
                        return false;
                    }
                    var menuItem = $(document.createElement("li"));
                    var btnTitle =  btn.label;
                    var link = $(document.createElement("div")).attr({
                        'title': btnTitle,
                        'class': btn.className,
                        'href': 'javascript:void(0)'
                    });
                    btn.editor = this.xEditor;
                    btn.btnName = btnName
                    btn.state = 1;
                    btn.height = 25;
                    btn.width = 29;
                    $(link).data('action', btn);
                    $(link).data('editor', this.xEditor);
                    link.bind('click', btn.action);
                    var imgSrc = this.xEditor.settings.imgURL +'/'+ btn.icon
                    var div = $('<div id="'+btnName+'" style="position:absolute;clip:rect(0px '+btn.width+'px '+btn.height+'px 0px);"></div>');
                    var img = $('<img unselectable="on" onmousedown="if(event.preventDefault) event.preventDefault();" src="'+imgSrc+'" style="position:relative;top:0px;left:0px" alt="'+btnTitle+'" title="'+btnTitle+'"/>');
                    img.hover(
                        function () {
                            if (btn.state != 5) {
                               img.css('top', "-25px");
                            }
                        },
                        function () {
                            img.css('top', -25*(btn.state-1)+"px");
                        }
                    );
                    div.append(img);
                    link.append(div);
                    menuItem.append(link);
                    $(this.itemsList).append(menuItem);
                }
            },

            checkState: function(xEditor, resubmited) {
                var self = this;
                if (!resubmited) {
                    // update selection before using the selection
                    setTimeout(function(){
                        self.checkState(xEditor, true); 
                        return true;
                    }, 250);
                    return true;
                }

                var selection = null;
                var range = null;
                var parentnode = null;

                // IE selections
                if (xEditor.iframe.contentWindow.document.selection) {
                    selection = xEditor.iframe.contentWindow.document.selection;
                    range = selection.createRange();
                    try {
                        parentnode = $(range.parentElement());
                    }
                    catch (e) {
                        return false;
                    }
                }
                // Mozilla selections
                else {
                    try {
                        selection = xEditor.iframe.contentWindow.getSelection();
                        range = selection.getRangeAt(0);
                        parentnode = $(range.commonAncestorContainer);
                    }
                    catch (e) {
                        return false;
                    }
                }

                while (parentnode.nodeType == 3) { // textNode
                    parentnode = parentnode.parent();
                }
                
                // reset all btn state
                $.each($.xEditorToolbarItems, function(i, btn) {
                    btn.state = 1;
                });
                // reset all icons
                $(self.itemsList).find('img').css('top', '0px');

                while (!parentnode.is('body')) {
                    if(parentnode.is('a')) {
                        self.setButtonState("link", 4);
                    }else if(parentnode.is('em')){
                        self.setButtonState("italic", 4);
                    }else if(parentnode.is('strong')) {
                        self.setButtonState("bold", 4);
                    }else if(parentnode.is('div') || parentnode.is('span') || parentnode.is('p')) {
                        if(parentnode.attr('align') == 'left') {
                            self.setButtonState("justifyLeft", 4);
                        }
                        else if(parentnode.attr('align') == 'center') {
                            self.setButtonState("justifyCenter", 4);
                        }
                        else if(parentnode.attr('align') == 'right') {
                            self.setButtonState("justifyRight", 4);
                        }
                        else if(parentnode.attr('align') == 'justify') {
                            self.setButtonState("justifyFull", 4);
                        }
                    }else if(parentnode.is('ol')) {
                        self.setButtonState("orderedlist", 4);
                        self.setButtonState("unorderedlist", 1);
                    }else if(parentnode.is('ul')) {
                        self.setButtonState("orderedlist", 1);
                        self.setButtonState("unorderedlist", 4);
                    }
                    // do we allow span in p tag?
                    else if(parentnode.is('span') || parentnode.is('p')) {
                        if(parentnode.css('font-style') == 'italic') {
                            self.setButtonState("italic", 4);
                        }
                        if(parentnode.css('font-weight') == 'bold') {
                            self.setButtonState("bold", 4);
                        }
                    }
                    parentnode = parentnode.parent();
                }
                var au = xEditor.arrUndo[0]?1:5;
                var ar = xEditor.arrRedo[0]?1:5;
                this.setButtonState('undo', au);
                this.setButtonState('redo', ar);
                
                // apply resize state
                if (this.isResized) {
                    this.setButtonState('resize', 4);
                }else{
                    this.setButtonState('resize', 1);
                }
            },

            // set button state, 1=normal, 2=over 3=down 4=active 5=disable
            setButtonState: function(btnName, state) {
                if (btnName) {
                    // set btn state
                    var btn = $.xEditorToolbarItems[btnName]
                    var className = btn.className;
                    btn.state = state;
                    // set icon state
                    $(btn).find('img').css('top', -25*(state-1)+"px");
                    var menuItem = $(this.itemsList).find('.' + className);
                    $(menuItem).find('img').css('top', -25*(state-1)+"px");
                }
            },

            resetButtonStates: function() {
                // reset all btn state
                var self = this;
                $.each($.xEditorToolbarItems, function(i, btn) {
                    self.setButtonState(btn.btnName, 1);
                });
            },

            disable: function() {
                // disable all btn state except mode switch
                var self = this;
                $.each($.xEditorToolbarItems, function(i, btn) {
                    self.setButtonState(btn.btnName, 5);
                });
                this.setButtonState('htmlsource', 4);
            },

            enable: function() {
                // checkState knows how to switch states
                this.checkState(this.xEditor);
            },
            
            init: function(editor) {
                this.xEditor = editor;
                this.createDOM();
                this.setButtonState('undo', 5);
                this.setButtonState('redo', 5);
            }
        });
        this.init(editor);
    };

    // xEditorToolbarItems class, can be extended using 
    // $.extend($.xEditorToolbarItems, { (...) }
    var xEditorToolbarItems = function() {
        // Defines singleton logic
        var xEditorToolbarItemsClass = this.constructor;
        if(typeof(xEditorToolbarItemsClass.singleton) != 'undefined') {
            return xEditorToolbarItemsClass.singleton;
        }
        else {
            xEditorToolbarItemsClass.singleton = this;
        }
        // Extends class with items properties, will only be executed once
        $.extend(xEditorToolbarItemsClass.singleton, {
            selector: {
                action: function() {
                    var isEmpty = false;
                    var editor = $.data(this, 'editor');
                    activeXEditor = editor;
                    var isSelected = editor.bookmarkSelection();
                    if (isSelected == false) {
                        var body = $(editor.iframe.contentWindow.document).find("body");
                        if (body.html()) {
                            // html available but nothing selected
                            return false;
                        }
                    }
                    var cbURL = editor.settings.cbURL;
                    editor.openJ01Dialog(cbURL);
                },
                className: 'xEditorButtonClipBoard',
                icon: 'btnCustomObject.gif',
                label: 'Select'
            },
            bold: {
                action: function(){
                    var editor = $.data(this, 'editor');
                    if(!editor.isEditable()) {
                        return;
                    }
                    editor.saveForUndo();
                    editor.iframe.contentWindow.document.execCommand('bold', false, null);
                    editor.toolbar.setButtonState("bold", 4);
                },
                className: 'xEditorButtonBold',
                icon: 'btnBold.gif',
                type: 'TGL',
                label: 'Bold'
            },
            italic: {
                action: function(){
                    var editor = $.data(this, 'editor');
                    if(!editor.isEditable()) {
                        return;
                    }
                    editor.saveForUndo();
                    editor.iframe.contentWindow.document.execCommand('italic', false, null);
                    editor.toolbar.setButtonState('italic', 4);
                },
                className: 'xEditorButtonItalic',
                icon: 'btnItalic.gif',
                label: 'Italic'
            },
            orderedlist: {
                action: function(){
                    var editor = $.data(this, 'editor');
                    if(!editor.isEditable()) {
                        return;
                    }
                    editor.saveForUndo();
                    editor.iframe.contentWindow.document.execCommand(
                        'insertorderedlist', false, null);
                },
                className: 'xEditorButtonOrderedList',
                icon: 'btnOrderedList.gif',
                label: 'Ordered List'
            },
            unorderedlist: {
                action: function(){
                    var editor = $.data(this, 'editor');
                    if(!editor.isEditable()) {
                        return;
                    }
                    editor.saveForUndo();
                    editor.iframe.contentWindow.document.execCommand(
                        'insertunorderedlist', false, null);
                },
                className: 'xEditorButtonUnorderedList',
                icon: 'btnUnorderedList.gif',
                label: 'Unordered List'
            },
            justifyLeft: {
                action: function(){
                    var editor = $.data(this, 'editor');
                    if(!editor.isEditable()) {
                        return;
                    }
                    editor.saveForUndo();
                    editor.iframe.contentWindow.document.execCommand(
                        'JustifyLeft', false, null);
                },
                className: 'xEditorButtonJustifyLeft',
                icon: 'btnJustifyLeft.gif',
                label: 'Justify  Left'
            },
            justifyCenter: {
                action: function(){
                    var editor = $.data(this, 'editor');
                    if(!editor.isEditable()) {
                        return;
                    }
                    editor.saveForUndo();
                    editor.iframe.contentWindow.document.execCommand(
                        'JustifyCenter', false, null);
                },
                className: 'xEditorButtonJustifyCenter',
                icon: 'btnJustifyCenter.gif',
                label: 'Justify  Center'
            },
            justifyRight: {
                action: function(){
                    var editor = $.data(this, 'editor');
                    if(!editor.isEditable()) {
                        return;
                    }
                    editor.saveForUndo();
                    editor.iframe.contentWindow.document.execCommand(
                        'JustifyRight', false, null);
                },
                className: 'xEditorButtonJustifyRight',
                icon: 'btnJustifyRight.gif',
                label: 'Justify  Right'
            },
            justifyFull: {
                action: function(){
                    var editor = $.data(this, 'editor');
                    if(!editor.isEditable()) {
                        return;
                    }
                    editor.saveForUndo();
                    editor.iframe.contentWindow.document.execCommand(
                        'JustifyFull', false, null);
                },
                className: 'xEditorButtonJustifyFull',
                icon: 'btnJustifyFull.gif',
                label: 'Justify  Full'
            },
            paste: {
                action: function(){
                    var editor = $.data(this, 'editor');
                    if (editor.bookmarkSelection()) {
                        activeXEditor = editor;
                        pageURL = editor.settings.siteURL + "/paste.html";
                        editor.openJ01Dialog(pageURL);
                    }
                },
                className: 'xEditorButtonPaste',
                icon: 'btnPaste.gif',
                label: 'Paste'
            },
            undo: {
                action: function(){
                    var editor = $.data(this, 'editor');
                    if(editor.wysiwyg) {
                        editor.doUndo();
                    }
                    
                },
                className: 'xEditorButtonUndo',
                icon: 'btnUndo.gif',
                label: 'Undo'
            },
            redo: {
                action: function(){
                    var editor = $.data(this, 'editor');
                    if(editor.wysiwyg) {
                        editor.doRedo();
                    }
                    
                },
                className: 'xEditorButtonRedo',
                icon: 'btnRedo.gif',
                label: 'Redo'
            },

            link: {
                action: function(){
                    var editor = $.data(this, 'editor');
                    var node = editor.bookmarkSelection();
                    if (node) {
                        activeXEditor = editor;
                        var tag = null;
                        if (node.is('A')) {
                            tag = node;
                        }else if (node.find('A')){
                            tag = node.find('A')
                        }else if (node.parent().is('A')){
                            tag = node.parent();
                        }
                        if (tag) {
                            activeXEditorLinkURL = tag.attr('href');
                            activeXEditorLinkTarget = tag.attr('target');
                        }
                        var pageURL = editor.settings.siteURL + "/link.html";
                        editor.openJ01Dialog(pageURL);
                    }
                },
                className: 'xEditorButtonHyperlink',
                icon: 'btnHyperlink.gif',
                label: 'Hyperlink'
            },

            media: {
                action: function(){
                    var editor = $.data(this, 'editor');
                    var node = editor.bookmarkSelection();
                    if (node) {
                        activeXEditor = editor;
                        if (node.get(0).tagName === 'OBJECT') {
                            activeXEditorMediaData = {};
                            activeXEditorMediaData['url'] = node.get(0).url;
                            activeXEditorMediaData['playCount'] = node.get(0).settings.playCount;
                            activeXEditorMediaData['autoStart'] = node.get(0).settings.autoStart;
                            activeXEditorMediaData['uiMode'] = node.attr('uiMode');
                            activeXEditorMediaData['width'] = node.attr('width');
                            activeXEditorMediaData['height'] = node.attr('height');
                        }
                        var pageURL = editor.settings.siteURL + "/media.html";
                        editor.openJ01Dialog(pageURL);
                    }
                },
                className: 'xEditorButtonMedia',
                icon: 'btnMedia.gif',
                label: 'Media'
            },
            flash: {
                action: function(){
                    var editor = $.data(this, 'editor');
                    var node = editor.bookmarkSelection();
                    if (node) {
                        activeXEditor = editor;
                        if (node.get(0).tagName === 'OBJECT') {
                            activeXEditorFlashData = {};
                            activeXEditorFlashData['url'] = node.attr('movie');
                            activeXEditorFlashData['loop'] = node.attr('loop');
                            activeXEditorFlashData['width'] = node.attr('width');
                            activeXEditorFlashData['height'] = node.attr('height');
                        }
                        var pageURL = editor.settings.siteURL + "/flash.html";
                        editor.openJ01Dialog(pageURL);
                    }
                },
                className: 'xEditorButtonFlash',
                icon: 'btnFlash.gif',
                label: 'Flash'
            },
            htmlsource: {
                action: function() {
                    var editor = $.data(this, 'editor');
                    editor.switchMode();
                },
                className: 'xEditorButtonHTML',
                icon: 'btnSource.gif',
                label: 'View/Edit Source'
            },
            removeFormatting: {
                action: function() {
                    var editor = $.data(this, 'editor');
                    if(!editor.wysiwyg) {
                        return;
                    }
                    editor.saveForUndo();
                    editor.iframe.contentWindow.document.execCommand('RemoveFormat', false, null);
                },
                className: 'xEditorButtonRemoveFormatting',
                icon: 'btnRemoveFormat.gif',
                label: 'Remove Formatting'
            },
            clearAll: {
                action: function() {
                    var editor = $.data(this, 'editor');
                    if(!editor.wysiwyg) {
                        return;
                    }
                    editor.removeAll();
                },
                className: 'xEditorButtonClearAll',
                icon: 'btnDelete.gif',
                label: 'Clear All'
            },

            resize: {
                action: function() {
                    var editor = $.data(this, 'editor');
                    if (editor.isResized) {
                        if (editor.wysiwyg) {
                            $(editor.iframe).height(200);
                            $(editor.container).height(227);
                        }else{
                            $(editor.textarea).height(200);
                            $(editor.container).height(227);
                        }
                        editor.isResized = false;
                        editor.toolbar.setButtonState('resize', 4);
                    }else{
                        editor.resizeContent();
                    }
                },
                className: 'xEditorButtonResize',
                icon: 'btnResize.gif',
                label: 'Resize'
            }
        });
    };
    $.xEditorToolbarItems = new xEditorToolbarItems();

    $.fn.extend({
        getSelectedText: function() {
            if(!this.is('iframe')) {
                return;
            } else {
                iframe = this[0];
            }
            if (iframe.contentWindow.document.selection) {
                return iframe.contentWindow.document.selection.createRange().text;
            }else{
                return iframe.contentWindow.getSelection().toString();
            }
        },

        getSelectedNode: function() {
            if(!this.is('iframe')) {
                return false;
            } else {
                iframe = this[0];
            }
            // ie
            if (iframe.contentWindow.document.selection) {
                selection = iframe.contentWindow.document.selection;
                range = selection.createRange();
                try {
                    if (selection.type == 'None' || selection.type == 'Text') {
                        return $(range.parentElement());
                    }else{
                        return $(range.item(0));
                    }
                }catch (e) {
                    return false;
                }
            }
            // moz
            else {
                try {
                    selection = iframe.contentWindow.getSelection();
                    range = selection.getRangeAt(0);
                    return $(range.commonAncestorContainer);
                }
                catch (e) {
                    return false;
                }
            }
        },

        xEditor: function(settings) {
            var defaultUndesiredTags = {
                'applet': 'remove',
                'area': 'remove',
                'basefont': 'remove',
                'button': 'remove',
                'center': 'extractContent',
                'col': 'extractContent',
                'colgroup': 'extractContent',
                'dir': 'extractContent',
                'embed': 'extractContent',
                //'div': 'extractContent',
                'fieldset': 'extractContent',
                'form': 'extractContent',
                'frame': 'remove',
                'frameset': 'remove',
                'iframe': 'remove',
                'input': 'remove',
                'isindex': 'remove',
                'label': 'extractContent',
                'legend': 'extractContent',
                'link': 'remove',
                'meta': 'remove',
                'nobr': 'extractContent',
                'noframes': 'remove',
                'noscript': 'extractContent',
                //'object': 'remove',
                'script': 'remove',
                'select': 'remove',
                'table': 'extractContent',
                'tbody': 'extractContent',
                'td': 'extractContent',
                'textarea': 'remove',
                'tfoot': 'extractContent',
                'thead': 'extractContent',
                'tr': 'extractContent'
            };

            settings = $.extend({
                containerClass: 'xEditor',
                cbURL: './xEditorClipBoardPopup',
                imgURL: '../xEditorImages',
                siteURL: '.',
                stylesURL: '../xEditorStyles.css',
                doPasteMethodName: 'doXEditorPaste',
                toolbarItems: ['selector','|','styles','|','bold','italic','|','unorderedlist','justifyLeft','justifyCenter','justifyRight','justifyFull','|','paste','|','undo','redo','link','media','flash','|','htmlsource','blocks','removeFormatting','clearAll'],
                undesiredTags: defaultUndesiredTags
            }, settings);

            return this.each(function(){
                new xEditor(this, settings);
            });
        }
    });
})(jQuery);
