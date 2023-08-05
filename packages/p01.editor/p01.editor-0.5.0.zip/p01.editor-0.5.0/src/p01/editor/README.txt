======
README
======

This package provides a WYSIWYG HTML editor wdiget based on z3c.form. The
special concept in this editor allows to define content editable areas in
the html input. this is optional and only usefull if you inject initial
content before a user can edit them. But this optional feature is not a part of
this test.

  >>> import zope.interface
  >>> import zope.interface.verify
  >>> import zope.component
  >>> import zope.schema
  >>> import z3c.form.interfaces
  >>> from z3c.form.testing import TestRequest


Our widget editor used the p01.cdn concept. Let's register a cdn manager:

This package provides a simple resource manager implementation. We will setup
them with a version number and an external uri:

  >>> import p01.cdn.manager
  >>> import p01.cdn.interfaces
  >>> VERSION = '1.0.0'
  >>> URI = 'http://www.foobar.tld'
  >>> manager = p01.cdn.manager.ResourceManager(VERSION, URI)
  >>> manager
  <ResourceManager '1.0.0' at 'http://www.foobar.tld'>

Let's now register the version manager, so that it is available for later use:

  >>> @zope.component.adapter(z3c.form.interfaces.IFormLayer)
  ... @zope.interface.implementer(p01.cdn.interfaces.IResourceManager)
  ... def getCDNResourceManager(request):
  ...     return manager

  >>> zope.component.provideAdapter(getCDNResourceManager)


XEditorWidget
-------------

  >>> from p01.editor import interfaces
  >>> from p01.editor.widget import XEditorWidget

  >>> zope.interface.verify.verifyClass(z3c.form.interfaces.IWidget,
  ...     XEditorWidget)
  True

Let's setup a schema  using our HTMLField first:

  >>> content = zope.schema.Text(
  ...     title=u"content",
  ...     description=u"content")

  >>> request = TestRequest()
  >>> widget = XEditorWidget(request)
  >>> widget.field = content

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'widget.id'
  >>> widget.name = 'widget.content'

Now we can render the widget:

  >>> widget.update()
  >>> print widget.render()
  <textarea id="contentXEditor" name="widget.content" class="xEditor"></textarea>
  <BLANKLINE>
  <script type="text/javascript">
  $(document).ready(function() {
      $("#contentXEditor").xEditor({
      stylesURL: 'http://www.foobar.tld/xEditorStyles.css',
      siteURL: 'http://127.0.0.1',
      cbURL: 'http://127.0.0.1/@@xEditorClipBoardPopup',
      undesiredTags: {'frameset':'remove',
  'frame':'remove',
  'area':'remove',
  'meta':'remove',
  'table':'extractContent',
  'select':'remove',
  'noframes':'remove',
  'noscript':'extractContent',
  'script':'remove',
  'tr':'extractContent',
  'tbody':'extractContent',
  'label':'extractContent',
  'tfoot':'extractContent',
  'input':'remove',
  'td':'extractContent',
  'thead':'extractContent',
  'fieldset':'extractContent',
  'form':'extractContent',
  'basefont':'remove',
  'nobr':'extractContent',
  'link':'remove',
  'legend':'extractContent',
  'center':'extractContent',
  'textarea':'remove',
  'colgroup':'extractContent',
  'button':'remove',
  'isindex':'remove',
  'applet':'remove',
  'iframe':'remove',
  'col':'extractContent',
  'dir':'extractContent'},
      toolbarItems: ['selector',
  '|',
  'styles',
  '|',
  'bold',
  'italic',
  '|',
  'unorderedlist',
  'justifyLeft',
  'justifyCenter',
  'justifyRight',
  'justifyFull',
  '|',
  'paste',
  '|',
  'undo',
  'redo',
  'link',
  'media',
  'flash',
  '|',
  'htmlsource',
  'blocks',
  'removeFormatting',
  'clearAll',
  'resize'],
      doPasteMethodName: 'doXEditorPaste',
      containerClass: 'xEditor',
      imgURL: 'http://www.foobar.tld/xEditorImages'
      });
    });
  </script>
  <BLANKLINE>


escape
------

There is an escape method if you need to render content in your template
without an editor widget:

  >>> import p01.editor
  >>> XSS = p01.editor.escape(u'<script>alert("evil");</script>')
  >>> evil = u'<html>%s</html>' % XSS
  >>> bad = p01.editor.escape(evil)
  >>> bad
  u'&lt;html&gt;&amp;lt;script&amp;gt;alert("evil");&amp;lt;/script&amp;gt;&lt;/html&gt;'

As you can see, if we unescape our evil content, we don't unescape the double
escaped part:

  >>> from xml.sax import saxutils
  >>> saxutils.unescape(bad)
  u'<html>&lt;script&gt;alert("evil");&lt;/script&gt;</html>'


We will always escape the given value in our editor widget. This makes sure
the we never render/unescape evil code within a widget which get rendered with
tal:content="structure ...". This will prevent us from double escaped code 
which we didn't strip during store the given input.

The widget will render he given value as escaped:

  >>> widget.value = evil
  >>> print widget.render()
  <textarea id="contentXEditor" name="widget.content" class="xEditor">&lt;html&gt;&amp;lt;script&amp;gt;alert("evil");&amp;lt;/script&amp;gt;&lt;/html&gt;</textarea>
  ...

The same as above, we will not unescape the evil part. This is the same as we
whould use <div tal:content="structure ..."></div>:

  >>> print saxutils.unescape(widget.render())
  <textarea id="contentXEditor" name="widget.content" class="xEditor"><html>&lt;script&gt;alert("evil");&lt;/script&gt;</html></textarea>
  ...
