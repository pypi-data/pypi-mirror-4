#-*- coding: utf-8 -*-

from zope import schema
from zope import interface
import z3c.form.interfaces
import z3c.form.browser.widget
import z3c.form.widget
from z3c.form.converter import BaseDataConverter


class IContentEditableWidget(z3c.form.interfaces.IWidget):
    """ ContentEditable widget marker for z3c.form"""


class IContentEditableField(schema.interfaces.ITextLine):
    """ Special marker for date fields that use our widget """


class ContentEditableWidget(z3c.form.browser.widget.HTMLTextInputWidget,
                z3c.form.widget.Widget):
    """HTML  widget:
    """

    interface.implementsOnly(IContentEditableWidget)

    klass = u'html5-contenteditable-widget'

    def update(self):
        super(ContentEditableWidget, self).update()
        z3c.form.browser.widget.addFieldClass(self)


def ContentEditableFieldWidget(field, request):
    """IFieldWidget factory for ContentEditableWidget."""
    return z3c.form.widget.FieldWidget(field, ContentEditableWidget(request))


class ContentEditableValidationError(schema.ValidationError, ValueError):
    __doc__ = u'Please enter a valid search term.'


class Converter(BaseDataConverter):

    def toWidgetValue(self, value):
        return value

    def toFieldValue(self, value):
        if not value:
            return self.field.missing_value

        try:
            return value
        except ValueError:
            raise ContentEditableValidationError
