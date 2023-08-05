import pytz
from datetime import date, datetime
from plone.formwidget.datetime import base
from plone.formwidget.datetime.z3cform.interfaces import IDateWidget
from plone.formwidget.datetime.z3cform.interfaces import IDatetimeWidget
from plone.formwidget.datetime.z3cform.interfaces import IMonthYearWidget
from plone.formwidget.datetime.z3cform.interfaces import IYearWidget

from z3c.form.browser.widget import addFieldClass, HTMLTextInputWidget
from z3c.form.interfaces import NOVALUE, IFormLayer, IFieldWidget
from z3c.form.widget import Widget, FieldWidget
from zope.component import adapter
from zope.i18n.format import DateTimeParseError
from zope.interface import implementer, implementsOnly
from zope.schema.interfaces import IField

class AbstractDXDateWidget(HTMLTextInputWidget, Widget):

    def update(self):
        super(AbstractDXDateWidget, self).update()
        addFieldClass(self)

    def extract(self, default=NOVALUE):
        # get normal input fields
        day = self.request.get(self.name + '-day', default)
        month = self.request.get(self.name + '-month', default)
        year = self.request.get(self.name + '-year', default)

        if not default in (year, month, day):
            return (year, month, day)

        # get a hidden value
        formatter = self._dtformatter
        hidden_date = self.request.get(self.name, '')
        try:
            if formatter is not None:
                dateobj = formatter.parse(hidden_date)
                return (str(dateobj.year),
                        str(dateobj.month),
                        str(dateobj.day))
        except DateTimeParseError:
            pass

        return default

    @property
    def js_value(self):
        value_date = self.value[:3]
        if '' not in value_date:
            return 'new Date(%s, %s, %s)' % (value_date)
        else:
            return ''

    @property
    def js_field(self):
        """Returns the id of a field that contains a js-parseable value of the selected date.
        Used by plone.formwidget.recurrencewidget"""
        return self.id + '-calendar'


class DateWidget(base.AbstractDateWidget, AbstractDXDateWidget):
    """ Date widget.

    Please note: zope.schema date/datetime field values are python datetime
    instances.

    """
    implementsOnly(IDateWidget)

@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def DateFieldWidget(field, request):
    """IFieldWidget factory for DateWidget."""
    return FieldWidget(field, DateWidget(request))


class DatetimeWidget(base.AbstractDatetimeWidget, AbstractDXDateWidget):
    """ DateTime widget """
    implementsOnly(IDatetimeWidget)

    def extract(self, default=NOVALUE):
        # get normal input fields
        day = self.request.get(self.name + '-day', default)
        month = self.request.get(self.name + '-month', default)
        year = self.request.get(self.name + '-year', default)
        hour = self.request.get(self.name + '-hour', default)
        minute = self.request.get(self.name + '-minute', default)
        timezone = self.request.get(self.name + '-timezone', default)

        if (self.ampm is True and
            hour is not default and
            minute is not default and
            hour):
            ampm = self.request.get(self.name + '-ampm', default)
            if ampm == 'PM':
                if hour != u'12':
                    hour = str(12+int(hour))
            elif ampm == 'AM':
                if hour == u'12':
                    hour = u'00'  # 12 a.m. midnight hour == 00:**
            # something strange happened since we either
            # should have 'PM' or 'AM', return default
            elif ampm != 'AM':
                return default

        if default not in (year, month, day, hour, minute):
            dt = (year, month, day, hour, minute)
            if timezone != default:
                # can be naive datetime
                dt += (timezone,)
            return dt

        # get a hidden value
        formatter = self._dtformatter
        try:
            if formatter is not None:
                hidden_date = self.request.get(self.name, '')
                dateobj = formatter.parse(hidden_date)
                tz = getattr(dateobj, 'tzinfo', '')
                if tz:
                    tz = str(tz)
                else:
                    ts = ''
                return (str(dateobj.year),
                        str(dateobj.month),
                        str(dateobj.day),
                        str(dateobj.hour),
                        str(dateobj.minute),
                        tz,)
        except DateTimeParseError:
            pass

        return default

@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def DatetimeFieldWidget(field, request):
    """IFieldWidget factory for DatetimeWidget."""
    return FieldWidget(field, DatetimeWidget(request))


class MonthYearWidget(base.AbstractMonthYearWidget, AbstractDXDateWidget):
    """ Month and year widget """
    implementsOnly(IMonthYearWidget)
    def extract(self, default=NOVALUE):
        day = self.request.get(self.name + '-day', default)
        year = self.request.get(self.name + '-year', default)
        month = self.request.get(self.name + '-month', default)
        # only make default for day if year/month are set !
        if ((not default in (year, month))
            and (day == default)):
            self.request.form[self.name + '-day'] = '1'
        return AbstractDXDateWidget.extract(self)

@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def MonthYearFieldWidget(field, request):
    """IFieldWidget factory for MonthYearWidget."""
    return FieldWidget(field, MonthYearWidget(request))

class YearWidget(base.AbstractYearWidget, AbstractDXDateWidget):
    """ Year widget """
    implementsOnly(IYearWidget)
    def extract(self, default=NOVALUE):
        day = self.request.get(self.name + '-day', default)
        year = self.request.get(self.name + '-year', default)
        month = self.request.get(self.name + '-month', default)
        # only make default for day/month if year is set !
        if year != default:
            if day == default:
                self.request.form[self.name + '-day'] = '1'
            if month == default:
                self.request.form[self.name + '-month'] = '1'
        return AbstractDXDateWidget.extract(self)

@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def YearFieldWidget(field, request):
    """IFieldWidget factory for YearWidget."""
    return FieldWidget(field, YearWidget(request))


