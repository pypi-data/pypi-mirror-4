from z3c.form.interfaces import IWidget
from zope.schema import ValidationError
from zope.schema import Bool
from zope.schema.interfaces import IDate, IDatetime

from plone.formwidget.datetime import MessageFactory as _


# Fields

class IDateField(IDate):
    """ Special marker for date fields that use our widget """

class IDatetimeField(IDatetime):
    """ Special marker for datetime fields that use our widget """


# Widgets

class IDateWidget(IWidget):
    """ Date widget marker for z3c.form """

    show_today_link = Bool(
        title=u'Show "today" link',
        description=(u'show a link that uses javascript to inserts '
                     u'the current date into the widget.'),
        default=False,
        )

class IDatetimeWidget(IWidget):
    """ Datetime widget marker for z3c.form """

class IMonthYearWidget(IWidget):
    """ MonthYear widget marker for z3c.form """


class IYearWidget(IWidget):
    """Year widget marker for z3c.form """ 
# Errors

class DateValidationError(ValidationError):
    __doc__ = _(u'Please enter a valid date.')

class DatetimeValidationError(ValidationError):
    __doc__ = _(u'Please enter a valid date and time.')
