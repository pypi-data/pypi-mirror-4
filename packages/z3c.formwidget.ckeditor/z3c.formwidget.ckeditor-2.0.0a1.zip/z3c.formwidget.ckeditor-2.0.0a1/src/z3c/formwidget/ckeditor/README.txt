====================================
RichText Fields and CKEditor Widgets
====================================

This package a provides a new field called `RichText`, which is a simple
extension to the default `Text` field. The `RichText` field declares that it
contains HTML-markup as part of its text.

  >>> from z3c.formwidget.ckeditor import richtext

So let's create a rich text field:

  >>> text = richtext.RichText(__name__='text')

Let's now verify that the field provides the text and rich text schema:

  >>> import zope.schema
  >>> from zope.interface import verify
  >>> from z3c.formwidget.ckeditor import interfaces

  >>> verify.verifyObject(interfaces.IRichText, text)
  True
  >>> verify.verifyObject(zope.schema.interfaces.IText, text)
  True

Next, a widget is provided to edit the rich text field. It uses the CKEditor.

  >>> from z3c.formwidget.ckeditor import interfaces, ckeditor

The ``CKEditorWidget`` is a widget:

  >>> from z3c.form.interfaces import IWidget

  >>> verify.verifyClass(interfaces.ICKEditorWidget, ckeditor.CKEditorWidget)
  True
  >>> verify.verifyClass(IWidget, ckeditor.CKEditorWidget)
  True

The widget can render an input field only by adapting a request:

  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()
  >>> widget = ckeditor.CKEditorWidget(request)

Such a widget provides ``IWidget``:

  >>> IWidget.providedBy(widget)
  True

Let's add some meaningful generic data:

  >>> widget.id = 'id'
  >>> widget.name = 'name'

If we render the widget we get the HTML:

  >>> widget.update()
  >>> print(widget.render())
  <textarea id="id" name="name" class="CKEditorWidget"></textarea>
  <script type="text/javascript">CKEDITOR.replace('name', {});</script>

As you can see, initially, CK Editor is instantiated with all its
defaults. This can be changed by modifying the `config` attribute on the
widget.

If the `config` attribute is a string, it is interpreted as a JavaScript
variable name. The variable must be declared beforehand.

  >>> widget.config = 'myCKEditorConfig'
  >>> widget.update()
  >>> print(widget.render())
  <textarea id="id" name="name" class="CKEditorWidget"></textarea>
  <script type="text/javascript">CKEDITOR.replace('name', myCKEditorConfig);</script>

Alternatively, the config attribute can be a dictionary of options, which are
encoded to Javascript upon render time:

  >>> widget.config = '{"toolbar": "Basic", "uiColor": "#9AB8F3"}'
  >>> widget.update()
  >>> print(widget.render())
  <textarea id="id" name="name" class="CKEditorWidget"></textarea>
  <script type="text/javascript">CKEDITOR.replace('name', {"toolbar": "Basic", "uiColor": "#9AB8F3"});</script>

All other values cause a `ValueError` to be raised.

  >>> widget.config = 3
  >>> widget.update()
  Traceback (most recent call last):
  ...
  ValueError: ('Invalid config object', 3)

The field widget for the rich text field is available too of course:

  >>> import zope.component
  >>> from z3c.form.interfaces import IFieldWidget

  >>> widget = zope.component.getMultiAdapter((text, request), IFieldWidget)
  >>> widget
  <CKEditorWidget 'text'>

  >>> widget.update()
  >>> print(widget.render())
  <textarea id="text" name="text"
            class="CKEditorWidget required richtext-field"></textarea>
  <script type="text/javascript">CKEDITOR.replace('text', {});</script>

You can also create CKEditor Field Widget factories on the fly using a given
configuration:

  >>> MinimalCKEditorWidget = ckeditor.CKEditorFieldWidgetFactory(
  ...     '{"toolbar": "Basic", "uiColor": "#9AB8F3"}')

  >>> widget = MinimalCKEditorWidget(text, request)
  >>> widget.update()
  >>> print(widget.render())
  <textarea id="text" name="text"
            class="CKEditorWidget required richtext-field"></textarea>
  <script type="text/javascript">CKEDITOR.replace('text',
       {"toolbar": "Basic", "uiColor": "#9AB8F3"});</script>
