from datetime import date, datetime, timedelta
from DateTime import DateTime
import pytz

from zope.i18n import translate
from plone.formwidget.datetime import MessageFactory as _
from collections import deque


def rotated(sequence, steps):
    """Returns a (shallow) copy of the ``sequence`` rotated ``steps``
    times to the right.
    """
    dq = deque(sequence)
    dq.rotate(steps)
    return list(dq)


def is_pure_date(instance):
    return (isinstance(instance, date)
            and not isinstance(instance, datetime))

class AbstractDateWidget(object):

    calendar_type = 'gregorian'
    klass = u'date-widget'
    empty_value = ('', '', '')
    years_range = (-10, 10)
    pattern = None # zope.i18n format (default: u'M/d/yyyy')
    value = empty_value

    #
    # pure javascript no dependencies
    show_today_link = False

    # Requires: jquery.tools.datewidget.js, jquery.js
    # Read more: http://flowplayer.org/tools/dateinput/index.html
    show_jquerytools_dateinput = True

    base_jquerytools_dateinput_config = 'selectors: true, ' \
            'trigger: true, ' \
            'format: \'mm/dd/yyyy\', '\
            'yearRange: [%s, %s]'


    @property
    def with_time(self):
        return 'time' in self.__class__.__name__.lower()

    @property
    def jquerytools_dateinput_config(self):
        config = self.base_jquerytools_dateinput_config
        if 'yearRange' in config:
            config = config % self.years_range
        return config
    # TODO: yearRange shoud respect site_properties values for
    #       calendar_starting_year and valendar_future_years_avaliable

    @property
    def years(self):
        """years."""
        # 0: year
        value = self.value[0]
        if not value:
            value = datetime.now().year
        now = int(value)
        before = now + self.years_range[0]
        after  = now + self.years_range[1]
        year_range = range(*(before, after))
        return [{'value': x, 'name': x} for x in year_range]

    def get_formatted_value(self, dt_value):
        # due to fantastic datetime.strftime we need this hack
        # for now ctime is default
        # but some persons have already a patched version
        # of python working for older years.
        if not dt_value:
            return ''
        if isinstance(dt_value, DateTime):
            dt_value =  dt_value.asdatetime()
        eraise = True
        if dt_value.year < 1900:
            eraise = False
        try:
            formater = self._dtformatter
            if self.pattern is not None:
                formater.setPattern(self.pattern)
            return formater.format(dt_value)
        except ValueError, e:
            if not eraise:
                pass
        date_fmt = '%Y/%m/%d %H:%M'
        # special handles for month and year/month patterns
        if not self.with_time:
            date_fmt = '%Y/%m/%d'
        if self.pattern == 'yyyy':
            date_fmt = '%Y'
        if self.pattern == 'yy':
            date_fmt = '%y'
        if self.pattern == 'yyyy/M':
            date_fmt = '%Y/%m'
        if self.pattern == 'M/yyyy':
            date_fmt = '%m/%Y'
        if self.pattern == 'yy/M':
            date_fmt = '%y/%m'
        if self.pattern == 'M/yy':
            date_fmt = '%m/%y'
        try:
            # try to format with bare python (no i18n)
            # it can do mervelous things with this
            # patch to handle old years:
            # https://github.com/minitage-dependencies/python-2.7/blob/master/patches/strftime-pre-1900.patch
            # you can also find this patch
            # on the python tracker)
            return dt_value.strftime(date_fmt)
        except Exception, e:
            try:
                dt = ''
                # try to fallback to DateTime repr()
                # be sure to call datetime methods or date
                # only if we have the right underlying object
                if not self.with_time or (
                    self.with_time
                    and is_pure_date(dt_value)):
                    dt = '%s-%s-%s' % (
                        dt_value.year,
                        dt_value.month,
                        dt_value.day)
                else:
                    dt = '%s-%s-%s %s:%s:%s.%s' % (
                        dt_value.year,
                        dt_value.month,
                        dt_value.day,
                        dt_value.hour,
                        dt_value.minute,
                        dt_value.second,
                        dt_value.microsecond
                    )
                    if dt_value.tzinfo is not None:
                        if dt_value.tzinfo.utcoffset(
                            dt_value) is not None:
                            dt += ' %s' % str(
                                dt_value.tzinfo)
                # ATTENTION / WARNING
                # its important to call DateTime with a
                # regular python datetime for it not to
                # break old dates < 100 (like 99)
                # because they would be translited to eg: 1999
                if dt:
                    dt = DateTime(dt)
                    if len(str(dt_value.year)) < 3:
                        date_fmt = date_fmt.replace('Y', 'y')
                    dt =  dt.strftime(date_fmt)
                return dt
            except Exception, e:
                # last resort is ctime
                return dt_value.ctime()

    def dtformatter_to_full_year(self, dt_type):
        formater = None
        try:
            formater = self.request.locale.dates.getFormatter(
                dt_type, "short")
            pattern = formater._pattern
            if (isinstance(pattern, basestring)
                and  ('yy' in pattern)
                and (not 'yyyy' in pattern)):
                formater._pattern = pattern.replace('yy', 'yyyy')
                bin_pattern = formater._bin_pattern[:]
                for i, info in enumerate(bin_pattern):
                    if 'y' == info[0]:
                        formater._bin_pattern[i] = (info[0],  4)
        except AttributeError, e:
            """Tests case, no request"""
            pass
        return formater

    @property
    def _dtformatter(self):
        return self.dtformatter_to_full_year("date")

    @property
    def formatted_value(self):
        if self.value in (self.empty_value, None):
            return ''
        dt_value = self._dtvalue(self.value)
        return self.get_formatted_value(dt_value)

    @property
    def months(self):
        try:
            selected = int(self.month)
        except:
            selected = -1

        calendar = self.request.locale.dates.calendars[self.calendar_type]
        month_names = calendar.getMonthNames()

        for i, month in enumerate(month_names):
            yield dict(
                name=month,
                value=i+1,
                selected=i+1 == selected)

    @property
    def days(self):
        day_range = range(1, 32)
        return [{'value': x, 'name': self._padded_value(x)} for x in day_range]

    @property
    def year(self):
        year = self.request.get(self.name+'-year', None)
        if year is not None:
            return year
        if self.value[0] != self.empty_value[0]:
            return self.value[0]
        return None

    @property
    def month(self):
        month = self.request.get(self.name+'-month', None)
        if month:
            return month
        if self.value[1] != self.empty_value[1]:
            return self.value[1]
        return None

    @property
    def day(self):
        day = self.request.get(self.name+'-day', None)
        if day is not None:
            return day
        if self.value[2] == 1:
            return 1
        if self.value[2] != self.empty_value[2]:
            return self.value[2]
        return None

    def _padded_value(self, value):
        return str(value).zfill(2)

    def show_today_link_js(self, fieldname=None):
        id = fieldname and fieldname or self.id
        now = datetime.today()
        show_link_func = id+'-show-today-link'
        for i in ['-', '_']:
            show_link_func = show_link_func.replace(i, '')
        return '<a href="#" onclick="' \
            'document.getElementById(\'%(id)s-day\').value = %(day)s;' \
            'document.getElementById(\'%(id)s-month\').value = %(month)s;' \
            'document.getElementById(\'%(id)s-year\').value = %(year)s;' \
            'return false;">%(today)s</a>' % dict(
                id=id,
                day=now.day,
                month=now.month,
                year=now.year,
                today=translate(_(u"Today"), context=self.request)
            )

    @property
    def js_value(self):
        year = self.year
        month = None
        month = self.month and int(self.month) - 1 or None

        day = self.day
        if year and month and day:
            return 'new Date(%s, %s, %s)' % (
                year, month, day)
        else:
            return ''

    def _base_dtvalue(self, func, value):
        if value:
            # either no noaive datetime or date
            if (len(value) in [4, 6]) and value[-1]:
                timezone = pytz.timezone(value[-1])
                return func(*map(int, value[:-1]), tzinfo=timezone)
            else:
                if (len(value) in [4, 6]) and not value[-1]:
                    # tz is empty
                    value = value[:-1]
                return func(*map(int, value))

    def _dtvalue(self, value):
        return self._base_dtvalue(date, value)

    def get_js(self, fieldname=None):
        # TODO:
        #     * check if self.name must always be self.name or fieldname if
        #       given (search for other self.name appearances)
        #     * has value be passed here from at-template?
        # archetypes based widget have to pass id and name from the template
        id = fieldname and fieldname or self.id
        name = fieldname and fieldname or self.name

        language = self.request.get('LANGUAGE', 'en')
        calendar = self.request.locale.dates.calendars[self.calendar_type]
        
        localize = 'jQuery.tools.dateinput.localize("' + language + '", {'
        localize += 'months: "%s",' % ','.join(calendar.getMonthNames())
        localize += 'shortMonths: "%s",' % ','.join(
            calendar.getMonthAbbreviations()
        )
        # jQuery Tools datepicker wants the days to always start with Sunday and
        # uses the 'firstDay' option to reorder them if required. The .getDayNames()
        # and .getDayAbbreviations() return the days beginning with monday, which
        # is why those lists need to be rotated by one
        localize += 'days: "%s",' % ','.join(
            rotated(calendar.getDayNames(), 1))

        localize += 'shortDays: "%s",' % ','.join(
            rotated(calendar.getDayAbbreviations(), 1))
        localize += '});'
        localize = localize.replace(',}', '}')

        config = 'lang: "%s", ' % language
        if self.js_value:
            config += 'value: %s, ' % self.js_value
        config += 'firstDay: %s, ' % calendar.week.get('firstDay', 0)

        config += ('change: function() {\n'
                   '  var value = this.getValue("yyyy-m-d").split("-");\n'
                   '  jQuery("#%(id)s-year").val(value[0]); \n' \
                   '  jQuery("#%(id)s-month").val(value[1]); \n' \
                   '  jQuery("#%(id)s-day").val(value[2]); \n' \
                   '}, ') % dict(id=id)
        config += self.jquerytools_dateinput_config

        return '''
            <input type="hidden"
                id="%(id)s-calendar"
                name="%(name)s-calendar"
                class="%(name)s-calendar" />
            <script type="text/javascript">
                if (jQuery().dateinput) {
                    %(localize)s
                    jQuery("#%(id)s-calendar").dateinput({%(config)s}).unbind('change')
                        .bind('onShow', function (event) {
                            var trigger_offset = jQuery(this).next().offset();
                            jQuery(this).data('dateinput').getCalendar().offset(
                                {top: trigger_offset.top+20, left: trigger_offset.left}
                            );
                        });
                }
                function updateCalendar(widgetId) {
                    var y = jQuery(widgetId + '-year').val();
                    var m = jQuery(widgetId + '-month').val();
                    var d = jQuery(widgetId + '-day').val();
                    if (!y || !m || !d) {
                        return;
                    }
                    var newDate = new Date(m + '/' + d + '/' + y);
                    if (newDate.getYear()) { // return NaN (which is false) if the date is invalid
                        jQuery(widgetId + '-calendar').val(m + '/' + d + '/' + y);
                        jQuery(widgetId + '-calendar').data()['dateinput'].setValue(newDate);
                    }
                }
            </script>''' % dict(
                id=id, name=name,
                config=config, localize=localize
            )

    def onchange(self, fieldname=None):
        if not self.show_jquerytools_dateinput:
            return ''

        id = fieldname and fieldname or self.id
        return "updateCalendar('#%(id)s');" % dict(id=id)


