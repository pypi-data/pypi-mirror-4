##############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: interfaces.py 2705 2011-12-06 22:06:45Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import z3c.jsonrpc.interfaces
from z3c.form.interfaces import ITextWidget


class IAutoSuggestWidget(ITextWidget):
    """AutoSuggest widget."""
    

class IJSONAutoSuggest(z3c.jsonrpc.interfaces.IJSONRPCRequest):
    """JSON-RPC auto suggest method."""

    def j01AutoSuggest(fieldName, searchString, page, batchSize):
        """Returns the auto suggest result on the search string."""
