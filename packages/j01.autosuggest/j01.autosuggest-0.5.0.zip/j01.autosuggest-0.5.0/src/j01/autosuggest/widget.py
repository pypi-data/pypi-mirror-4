##############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: widget.py 3339 2012-11-17 06:33:32Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
import zope.schema.interfaces
from zope.component import hooks
from zope.traversing.browser import absoluteURL

import z3c.form.browser.text
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget

from j01.autosuggest import interfaces


j01_auto_suggest_template = """
<script type="text/javascript">
  $("#%s").j01AutoSuggest({%s
  });
</script>
"""


class AutoSuggestWidgetBase(z3c.form.browser.text.TextWidget):
    """AutoSuggest input widget is only a base class.

    NOTE: you must implement your own AutoSuggestWidget which knows how to
    setup a jsonRPCURL which returns the right auto suggest items if you don't
    like to use the site as context for the j01AutoSuggest JSON-RPC method

    """

    zope.interface.implementsOnly(interfaces.IAutoSuggestWidget)

    klass = u'j01AutoSuggestInput'
    css = u'j01-autosuggest'
    value = u''

    jsonRPCMethodName = 'j01AutoSuggest'
    widgetExpression = '.j01AutoSuggestWidget'
    inputExpression = '.j01AutoSuggestInput'
    resultExpression = '.j01AutoSuggestResult'
    resultContainerExpression = '.j01AutoSuggestContainer'
    callback = 'j01RenderAutoSuggestResult'
    requestId = 'j01AutoSuggest'
    minQueryLenght = 1
    fadeOutTimeout = 100
    showAllOnClick = False

    items = []

    @property
    def autoSuggestId(self):
        return '%s-autosuggest' % self.id

    @property
    def jsonRPCURL(self):
        return absoluteURL(self.form, self.request)

    @property
    def javaScript(self):
        lines = []
        append = lines.append
        append("\n    formName: '%s'" % self.form.name)
        append("\n    fieldName: '%s'" % self.__name__)
        append("\n    url: '%s'" % self.jsonRPCURL)
        append("\n    jsonRPCMethodName: '%s'" % self.jsonRPCMethodName)
        if self.widgetExpression != '.j01AutoSuggestWidget':
            append("\n    widgetExpression: '%s'" % self.widgetExpression)
        if self.inputExpression != '.j01AutoSuggestInput':
            append("\n    inputExpression: '%s'" % self.inputExpression)
        if self.resultExpression != '#j01AutoSuggestResult':
            append("\n    resultExpression: '%s'" % self.resultExpression)
        if self.callback != 'j01RenderAutoSuggestResult':
            append("\n    callback: %s" % self.callback)
        if self.requestId != 'j01AutoSuggest':
            append("\n    requestId: %s" % self.requestId)
        if self.minQueryLenght != 1:
            append("\n    minQueryLenght: %s" % self.minQueryLenght)
        if self.fadeOutTimeout != 100:
            append("\n    fadeOutTimeout: %s" % self.fadeOutTimeout)
        if self.showAllOnClick:
            append("\n    showAllOnClick: true")

        code = ','.join(lines)
        return j01_auto_suggest_template % (self.autoSuggestId, code)


class SiteAutoSuggestWidget(AutoSuggestWidgetBase):
    """AutoSuggest input widget

    NOTE:
    This widget uses the site as context for the j01AutoSuggest
    JSON-RPC method. 

    This means you need to implement a custom j01AutoSuggest method which knows
    what to return for the given fieldName. 
    """

    @property
    def jsonRPCURL(self):
        site = hooks.getSite()
        return absoluteURL(site, self.request)


@zope.component.adapter(zope.schema.interfaces.ITextLine, IFormLayer)
@zope.interface.implementer(IFieldWidget)
def getSiteAutoSuggestWidget(field, request):
    """IFieldWidget factory for SiteAutoSuggestWidget."""
    return FieldWidget(field, SiteAutoSuggestWidget(request))


def getSiteAutoSuggestShowAllOnClickWidget(field, request):
    """IFieldWidget factory for SiteAutoSuggestWidget with showAllOnClick."""
    widget = FieldWidget(field, SiteAutoSuggestWidget(request))
    widget.showAllOnClick = True
    return widget


class ContextAutoSuggestWidget(AutoSuggestWidgetBase):
    """AutoSuggest input widget

    NOTE:
    This widget uses the form context as context for the j01AutoSuggest
    JSON-RPC method. 

    This means you need to implement a custom j01AutoSuggest method which knows
    what to return for the given fieldName. 
    """

    @property
    def jsonRPCURL(self):
        return absoluteURL(self.form.__parent__, self.request)


@zope.component.adapter(zope.schema.interfaces.ITextLine, IFormLayer)
@zope.interface.implementer(IFieldWidget)
def getContextAutoSuggestWidget(field, request):
    """IFieldWidget factory for ContextAutoSuggestWidget."""
    return FieldWidget(field, ContextAutoSuggestWidget(request))


def getContextAutoSuggestShowAllOnClickWidget(field, request):
    """IFieldWidget factory for ContextAutoSuggestWidget with showAllOnClick."""
    widget = FieldWidget(field, ContextAutoSuggestWidget(request))
    widget.showAllOnClick = True
    return widget


class FormAutoSuggestWidget(AutoSuggestWidgetBase):
    """AutoSuggest input widget

    NOTE:
    This widget uses the form as context for the j01AutoSuggest
    JSON-RPC method. 

    HEADSUP:
    This means you need to implement your own widget which knows how to return
    auto suggest items. 
    """

    @property
    def getItems(self):
        raise NotImplementedError("Subclass must implement getItems method")
