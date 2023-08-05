##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: jsonrpc.py 3030 2012-08-26 04:26:26Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
from zope.publisher.interfaces.browser import IBrowserPage

from z3c.jsonrpc.interfaces import IJSONRPCRequest
from z3c.jsonrpc.publisher import MethodPublisher

from j01.select2 import interfaces


class Select2Result(MethodPublisher):
    """JSON-RPC select2 result search method."""

    zope.interface.implements(interfaces.ISelect2Result)
    zope.component.adapts(IBrowserPage, IJSONRPCRequest)

    def j01Select2Result(self, fieldName, searchString, page):
        """Returns the select2 search result as JSON data.

        The returned value provides the following data structure:

        {
             more: false,
             results: [
                { id: "CA", text: "California" },
                { id: "AL", text: "Alabama" }
             ]
        }

        or for grouped data:

        {
            more: false,
            results: [
                { text: "Western", children: [
                    { id: "CA", text: "California" },
                    { id: "AZ", text: "Arizona" }
                ] },
                { text: "Eastern", children: [
                    { id: "FL", text: "Florida" }
                ] }
            ]
        }

        """

        # setup widget
        self.context.fields = self.context.fields.select(fieldName)
        self.context.updateWidgets()
        widget = self.context.widgets.get(fieldName)
        return widget.getSelect2Result(searchString, page)
