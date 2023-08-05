##############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: jsonrpc.py 2705 2011-12-06 22:06:45Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
from zope.publisher.interfaces.browser import IBrowserPage

from z3c.jsonrpc.publisher import MethodPublisher
from z3c.jsonrpc.interfaces import IJSONRPCRequest

from j01.autosuggest import interfaces


class FormAutoSuggest(MethodPublisher):
    """Auto suggest JSON-RPC method
    
    NOTE:
    This method is only used for FormAutoSuggestWidget. You must implement
    your own j01AutoSuggest JSON-RPC method if you use the form context or site
    as your j01AutoSuggest method context

    """

    zope.component.adapts(IBrowserPage, IJSONRPCRequest)
    zope.interface.implements(interfaces.IJSONAutoSuggest)

    def j01AutoSuggest(self, fieldName, searchString):
        """Retruns an auto suggest result"""
        # setup single widget
        self.context.fields = self.context.fields.select(fieldName)
        self.context.updateWidgets()
        widget = self.context.widgets.get(fieldName)

        items = []
        if widget is not None:
            items = widget.items
        return {'items': items}
