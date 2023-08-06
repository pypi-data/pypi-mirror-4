
from DateTime import DateTime
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.formwidget.datetime.at.widget import (
    DatetimeWidget,
    YearWidget,
    MonthYearWidget,
    DateWidget,)
from plone.formwidget.datetime.testing import PFWDT_INTEGRATION_TESTING
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView
import datetime
import unittest2 as unittest

class BaseTestDatetimeIWidget(unittest.TestCase):
    layer = PFWDT_INTEGRATION_TESTING
    fid = 'modification_date'

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.folder =  (
            'f1' in self.portal.objectIds()
            and self.portal['f1']
            or self.portal[
                self.portal.invokeFactory('Folder', 'f1')])
        self.folder.schema[self.fid
                          ].widget = self.createInstance()
        self.request = self.layer['request']
        self.field = self.folder.Schema()[self.fid]
        class B(BrowserView):
            template = ViewPageTemplateFile('testv.pt')
            def render(self, **kw):
                return self.template(**kw)
        self.v = B(self.folder, self.request)

    def createInstance(self):
        raise Exception('notimplemented')

class TestDatetimeIWidget(BaseTestDatetimeIWidget):
    def createInstance(self):
        mrange = (datetime.datetime.now() - datetime.datetime(1,1,1)).days/365
        return DatetimeWidget(years_range=(-mrange, 10))

    def test_a_render_yearsrange(self):
        dt = DateTime(
            datetime.datetime(99,1,2,3,4))
        self.folder.getField(self.fid).set(self.folder, dt)
        res1 = self.v.render(field=self.field, mode='edit')
        dt = DateTime(
            datetime.datetime(1910,1,2,3,4))
        self.folder.getField(self.fid).set(self.folder, dt)
        res2 = self.v.render(field=self.field, mode='edit')
        dt = DateTime(
            datetime.datetime(2000,1,2,3,4))
        self.folder.getField(self.fid).set(self.folder, dt)
        res3 = self.v.render(field=self.field, mode='edit')
        tests = [
            ('<option selected="selected" value="99">99</option>', res1, True),
            ('<option selected="selected" value="1910">1910</option>', res2, True),
            ('<option selected="selected" value="2000">2000</option>', res3, True),
        ]
        for i, content, v in tests:
            self.assertTrue(v==(i in content), i)

    def test_view_render_DateTime(self):
        dt = DateTime(datetime.datetime(99,1,2,3,4))
        self.folder.getField(self.fid).set(self.folder, dt)
        res = self.v.render(field=self.field, mode='view').strip()
        REF = u'<span>99/01/02 03:04</span>'
        self.assertEqual(res, REF)

    def test_view_render_datetime(self):
        dt = datetime.datetime(99,1,2,3,4)
        self.folder.getField(self.fid).set(self.folder, dt)
        res = self.v.render(field=self.field, mode='view').strip()
        REF = u'<span>1999/01/02 03:04</span>'
        self.assertEqual(res, REF)

    def test_edit_render_date(self):
        dt = DateTime('0099/01/02')
        self.folder.getField(self.fid).set(self.folder, dt)
        res = self.v.render(field=self.field, mode='edit')
        tests = [
            ('<option selected="selected" value="2">02</option>', True),
            ('<option selected="selected" value="3">03</option>', False),
            ('<option selected="selected" value="4">04</option>', False),
            ('<option selected="selected" value="1">1</option>' , True),
        ]
        for i, v in tests:
            self.assertTrue(v==(i in res), i)

    def test_edit_render_DateTime(self):
        dt = DateTime(
            datetime.datetime(99,1,2,3,4))
        self.folder.getField(self.fid).set(self.folder, dt)
        res = self.v.render(field=self.field, mode='edit')
        tests = [
            '<option selected="selected" value="2">02</option>',
            '<option selected="selected" value="3">03</option>',
            '<option selected="selected" value="4">04</option>',
            '<option selected="selected" value="1">1</option>',
        ]
        for i in tests:
            self.assertTrue(i in res, i)


    def test_edit_render_datetime(self):
        dt = datetime.datetime(99,1,2,3,4)
        self.folder.getField(self.fid).set(self.folder, dt)
        res = self.v.render(field=self.field, mode='edit')
        tests = [
            '<option selected="selected" value="2">02</option>',
            '<option selected="selected" value="3">03</option>',
            '<option selected="selected" value="4">04</option>',
            '<option selected="selected" value="1">1</option>',
        ]
        for i in tests:
            self.assertTrue(i in res, i)

    def test_edit_render_request(self):
        self.request.form.update({
            '%s-year'  % self.fid : '2012',
            '%s-month' % self.fid : '1',
            '%s-day'   % self.fid : '2',
            '%s-hour'  % self.fid : '4',
            '%s-minute'% self.fid : '5',
        })
        res = self.v.render(field=self.field, mode='edit')
        self.assertTrue(
            '<option selected="selected" value="5">05</option>'
            in res)
        self.assertTrue(
            '<option selected="selected" value="4">04</option>'
            in res)
        self.assertTrue(
            '<option selected="selected" value="1">1</option>'
            in res)
        self.assertTrue(
            '<option selected="selected" value="2">02</option>'
            in res)
        self.assertTrue(
            '<option selected="selected" value="2012">2012</option>'
            in res)

