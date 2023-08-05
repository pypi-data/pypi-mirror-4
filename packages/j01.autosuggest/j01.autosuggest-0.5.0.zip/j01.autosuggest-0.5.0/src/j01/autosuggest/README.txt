==================
AutoSuggest Widget
==================

This package provides an auto suggest widgets.


SiteAutoSuggestWidget
---------------------

As for all widgets, the SiteAutoSuggestWidget must provide the new ``IWidget``
interface:

  >>> from zope.interface.verify import verifyClass
  >>> from z3c.form.interfaces import IWidget
  >>> from z3c.form.interfaces import INPUT_MODE
  >>> from j01.autosuggest import interfaces
  >>> from j01.autosuggest.widget import SiteAutoSuggestWidget

  >>> verifyClass(IWidget, SiteAutoSuggestWidget)
  True

The widget can be instantiated only using the request:

  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()

  >>> widget = SiteAutoSuggestWidget(request)

Before rendering the widget, one has to set the name and id of the widget:

  >>> class FakeForm(object):
  ...     name = 'search-form'

  >>> widget.id = 'id'
  >>> widget.name = 'name'
  >>> widget.__name__ = '__name__'
  >>> widget.form = FakeForm()

We also need to register the template for the widget:

  >>> import zope.component
  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> from z3c.form.widget import WidgetTemplateFactory

  >>> import os
  >>> import j01.autosuggest
  >>> def getPath(filename):
  ...     return os.path.join(os.path.dirname(j01.autosuggest.__file__),
  ...     filename)

  >>> zope.component.provideAdapter(
  ...     WidgetTemplateFactory(getPath('widget_input.pt'), 'text/html'),
  ...     (None, None, None, None, interfaces.IAutoSuggestWidget),
  ...     IPageTemplate, name=INPUT_MODE)

If we render the widget we get a simple input element. We will display a
simple text input with auto suggest support if you type some text:

  >>> widget.update()
  >>> print widget.render()
  <div class="j01AutoSuggest" id="id-autosuggest">
    <div class="j01AutoSuggestWidget">
      <input id="id" name="name" class="j01AutoSuggestInput" value="" type="text" />
    </div>
    <div class="j01AutoSuggestResult" style="display: none;"></div>
  <script type="text/javascript">
    $("#id-autosuggest").j01AutoSuggest({
      formName: 'search-form',
      fieldName: '__name__',
      url: 'http://127.0.0.1',
      jsonRPCMethodName: 'j01AutoSuggest',
      resultExpression: '.j01AutoSuggestResult'
    });
  </script>
  </div>


A value will get rendered as simple text input:

  >>> widget.value = 'search'
  >>> print widget.render()
  <div class="j01AutoSuggest" id="id-autosuggest">
    <div class="j01AutoSuggestWidget">
      <input id="id" name="name" class="j01AutoSuggestInput" value="search" type="text" />
    </div>
    <div class="j01AutoSuggestResult" style="display: none;"></div>
  <script type="text/javascript">
    $("#id-autosuggest").j01AutoSuggest({
      formName: 'search-form',
      fieldName: '__name__',
      url: 'http://127.0.0.1',
      jsonRPCMethodName: 'j01AutoSuggest',
      resultExpression: '.j01AutoSuggestResult'
    });
  </script>
  </div>

Let's now make sure that we can extract user entered data from a widget:

  >>> widget.request = TestRequest(form={'name': 'search'})
  >>> widget.update()
  >>> widget.extract()
  'search'


If nothing is found in the request, the default is returned:

  >>> widget.request = TestRequest()
  >>> widget.update()
  >>> widget.extract()
  <NO_VALUE>
