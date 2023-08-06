import zope.interface
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary
from z3c.form.browser.interfaces import IHTMLInputWidget
from z3c.form.browser.widget import HTMLInputWidget
from zope.schema.fieldproperty import FieldProperty


required_vocab = SimpleVocabulary.fromValues(['required'])
autocomplete_vocab = SimpleVocabulary.fromValues(['on', 'off'])
# http://www.w3.org/wiki/HTML/Elements/input
input_type_vocab = SimpleVocabulary.fromValues([
    "hidden",
    "text",
    "search",
    "tel",
    "url",
    "email",
    "password",
    "datetime",
    "date",
    "month",
    "week",
    "time",
    "datetime-local",
    "number",
    "range",
    "color",
    "checkbox",
    "radio",
    "file",
    "submit",
    "image",
    "reset",
    "button"
])

TYPES_MATRIX = {
    'autocomplete': [
        'text', 'search', 'url', 'tel', 'email', 'password',
        'datepickers', 'range', 'color'
    ],
    'step': ['number', 'range', 'date', 'datetime', 'datetime-local', 'month',
        'time', 'week'
    ],
    'placeholder': ['text', 'search', 'url', 'tel', 'email', 'password'],
    'required_attr': ['text', 'search', 'password', 'url', 'tel', 'email',
        'date', 'datetime', 'datetime-local', 'month', 'week', 'time',
        'number', 'checkbox', 'radio', 'file'
    ],
    'pattern': ['text', 'search', 'url', 'tel', 'email', 'password'],
    'min': ['number', 'range', 'date', 'datetime', 'datetime-local', 'month',
        'time', 'week'
    ],
    'max': ['number', 'range', 'date', 'datetime', 'datetime-local', 'month',
        'time', 'week'
    ],
}


class IHTML5InputWidget(IHTMLInputWidget):
    """
    * min max: input type number, date, range
    """

    input_type = schema.Choice(title=u"Type",
                               required=True,
                               vocabulary=input_type_vocab)

    autocomplete = schema.Choice(title=u"autocomplete", required=False,
                                 vocabulary=autocomplete_vocab)

    min = schema.ASCIILine(title=u"Min", required=False)
    max = schema.ASCIILine(title=u"Max", required=False)
    pattern = schema.ASCIILine(title=u"Pattern", required=False)
    placeholder = schema.TextLine(title=u"Placeholder", required=False)

    required_attr = schema.Choice(title=u"Required (attribute)",
                                  required=False,
                                  vocabulary=required_vocab)

    step = schema.Int(title=u"Step", required=False)


@zope.interface.implementer(IHTML5InputWidget)
class HTML5InputWidget(HTMLInputWidget):

    autocomplete = FieldProperty(IHTML5InputWidget['autocomplete'])
    min = FieldProperty(IHTML5InputWidget['min'])
    max = FieldProperty(IHTML5InputWidget['max'])
    pattern = FieldProperty(IHTML5InputWidget['pattern'])
    placeholder = FieldProperty(IHTML5InputWidget['placeholder'])
    required_attr = FieldProperty(IHTML5InputWidget['required_attr'])
    step = FieldProperty(IHTML5InputWidget['step'])

    def update(self):
        """See z3c.form.interfaces.IWidget"""
        super(HTML5InputWidget, self).update()
        if self.required:
            self.required_attr = "required"
        else:
            self.required_attr = None
        #lets force compatibility
        itype = self.input_type
        ATTR = ('autocomplete', 'step', 'placeholder', 'required_attr',
                'pattern', 'min', 'max')
        for attr in ATTR:
            if getattr(self, attr, None) and itype not in TYPES_MATRIX[attr]:
                setattr(self, attr, None)  # reset
