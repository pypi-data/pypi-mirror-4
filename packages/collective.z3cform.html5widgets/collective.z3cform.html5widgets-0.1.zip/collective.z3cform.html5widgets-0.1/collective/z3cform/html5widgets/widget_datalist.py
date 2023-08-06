#python
from datetime import datetime

#zope
from zope import schema
from zope import interface
from zope import component
from zope.schema.fieldproperty import FieldProperty
import z3c.form.browser.widget
import z3c.form.widget
from z3c.form.converter import BaseDataConverter

#plone
from plone.app.z3cform import widget
from plone.formwidget.autocomplete.widget import AutocompleteSelectionWidget
from plone.formwidget.autocomplete.interfaces import IAutocompleteWidget
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

#internal
from collective.z3cform.html5widgets import base


class IDatalistSelectionWidget(base.IHTML5InputWidget, IAutocompleteWidget,
                               z3c.form.interfaces.IWidget):
    """Datalist widget marker for z3c.form """


class DatalistSelectionWidget(AutocompleteSelectionWidget, z3c.form.widget.Widget):
    """HTML Datalist widget:"""

    interface.implementsOnly(IDatalistSelectionWidget)

    klass = u'html5-datalist-widget'
    js_template = """\
    (function($) {
        $().ready(function() {
            console.log('autocomplete ready ?');
        });
    })(jQuery);
    """

    def update(self):
        super(DatalistSelectionWidget, self).update()
        z3c.form.browser.widget.addFieldClass(self)


@interface.implementer(z3c.form.interfaces.IFieldWidget)
def DatalistSelectionFieldWidget(field, request):
    """IFieldWidget factory for DatalistWidget."""
    return z3c.form.widget.FieldWidget(field, DatalistSelectionWidget(request))
