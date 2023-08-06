#-*- coding: utf-8 -*-

from zope import schema
from zope import interface
from zope import component
import z3c.form.browser.widget
import z3c.form.widget
from zope.schema.fieldproperty import FieldProperty
from z3c.form.converter import BaseDataConverter
from collective.z3cform.html5widgets import base


class IRangeWidget(base.IHTML5InputWidget, z3c.form.interfaces.IWidget):
    """ Range widget marker for z3c.form
    http://www.w3.org/TR/html-markup/input.range.html

    """


class IRangeField(schema.interfaces.IASCIILine):
    """ Special marker for date fields that use our widget """


class RangeWidget(base.HTML5InputWidget, z3c.form.widget.Widget):
    """Widget"""

    interface.implementsOnly(IRangeWidget)

    klass = u'html5-number-widget'
    input_type = "range"

    def update(self):
        super(RangeWidget, self).update()
        z3c.form.browser.widget.addFieldClass(self)


def RangeFieldWidget(field, request):
    """IFieldWidget factory for RangeWidget."""
    return z3c.form.widget.FieldWidget(field, RangeWidget(request))


class RangeValidationError(schema.ValidationError, ValueError):
    __doc__ = u'Please enter a valid number.'


class Converter(BaseDataConverter):

    def toWidgetValue(self, value):
        return value

    def toFieldValue(self, value):
        if not value:
            return self.field.missing_value

        try:
            return int(value)
        except ValueError:
            raise RangeValidationError