class TestDateIWidget(BaseTestDatetimeIWidget):
    def createInstance(self):
        return DateWidget()

    def test_view_render_DateTime(self):
        dt = DateTime(datetime.datetime(99,1,2,3,4))
        self.folder.getField(self.fid).set(self.folder, dt)
        res = self.v.render(field=self.field, mode='view').strip()
        REF = u'<span>99/01/02</span>'
        self.assertEqual(res, REF)

    def test_view_render_datetime(self):
        dt = datetime.datetime(99,1,2,3,4)
        self.folder.getField(self.fid).set(self.folder, dt)
        res = self.v.render(field=self.field, mode='view').strip()
        REF = u'<span>1999/01/02</span>'
        self.assertEqual(res, REF)

    def test_edit_render_date(self):
        dt = DateTime('0099/01/02')
        self.folder.getField(self.fid).set(self.folder, dt)
        res = self.v.render(field=self.field, mode='edit')
        tests = [
            ('<option selected="selected" value="2">02</option>', True),
            ('<option selected="selected" value="3">03</option>', False),
            ('<option selected="selected" value="4">04</option>', False),
            ('<option selected="selected" value="1">1</option>' , True),
        ]
        for i, v in tests:
            self.assertTrue(v==(i in res), i)

    def test_edit_render_DateTime(self):
        dt = DateTime(
            datetime.datetime(99,1,2,3,4))
        self.folder.getField(self.fid).set(self.folder, dt)
        res = self.v.render(field=self.field, mode='edit')
        tests = [
            ('<option selected="selected" value="2">02</option>', True),
            ('<option selected="selected" value="3">03</option>', False),
            ('<option selected="selected" value="4">04</option>', False),
            ('<option selected="selected" value="1">1</option>' , True),
        ]
        for i, v in tests:
            self.assertTrue(v==(i in res), i)


    def test_edit_render_datetime(self):
        dt = datetime.datetime(99,1,2,3,4)
        self.folder.getField(self.fid).set(self.folder, dt)
        res = self.v.render(field=self.field, mode='edit')
        tests = [
            ('<option selected="selected" value="2">02</option>', True),
            ('<option selected="selected" value="3">03</option>', False),
            ('<option selected="selected" value="4">04</option>', False),
            ('<option selected="selected" value="1">1</option>' , True),
        ]
        for i, v in tests:
            self.assertTrue(v==(i in res), i)


    def test_edit_render_request(self):
        self.request.form.update({
            '%s-year'  % self.fid : '2012',
            '%s-month' % self.fid : '1',
            '%s-day'   % self.fid : '2',
            '%s-hour'  % self.fid : '4',
            '%s-minute'% self.fid : '5',
        })
        res = self.v.render(field=self.field, mode='edit')
        self.assertFalse(
            '<option selected="selected" value="5">05</option>'
            in res)
        self.assertFalse(
            '<option selected="selected" value="4">04</option>'
            in res)
        self.assertTrue(
            '<option selected="selected" value="1">1</option>'
            in res)
        self.assertTrue(
            '<option selected="selected" value="2">02</option>'
            in res)
        self.assertTrue(
            '<option selected="selected" value="2012">2012</option>'
            in res)

