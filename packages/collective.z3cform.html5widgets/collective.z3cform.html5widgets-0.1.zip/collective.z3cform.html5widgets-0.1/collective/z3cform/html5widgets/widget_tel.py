#-*- coding: utf-8 -*-

from zope import schema
from zope import interface
from zope import component
import z3c.form.browser.widget
import z3c.form.widget
#from zope.i18n.format import TelTimeParseError
from zope.schema.fieldproperty import FieldProperty
from z3c.form.converter import BaseDataConverter
from collective.z3cform.html5widgets import base


class ITelWidget(base.IHTML5InputWidget, z3c.form.interfaces.IWidget):
    """ Tel widget marker for z3c.form """


class ITelField(schema.interfaces.IASCIILine):
    """ Special marker for date fields that use our widget """


class TelWidget(base.HTML5InputWidget, z3c.form.widget.Widget):
    """widget"""
    interface.implementsOnly(ITelWidget)

    klass = u'html5-tel-widget'
    input_type = "tel"

    def update(self):
        super(TelWidget, self).update()
        z3c.form.browser.widget.addFieldClass(self)


def TelFieldWidget(field, request):
    """IFieldWidget factory for TelWidget."""
    return z3c.form.widget.FieldWidget(field, TelWidget(request))


class TelValidationError(schema.ValidationError, ValueError):
    __doc__ = u'Please enter a valid date.'


class Converter(BaseDataConverter):

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return ''
        return value

    def toFieldValue(self, value):
        if not value:
            return self.field.missing_value

        try:
            return value
        except ValueError:
            raise TelValidationError
