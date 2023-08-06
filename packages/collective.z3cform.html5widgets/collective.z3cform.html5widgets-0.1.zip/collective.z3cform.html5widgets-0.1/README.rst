Introduction
============

This addon provide the following HTML5 widgets:

* color
* contenteditable (+wysiwyg)
* datalist
* date
* datetime
* datetime-local
* email
* month
* number
* password
* range
* search
* tel
* time
* url
* week

Status: young

TODO
====

* less copy/paste where it's possible
* add tests
* add support of datalist
* add contenteditable widget for Text and TextLine

How to install
==============

This addon can be installed has any other addons. please follow official
documentation_. It doesn't provide any profile, so you juste have to add it
to your zope install.

If you want to support theses widgets on incapable browser you must consider
using polyfill.

Some addons which provide polyfills:

* collective.js.webshims

Widgets review & support
========================

datalist
--------


color
-----

Use it with zope.schema.ASCIILine field::

    from zope import schema
    from zope import interface
    from z3c.form import form, field
    from collective.z3cform.html5widgets.widget_color import ColorFieldWidget
    class ExampleSchema(interface.Interface):
        color = schema.ASCIILine(title=u"Color", required=False)
    class ExampleForm(form.Form):
        fields = field.Fields(ExampleSchema)
        fields['color'].widgetFactory = ColorFieldWidget



contenteditable
---------------

browsers supports:

* Chrome: 4.0+
* Safari: 3.1+
* Safari mobile: 5.0+
* Firefox: 3.5+
* Opera: 9.0+
* Opera mini/mobile: N/A
* Internet Explore: 5.5 (sic)
* Android: 3.0+

Example::

    from zope import schema
    from zope import interface
    from z3c.form import form, field
    class ExampleSchema(interface.Interface):
        pass
    class ExampleForm(form.Form):
        fields = field.Fields(ExampleSchema)

date
----

Example::

    from zope import schema
    from zope import interface
    from z3c.form import form, field
    
    class ExampleSchema(interface.Interface):
        date = schema.Date(title=u"Date (created)", required=False)
    
    class ExampleForm(form.Form):
        fields = field.Fields(ExampleSchema)

datetime
--------

Example::

    from zope import schema
    from zope import interface
    from z3c.form import form, field
    class ExampleSchema(interface.Interface):
        datetime = schema.Datetime(title=u"Date time (modified)", required=False)
    class ExampleForm(form.Form):
        fields = field.Fields(ExampleSchema)

datetime-local
--------------

Example::

    from zope import schema
    from zope import interface
    from z3c.form import form, field
    class ExampleSchema(interface.Interface):
        datetime = schema.Datetime(title=u"Date time (modified)", required=False)
    class ExampleForm(form.Form):
        fields = field.Fields(ExampleSchema)

email
-----

Example::

    from zope import schema
    from zope import interface
    from z3c.form import form, field
    from collective.z3cform.html5widgets.widget_email import EmailFieldWidget
    class ExampleSchema(interface.Interface):
        email = schema.ASCIILine(title=u"Email", required=False)
    class ExampleForm(form.Form):
        fields = field.Fields(ExampleSchema)
        fields['email'].widgetFactory = EmailFieldWidget

month
-----

Example::

    from zope import schema
    from zope import interface
    from z3c.form import form, field
    from collective.z3cform.html5widgets.widget_month import MonthFieldWidget
    class ExampleSchema(interface.Interface):
        month = schema.Date(title=u"Month", required=False)
    class ExampleForm(form.Form):
        fields = field.Fields(ExampleSchema)
        fields['month'].widgetFactory = MonthFieldWidget


number
------

Example::

    from zope import schema
    from zope import interface
    from z3c.form import form, field
    from collective.z3cform.html5widgets.widget_number import NumberFieldWidget
    class ExampleSchema(interface.Interface):
        number = schema.Int(title=u"Number", required=False)
    class ExampleForm(form.Form):
        fields = field.Fields(ExampleSchema)
        fields['number'].widgetFactory = NumberFieldWidget

password
--------

Example::

    from zope import schema
    from zope import interface
    from z3c.form import form, field
    class ExampleSchema(interface.Interface):
        password = schema.Password(title=u"Password", required=False)
    class ExampleForm(form.Form):
        fields = field.Fields(ExampleSchema)

range
-----

Example::

    from zope import schema
    from zope import interface
    from z3c.form import form, field
    from collective.z3cform.html5widgets.widget_range import RangeFieldWidget
    class ExampleSchema(interface.Interface):
        range = schema.Int(title=u"Range", required=False)
    class ExampleForm(form.Form):
        fields = field.Fields(ExampleSchema)
        fields['range'].widgetFactory = RangeFieldWidget

search
------

Example::

    from zope import schema
    from zope import interface
    from z3c.form import form, field
    from collective.z3cform.html5widgets.widget_search import SearchFieldWidget
    class ExampleSchema(interface.Interface):
        search = schema.TextLine(title=u"Search", required=False)
    class ExampleForm(form.Form):
        fields = field.Fields(ExampleSchema)
        fields['search'].widgetFactory = SearchFieldWidget


tel
---

Example::

    from zope import schema
    from zope import interface
    from z3c.form import form, field
    from collective.z3cform.html5widgets.widget_tel import TelFieldWidget
    class ExampleSchema(interface.Interface):
        tel = schema.ASCIILine(title=u"Telephone", required=False)
    class ExampleForm(form.Form):
        fields = field.Fields(ExampleSchema)
        fields['tel'].widgetFactory = TelFieldWidget

time
----

Example::

    from zope import schema
    from zope import interface
    from z3c.form import form, field
    class ExampleSchema(interface.Interface):
        time = schema.Time(title=u"Time", required=False)
    class ExampleForm(form.Form):
        fields = field.Fields(ExampleSchema)

url
---

Example::

    from zope import schema
    from zope import interface
    from z3c.form import form, field
    class ExampleSchema(interface.Interface):
        url = schema.URI(title=u"URL", required=False)
    class ExampleForm(form.Form):
        fields = field.Fields(ExampleSchema)

week
----

Example::

    from zope import schema
    from zope import interface
    from z3c.form import form, field
    from collective.z3cform.html5widgets.widget_week import WeekFieldWidget
    class ExampleSchema(interface.Interface):
        week = schema.Date(title=u"Week", required=False)
    class ExampleForm(form.Form):
        fields = field.Fields(ExampleSchema)
        fields['week'].widgetFactory = WeekFieldWidget


Credits
=======

Companies
---------

* `Planet Makina Corpus <http://www.makina-corpus.org>`_
* `Contact Makina Corpus <mailto:python@makina-corpus.org>`_

People
------

- JeanMichel FRANCOIS aka toutpt <toutpt@gmail.com>

.. _documentation: http://plone.org/documentation/kb/installing-add-ons-quick-how-to
