from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class Base(BrowserView):
    template = ViewPageTemplateFile('datetime_input.pt')

    @property
    def macros(self):
        return self.template.macros


class DateWidget(Base):
    """ view klass for DateWidget """


class DatetimeWidget(Base):
    """ view klass for DatetimeWidget """


class MonthYearWidget(Base):
    """ view klass for MonthYearWidget """


class YearWidget(Base):
    """ view klass for YearWidget """


