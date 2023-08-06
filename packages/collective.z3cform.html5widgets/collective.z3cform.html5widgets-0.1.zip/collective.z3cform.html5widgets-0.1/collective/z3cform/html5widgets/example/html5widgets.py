from zope import component
from zope import schema
from zope import interface
from z3c.form import form, button, field
from plone.z3cform import layout
from collective.z3cform.html5widgets.widget_tel import TelFieldWidget
from collective.z3cform.html5widgets.widget_month import MonthFieldWidget
from collective.z3cform.html5widgets.widget_number import NumberFieldWidget
from collective.z3cform.html5widgets.widget_week import WeekFieldWidget
from collective.z3cform.html5widgets.widget_email import EmailFieldWidget
from collective.z3cform.html5widgets.widget_range import RangeFieldWidget
from collective.z3cform.html5widgets.widget_search import SearchFieldWidget
from collective.z3cform.html5widgets.widget_color import ColorFieldWidget
from collective.z3cform.html5widgets.widget_contenteditable import ContentEditableFieldWidget


from collective.z3cform.html5widgets.widget_datalist import DatalistSelectionFieldWidget
from z3c.formwidget.query.interfaces import IQuerySource
from Products.CMFCore.utils import getToolByName
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.schema.interfaces import IContextSourceBinder


class KeywordSource(object):
    interface.implements(IQuerySource)

    def __init__(self, context):
        self.context = context
        catalog = getToolByName(context, 'portal_catalog')
        self.keywords = catalog.uniqueValuesFor('Subject')
        terms = []
        for x in self.keywords:
            terms.append(SimpleTerm(x, x, unicode(x)))
        self.vocab = SimpleVocabulary(terms)

    def __contains__(self, term):
        return self.vocab.__contains__(term)

    def __iter__(self):
        return self.vocab.__iter__()

    def __len__(self):
        return self.vocab.__len__()

    def getTerm(self, value):
        return self.vocab.getTerm(value)

    def getTermByToken(self, value):
        return self.vocab.getTermByToken(value)

    def search(self, query_string):
        q = query_string.lower()
        return [self.getTerm(kw) for kw in self.keywords if q in kw.lower()]


class KeywordSourceBinder(object):
    interface.implements(IContextSourceBinder)

    def __call__(self, context):
        return KeywordSource(context)


class ExampleSchema(interface.Interface):
    color = schema.ASCIILine(title=u"Color", required=False)
    contenteditable = schema.Text(title=u"Content Editable", required=False,
                          default=u"<p>editable value</p><p>on multi line</p>")
    date = schema.Date(title=u"Date (created)", required=False)
    datetime = schema.Datetime(title=u"Date time (modified)", required=False)
    datetime_local = schema.Datetime(title=u"Date time local (modified)", required=False)
    email = schema.ASCIILine(title=u"Email", required=False)
    month = schema.Date(title=u"Month", required=False)
    number = schema.Int(title=u"Number", required=False)
    password = schema.Password(title=u"Password", required=False)
    range = schema.Int(title=u"Range", required=False)
    search = schema.TextLine(title=u"Search", required=False)
    tel = schema.ASCIILine(title=u"Telephone", required=False)
    time = schema.Time(title=u"Time", required=False)
    url = schema.URI(title=u"URL", required=False)
    #required = schema.ASCIILine(title=u"", required=True)
    week = schema.Date(title=u"Week", required=False)

    datalist = schema.Choice(title=u"Datalist (single)",
        source=KeywordSourceBinder(), required=False)


class ExampleAdapter(object):
    interface.implements(ExampleSchema)
    component.adapts(interface.Interface)

    def __init__(self, context):
        self.context = context
        self.date = None
        self.datetime = None
        self.datetime_local = None
        self.tel = None


class ExampleForm(form.Form):
    """example"""
    fields = field.Fields(ExampleSchema)
    fields['color'].widgetFactory = ColorFieldWidget
    fields['contenteditable'].widgetFactory = ContentEditableFieldWidget
    fields['email'].widgetFactory = EmailFieldWidget
    fields['month'].widgetFactory = MonthFieldWidget
    fields['number'].widgetFactory = NumberFieldWidget
    fields['range'].widgetFactory = RangeFieldWidget
    fields['search'].widgetFactory = SearchFieldWidget
    fields['tel'].widgetFactory = TelFieldWidget
    fields['week'].widgetFactory = WeekFieldWidget
    fields['datalist'].widgetFactory = DatalistSelectionFieldWidget

    @button.buttonAndHandler(u'Ok')
    def handle_ok(self, action):
        data, errors = self.extractData()
        print data, errors

Example = layout.wrap_form(ExampleForm)
