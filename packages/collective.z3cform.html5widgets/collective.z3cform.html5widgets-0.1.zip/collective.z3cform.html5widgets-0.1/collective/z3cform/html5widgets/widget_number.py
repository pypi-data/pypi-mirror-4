#-*- coding: utf-8 -*-

from zope import schema
from zope import interface
from zope import component
import z3c.form.browser.widget
import z3c.form.widget
from zope.schema.fieldproperty import FieldProperty
from z3c.form.converter import BaseDataConverter
from collective.z3cform.html5widgets import base


class INumberWidget(base.IHTML5InputWidget, z3c.form.interfaces.IWidget):
    """ Number widget marker for z3c.form """


class INumberField(schema.interfaces.IASCIILine):
    """ Special marker for date fields that use our widget """


class NumberWidget(base.HTML5InputWidget, z3c.form.widget.Widget):
    """Widget"""

    interface.implementsOnly(INumberWidget)

    klass = u'html5-number-widget'
    input_type = "number"

    def update(self):
        super(NumberWidget, self).update()
        z3c.form.browser.widget.addFieldClass(self)


def NumberFieldWidget(field, request):
    """IFieldWidget factory for NumberWidget."""
    return z3c.form.widget.FieldWidget(field, NumberWidget(request))


class NumberValidationError(schema.ValidationError, ValueError):
    __doc__ = u'Please enter a valid number.'


class Converter(BaseDataConverter):

    def toWidgetValue(self, value):
        return value

    def toFieldValue(self, value):
        if not value:
            return self.field.missing_value

        try:
            return value
        except ValueError:
            raise NumberValidationError