class TestYearIWidget(BaseTestDatetimeIWidget):
    def createInstance(self):
        return YearWidget()

    def test_view_render_DateTime(self):
        dt = DateTime(datetime.datetime(99,1,2,3,4))
        self.folder.getField(self.fid).set(self.folder, dt)
        res = self.v.render(field=self.field, mode='view').strip()
        REF = u'<span>99</span>'
        self.assertEqual(res, REF)

    def test_view_render_datetime(self):
        dt = datetime.datetime(99,1,2,3,4)
        self.folder.getField(self.fid).set(self.folder, dt)
        res = self.v.render(field=self.field, mode='view').strip()
        REF = u'<span>1999</span>'
        self.assertEqual(res, REF)

    def test_edit_render_date(self):
        dt = DateTime('0099/01/02')
        self.folder.getField(self.fid).set(self.folder, dt)
        res = self.v.render(field=self.field, mode='edit')
        tests = [
            ('<input type="hidden" name="modification_date-day" value="2">', True),
            ('<input type="hidden" name="modification_date-month" value="1">', True),
            ('<option selected="selected" value="3">03</option>', False),
            ('<option selected="selected" value="4">04</option>', False),
        ]
        for i, v in tests:
            self.assertTrue(v==(i in res), i)

    def test_edit_render_DateTime(self):
        dt = DateTime(
            datetime.datetime(99,1,2,3,4))
        self.folder.getField(self.fid).set(self.folder, dt)
        res = self.v.render(field=self.field, mode='edit')
        tests = [
            ('<option selected="selected" value="3">03</option>', False),
            ('<option selected="selected" value="4">04</option>', False),
        ]
        for i, v in tests:
            self.assertTrue(v==(i in res), i)


    def test_edit_render_datetime(self):
        dt = datetime.datetime(99,1,2,3,4)
        self.folder.getField(self.fid).set(self.folder, dt)
        res = self.v.render(field=self.field, mode='edit')
        tests = [
            ('<input type="hidden" name="modification_date-day" value="2">', True),
            ('<input type="hidden" name="modification_date-month" value="1">', True),
            ('<option selected="selected" value="3">03</option>', False),
            ('<option selected="selected" value="4">04</option>', False),
        ]
        for i, v in tests:
            self.assertTrue(v==(i in res), i)


    def test_edit_render_request(self):
        self.request.form.update({
            '%s-year'  % self.fid : '2012',
            '%s-month' % self.fid : '1',
            '%s-day'   % self.fid : '2',
            '%s-hour'  % self.fid : '4',
            '%s-minute'% self.fid : '5',
        })
        res = self.v.render(field=self.field, mode='edit')
        self.assertFalse(
            '<option selected="selected" value="5">05</option>'
            in res)
        self.assertFalse(
            '<option selected="selected" value="4">04</option>'
            in res)
        self.assertTrue(
           '<input type="hidden" name="modification_date-day" value="2">'
            in res)
        self.assertTrue(
            '<input type="hidden" name="modification_date-month" value="1">'
            in res)
        self.assertTrue(
            '<option selected="selected" value="2012">2012</option>'
            in res)


class TestYearMonthIWidget(BaseTestDatetimeIWidget):
    def createInstance(self):
        return MonthYearWidget()

    def test_view_render_DateTime(self):
        dt = DateTime(datetime.datetime(99,1,2,3,4))
        self.folder.getField(self.fid).set(self.folder, dt)
        res = self.v.render(field=self.field, mode='view').strip()
        # with a patched python
        # month is in integer form, non zero padded
        EITHER = [u'<span>99/1</span>',
                  u'<span>99/01</span>'
                 ]
        self.assertTrue(
            True
            in [a in res for a in EITHER])

    def test_a_view_render_datetime(self):
        dt = datetime.datetime(99,6,2,3,4)
        self.folder.getField(self.fid).set(self.folder, dt)
        res = self.v.render(field=self.field, mode='view').strip()
        REF = u'<span>1999/6</span>'
        self.assertEqual(res, REF)

    def test_edit_render_date(self):
        dt = DateTime('0099/01/02')
        self.folder.getField(self.fid).set(self.folder, dt)
        res = self.v.render(field=self.field, mode='edit')
        tests = [
            ('<input type="hidden" name="modification_date-day" value="2">', True),
            ('<option selected="selected" value="1">1</option>' , True),
            ('<option selected="selected" value="3">03</option>', False),
            ('<option selected="selected" value="4">04</option>', False),
        ]
        for i, v in tests:
            self.assertTrue(v==(i in res), i)

    def test_edit_render_DateTime(self):
        dt = DateTime(
            datetime.datetime(99,1,2,3,4))
        self.folder.getField(self.fid).set(self.folder, dt)
        res = self.v.render(field=self.field, mode='edit')
        tests = [
            ('<input type="hidden" name="modification_date-day" value="2">', True),
            ('<option selected="selected" value="1">1</option>' , True),
            ('<option selected="selected" value="3">03</option>', False),
            ('<option selected="selected" value="4">04</option>', False),
        ]
        for i, v in tests:
            self.assertTrue(v==(i in res), i)


    def test_edit_render_datetime(self):
        dt = datetime.datetime(99,1,2,3,4)
        self.folder.getField(self.fid).set(self.folder, dt)
        res = self.v.render(field=self.field, mode='edit')
        tests = [
            ('<input type="hidden" name="modification_date-day" value="2">', True),
            ('<option selected="selected" value="1">1</option>' , True),
            ('<option selected="selected" value="3">03</option>', False),
            ('<option selected="selected" value="4">04</option>', False),
        ]
        for i, v in tests:
            self.assertTrue(v==(i in res), i)


    def test_edit_render_request(self):
        self.request.form.update({
            '%s-year'  % self.fid : '2012',
            '%s-month' % self.fid : '1',
            '%s-day'   % self.fid : '2',
            '%s-hour'  % self.fid : '4',
            '%s-minute'% self.fid : '5',
        })
        res = self.v.render(field=self.field, mode='edit')
        self.assertTrue(
            '<option selected="selected" value="1">1</option>'
            in res)
        self.assertFalse(
            '<option selected="selected" value="5">05</option>'
            in res)
        self.assertFalse(
            '<option selected="selected" value="4">04</option>'
            in res)
        self.assertTrue(
           '<input type="hidden" name="modification_date-day" value="2">'
            in res)
        self.assertTrue(
            '<option selected="selected" value="2012">2012</option>'
            in res)

