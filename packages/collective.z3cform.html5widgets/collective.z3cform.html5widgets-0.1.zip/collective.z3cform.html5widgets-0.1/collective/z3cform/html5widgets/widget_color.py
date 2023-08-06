#-*- coding: utf-8 -*-

from zope import schema
from zope import interface
from zope import component
import z3c.form.browser.widget
import z3c.form.widget
from zope.schema.fieldproperty import FieldProperty
from z3c.form.converter import BaseDataConverter
from collective.z3cform.html5widgets import base


class IColorWidget(base.IHTML5InputWidget, z3c.form.interfaces.IWidget):
    """ Color widget marker for z3c.form
    http://www.w3.org/TR/html-markup/input.color.html
    """


class IColorField(schema.interfaces.IASCIILine):
    """ Special marker for date fields that use our widget """


class ColorWidget(base.HTML5InputWidget, z3c.form.widget.Widget):
    """widget"""

    interface.implementsOnly(IColorWidget)

    klass = u'html5-color-widget'
    input_type = "color"

    def update(self):
        super(ColorWidget, self).update()
        z3c.form.browser.widget.addFieldClass(self)


def ColorFieldWidget(field, request):
    """IFieldWidget factory for ColorWidget."""
    return z3c.form.widget.FieldWidget(field, ColorWidget(request))


class ColorValidationError(schema.ValidationError, ValueError):
    __doc__ = u'Please enter a valid color (eg. #0590FF)'


class Converter(BaseDataConverter):

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return ''
        return value

    def toFieldValue(self, value):
        if not value:
            return self.field.missing_value

        try:
            return str(value)
        except ValueError:
            raise ColorValidationError