class AbstractDatetimeWidget(AbstractDateWidget):

    empty_value = ('', '', '', '00', '00', '')
    value = empty_value
    klass = u'datetime-widget'
    ampm = False
    pattern = None # (default: u'M/d/yyyy h:mm a'')

    @property
    def _dtformatter(self):
        return self.dtformatter_to_full_year("dateTime")

    def _dtvalue(self, value):
        return self._base_dtvalue(datetime, value)

    @property
    def hour(self):
        hour = self.request.get(self.name+'-hour', None)
        if hour is not None:
            return hour
        if self.value[3] != self.empty_value[3]:
            return self.value[3]
        return None

    @property
    def minute(self):
        minute = self.request.get(self.name+'-minute', None)
        if minute is not None:
            return minute
        if self.value[4] != self.empty_value[4]:
            return self.value[4]
        return None

    def is_pm(self):
        hour = self.hour
        if hour in (None, '') or int(hour) < 12:
            return False
        return True

    @property
    def timezone(self):
        timezone = self.request.get(self.name+'-timezone', None)
        if timezone:
            return timezone
        if self.value[5] != self.empty_value[5]:
            return self.value[5]
        return None

    @property
    def minutes(self):
        return [{'value': x, 'name': self.padded_minute(x)} for x in range(60)]

    @property
    def hours(self):
        return [{'value': x, 'name': self.padded_hour(x)} for x in range(24)]

    def padded_hour(self, hour=None):
        hour = hour is not None and hour or self.hour
        if hour not in (None, ''):
            pm = self.is_pm()
            if self.ampm is True and pm and int(hour)!=12:
                hour = str(int(hour)-12)
            if self.ampm is True and not pm and int(hour)==0:
                hour = u'12'  # 12 a.m. midnight hour == 00:** hour
            return self._padded_value(hour)
        else:
            return None

    def padded_minute(self, minute=None):
        minute = minute is not None and minute or self.minute
        if minute is not None:
            return self._padded_value(minute)
        else:
            return None

    @property
    def js_value(self):
        year = self.year
        month = self.month and int(self.month) - 1 or None
        day = self.day
        hour = self.hour
        minute = self.minute
        if (year is not None
            and month is not None
            and day is not None
            and hour is not None
            and minute is not None):
            return 'new Date(%s, %s, %s, %s, %s)' % (
                year, month, day, hour, minute)
        elif year and month and day:
            return 'new Date(%s, %s, %s)' % (
                year, month, day)
        else:
            return None

class AbstractMonthYearWidget(AbstractDateWidget):

    klass = u'monthyear-widget'
    empty_value = ('', '', 1)
    value = empty_value
    pattern = 'yyyy/M'


class AbstractYearWidget(AbstractDateWidget):

    klass = u'year-widget'
    empty_value = ('', 1, 1)
    value = empty_value
    pattern = 'yyyy'
