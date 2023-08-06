#python
from datetime import datetime

#zope
from zope import schema
from zope import interface
from zope import component
from zope.schema.fieldproperty import FieldProperty
import z3c.form.browser.widget
import z3c.form.widget

#plone
import plone.app.z3cform

#internal
from collective.z3cform.html5widgets.widget_datetime import DateTimeConverter
from collective.z3cform.html5widgets import base


class IDateTimeLocalWidget(base.IHTML5InputWidget,
                           z3c.form.interfaces.IWidget):
    """ Date widget marker for z3c.form
    #rfc 3339
    #full-date       = date-fullyear "-" date-month "-" date-mday
    supported:
    # IE9: display input type text
    # Opera: Supported -> 2012-01-26-T13:37:01.00Z
    # Safari: Supported -> 2012-01-26-T13:37Z
    # IPhone: Supported -> 2012-01-26-T13:37:01Z
    # Chrome: input type text
    # Chrome mobile (android): supported
    # Firefox: display input type text.
    # Firefox mobile (android): display input type text with numeric keyboard
    # Androidi browser (3.1+): input type text
    """


class IDateTimeLocalField(plone.app.z3cform.widget.IDatetimeField):
    """ Special marker for date fields that use our widget """


class DateTimeLocalWidget(base.HTML5InputWidget, z3c.form.widget.Widget):
    """widget"""

    interface.implementsOnly(IDateTimeLocalWidget)

    klass = u'html5-datetimelocal-widget'
    input_type = "datetime-local"

    def update(self):
        super(DateTimeLocalWidget, self).update()
        z3c.form.browser.widget.addFieldClass(self)


def DateTimeLocalFieldWidget(field, request):
    """IFieldWidget factory for DateTimeLocalWidget."""
    return z3c.form.widget.FieldWidget(field, DateTimeLocalWidget(request))


class DateTimeLocalValidationError(schema.ValidationError, ValueError):
    __doc__ = u'Please enter a valid datetime.'


class DateTimeLocalConverter(DateTimeConverter):
    def raise_error(self):
        raise DateTimeLocalValidationError
