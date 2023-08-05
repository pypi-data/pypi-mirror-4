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
$Id: widget.py 3553 2012-12-16 09:12:34Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
from zope.component import hooks
from zope.traversing.browser import absoluteURL

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.browser.textarea

import p01.cdn.interfaces

import p01.editor
import p01.editor.util
from p01.editor import interfaces


# XEditor
JAVASCRIPT = """
<script type="text/javascript">
$(document).ready(function() {
    $("%s").xEditor({%s
    });
  });
</script>
"""

TEXTAREA = """<textarea id="%s" name="%s" class="xEditor">%s</textarea>"""


def getJavaScript(data):
    """SmartEditorWidget JavaScript generator."""
    try:
        widgetExpression = data.pop('widgetExpression')
    except KeyError, e:
        widgetExpression = '.xEditor'

    lines = []
    append = lines.append
    for key, value in data.items():
        if key == 'toolbarItems':
            value = ["'%s'" % v for v in value]
            menuItems = ',\n'.join(value)
            append("\n    %s: [%s]" % (key, menuItems))
        elif key == 'undesiredTags':
            tags = []
            for k, v in value.items():
                tags.append("'%s':'%s'" % (k, v))
            tags = ',\n'.join(tags)
            append("\n    %s: {%s}" % (key, tags))
        elif value is True:
            append("\n    %s: true" % key)
        elif value is False:
            append("\n    %s: false" % key)
        elif value is None:
            append("\n    %s: null" % key)
        elif isinstance(value, int):
            append("\n    %s: %s" % (key, value))
        elif isinstance(value, str):
            if value.startswith('$'):
                append("\n    %s: %s" % (key, value))
            else:
                append("\n    %s: '%s'" % (key, value))
        else:
            append("\n    %s: %s" % (key, value))
    code = ','.join(lines)

    return JAVASCRIPT % (widgetExpression, code)


class XEditorWidget(z3c.form.browser.textarea.TextAreaWidget):
    """XEditor widget
    
    Note, this widget is using p01.cdn for get the right style and image
    resource uri.
    """

    zope.interface.implementsOnly(interfaces.IXEditorWidget)

    # widget
    _missing = u''
    rows = 4
    cols = 30

    klass = u'editor'
    css = u'editor'

    # editor
    widgetExpression = None
    containerClass = 'xEditor'

    doPasteMethodName = 'doXEditorPaste'

    toolbarItems = [
        'selector', '|',
        'styles', '|',
        'bold', 'italic', '|',
        'unorderedlist', 'justifyLeft', 'justifyCenter', 'justifyRight',
        'justifyFull', '|',
        'paste', '|',
        'undo', 'redo', 'link', 'media', 'flash', '|',
        'htmlsource', 'blocks', 'removeFormatting', 'clearAll','resize',
        ]

    undesiredTags = {
        'script' : 'remove',
        'meta' : 'remove',
        'link' : 'remove',
        'basefont' : 'remove',
        'noscript' : 'extractContent',
        'nobr' : 'extractContent',
        # 'object' : 'remove',
        'applet' : 'remove',
        'form': 'extractContent',
        'fieldset': 'extractContent',
        'input' : 'remove',
        'select': 'remove',
        'textarea' : 'remove',
        'button' : 'remove',
        'isindex' : 'remove',
        'label' : 'extractContent',
        'legend' : 'extractContent',
        # 'div' : 'extractContent',
        'table' : 'extractContent',
        'thead' : 'extractContent',
        'tbody' : 'extractContent',
        'tr' : 'extractContent',
        'td' : 'extractContent',
        'tfoot' : 'extractContent',
        'col' : 'extractContent',
        'colgroup' : 'extractContent',
        'center' : 'extractContent',
        'area' : 'remove',
        'dir' : 'extractContent',
        'frame' : 'remove',
        'frameset' : 'remove',
        'noframes' : 'remove',
        'iframe' : 'remove'
    }

    @property
    def cbURL(self):
        return "%s/@@xEditorClipBoardPopup" % self.request.URL

    @property
    def imgURL(self):
        cdnManager = p01.cdn.interfaces.IResourceManager(self.request)
        return cdnManager.getURI('xEditorImages')

    @property
    def stylesURL(self):
        cdnManager = p01.cdn.interfaces.IResourceManager(self.request)
        return cdnManager.getURI('xEditorStyles.css')

    @property
    def siteURL(self):
        site = hooks.getSite()
        return absoluteURL(site, self.request)

    def cleanup(self, value):
        """Cleanup method which removes any tag attribute and only allows a
        small set of tags. See simpleHTML for more info.
        """
        return p01.editor.util.simpleHTML(value)

    @property
    def widgetExpression(self):
        shortName = self.name.split('.')[1]
        return '#%sXEditor' % shortName

    def extract(self, default=z3c.form.interfaces.NO_VALUE):
        """Support cleanup value call"""
        value = super(XEditorWidget, self).extract(default)
        if value is not z3c.form.interfaces.NO_VALUE:
            # cleanup if value is given
            value = self.cleanup(value)
        return value

    def render(self):
        """See IBrowserWidget."""
        value = self.value
        if not value:
            value = u''
        shortName = self.name.split('.')[1]
        shortName = '%sXEditor' % shortName
        name = self.name
        textarea = TEXTAREA % (shortName, self.name,
            p01.editor.escape(value))
        return '%s\n%s' % (textarea, self.javascript)

    @property
    def javascript(self):
        data = {'widgetExpression': self.widgetExpression,
                'containerClass': self.containerClass,
                'cbURL': self.cbURL,
                'imgURL': self.imgURL,
                'siteURL': self.siteURL,
                'stylesURL': self.stylesURL,
                'doPasteMethodName': self.doPasteMethodName,
                'toolbarItems': self.toolbarItems,
                'undesiredTags': self.undesiredTags,
               }
        return getJavaScript(data)


class SimpleXEditorWidget(XEditorWidget):
    """XEditor widget for simple textarea fields.
    
    This widget is the default widget registred for the IHTMLField. Implement
    your own widget with a custom configuration and use then in your forms.
    Below, you can see a widget getter method e.g. getSimpleXEditorWidget for
    simply get such a widget.

    """

    toolbarItems = [
        'bold', 'italic', '|',
        'unorderedlist', '|',
        'undo', 'redo', '|',
        'htmlsource', 'removeFormatting', 'clearAll','resize',
        ]


def getSimpleXEditorWidget(field, request):
    """IFieldWidget factory for LiveEditorWidget."""
    return z3c.form.widget.FieldWidget(field, SimpleXEditorWidget(request))
