##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: converter.py 3041 2012-08-31 07:08:19Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
import zope.schema
import zope.schema.interfaces

from z3c.form import widget

from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IDataConverter
from z3c.form import widget
from z3c.form import converter
from z3c.form.browser import textarea

from j01.select2 import interfaces


class TagListConverter(converter.BaseDataConverter):
    """Data converter for ITagListSelect2Widget."""

    zope.component.adapts(
        zope.schema.interfaces.IList, interfaces.ITagListSelect2Widget)

    def toWidgetValue(self, value):
        """Convert from Python to HTML representation."""
        widget = self.widget
        # if the value is the missing value, then an empty list is produced.
        if value is self.field.missing_value:
            return u""
        if value:
            s = u"%s" % self.widget.separator
            return s.join(value)
        else:
            return u""

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        widget = self.widget
        if not len(value):
            return self.field.missing_value or []
        return [s for s in value.split(self.widget.separator) if s.strip()]


class LiveListConverter(converter.CollectionSequenceDataConverter):
    """Data converter for ILiveListSelect2Widget."""

    zope.component.adapts(
        zope.schema.interfaces.IList, interfaces.ILiveListSelect2Widget)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        widget = self.widget
        if not len(value):
            return self.field.missing_value or []
        if widget.terms is None:
            widget.updateTerms()
        return [widget.terms.getValue(token) for token in value]
