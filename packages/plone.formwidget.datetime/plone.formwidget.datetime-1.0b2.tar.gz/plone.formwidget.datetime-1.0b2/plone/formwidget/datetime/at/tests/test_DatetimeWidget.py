from plone.formwidget.datetime.at.widget import DateWidget
from plone.formwidget.datetime.base import AbstractDatetimeWidget
from plone.formwidget.datetime.at.widget import DatetimeWidget
from DateTime import DateTime
from Products.Archetypes.Field import DateTimeField
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from plone.formwidget.datetime.testing import PFWDT_INTEGRATION_TESTING
from plone.formwidget.datetime.at.browser import widget as bw
import datetime
import mock
from DateTime import DateTime
import unittest2 as unittest


class TestDatetimeWidget(unittest.TestCase):

    def createInstance(self):
        return DatetimeWidget()

    def test_subclass(self):
        self.assertTrue(DatetimeWidget, (AbstractDatetimeWidget, DateWidget))

    def test__properties(self):
        instance = self.createInstance()
        self.assertEqual(
            instance._properties,
            {
                'show_calendar': True,
                'helper_css': (),
                'years_range': (-10, 10),
                'description': '',
                'populate': True,
                'show_day': True,
                'show_month': True,
                'macro': 'datetime_input',
                'postback': True,
                'label': '',
                'visible': {'edit': 'visible', 'view': 'visible'},
                'blurrable': False,
                'modes': ('view', 'edit'),
                'show_content_type': False,
                'condition': '',
                'helper_js': ()
            }
        )



    def test_process_form_with_valid_date_without_ampm(self):
        instance = self.createInstance()
        ins = mock.Mock()
        field = mock.Mock()
        field.getName.return_value = 'field'
        form = {
            'field-calendar': 'value',
            'field-year': '2011',
            'field-month': '11',
            'field-day': '22',
            'field-hour': '13',
            'field-minute': '30',
        }
        self.assertEqual(
            instance.process_form(ins, field, form)[0].asdatetime(),
            (datetime.datetime(2011, 11, 22, 13, 30))
        )
        self.assertEqual(
            form['field'].asdatetime(),
            datetime.datetime(2011, 11, 22, 13, 30)
        )

    def test_process_form_with_valid_date_pm(self):
        instance = self.createInstance()
        ins = mock.Mock()
        field = mock.Mock()
        field.getName.return_value = 'field'
        form = {
            'field-calendar': 'value',
            'field-year': '2011',
            'field-month': '11',
            'field-day': '22',
            'field-hour': '2',
            'field-minute': '30',
            'field-ampm': 'PM',
        }
        self.assertEqual(
            instance.process_form(ins, field, form)[0].asdatetime(),
            (datetime.datetime(2011, 11, 22, 14, 30))
        )
        self.assertEqual(
            form['field'].asdatetime(),
            datetime.datetime(2011, 11, 22, 14, 30)
        )

    def test_process_form_with_valid_date_am(self):
        instance = self.createInstance()
        ins = mock.Mock()
        field = mock.Mock()
        field.getName.return_value = 'field'
        form = {
            'field-calendar': 'value',
            'field-year': '2011',
            'field-month': '11',
            'field-day': '22',
            'field-hour': '12',
            'field-minute': '30',
            'field-ampm': 'AM',
        }
        self.assertEqual(
            instance.process_form(ins, field, form)[0].asdatetime(),
            (datetime.datetime(2011, 11, 22, 0, 30))
        )
        self.assertEqual(
            form['field'].asdatetime(),
            datetime.datetime(2011, 11, 22, 0, 30)
        )

    def test_process_form_with_oldyear(self):
        instance = self.createInstance()
        ins = mock.Mock()
        field = mock.Mock()
        field.getName.return_value = 'field'
        form = {
            'field-calendar': 'value',
            'field-year': '99',
            'field-month': '11',
            'field-day': '22',
            'field-hour': '12',
            'field-minute': '30',
            'field-ampm': 'AM',
        }
        self.assertEqual(
            instance.process_form(ins, field, form)[0].asdatetime(),
            (datetime.datetime(99, 11, 22, 0, 30))
        )
        self.assertEqual(
            form['field'].asdatetime(),
            datetime.datetime(99, 11, 22, 0, 30)
        )
