##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""z3c.form converters for m01.mongo

"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
import zope.schema

import z3c.form.interfaces
import z3c.form.converter

import m01.mongo.interfaces
import m01.mongo.schema
import m01.mongo.util


class MongoListTextLinesWidgetConverter(z3c.form.converter.TextLinesConverter):
    """A special converter between IMongoList and ITextLinesWidget."""

    zope.component.adapts(m01.mongo.interfaces.IMongoList,
        z3c.form.interfaces.ITextLinesWidget)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if not len(value):
            return self.field.missing_value

        # get value converter
        field = self.field.value_type
        widget = zope.component.getMultiAdapter((field, self.widget.request),
            z3c.form.interfaces.IFieldWidget)
        if z3c.form.interfaces.IFormAware.providedBy(self.widget):
            # form property required by objecwidget
            widget.form = self.widget.form
            zope.interface.alsoProvides(widget, z3c.form.interfaces.IFormAware)
        converter = zope.component.getMultiAdapter((field, widget),
            z3c.form.interfaces.IDataConverter)

        # return a simple list, the MongoFieldProperty will convert the given
        # list of values to a MongoItemsData or MongoListData and locate them
        return [converter.toFieldValue(v) for v in value.splitlines()]


class MongoListMultiWidgetConverter(z3c.form.converter.MultiConverter):
    """A special converter between IMongoList and IMultiWidget."""

    zope.component.adapts(m01.mongo.interfaces.IMongoList,
        z3c.form.interfaces.IMultiWidget)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if not len(value):
            return self.field.missing_value

        field = self.field.value_type
        widget = zope.component.getMultiAdapter((field, self.widget.request),
            z3c.form.interfaces.IFieldWidget)
        if z3c.form.interfaces.IFormAware.providedBy(self.widget):
            #form property required by objecwidget
            widget.form = self.widget.form
            zope.interface.alsoProvides(widget, z3c.form.interfaces.IFormAware)
        converter = zope.component.getMultiAdapter((field, widget),
            z3c.form.interfaces.IDataConverter)

        # return a simple list, the MongoFieldProperty will convert the given
        # list of values to a MongoItemsData or MongoListData and locate them
        return [converter.toFieldValue(v) for v in value]
