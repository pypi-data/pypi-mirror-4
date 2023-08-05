import unittest2 as unittest


class TestYearWidget(unittest.TestCase):

    def createInstance(self):
        from plone.formwidget.datetime.at.widget import YearWidget
        return YearWidget()

    def test_subclass(self):
        from plone.formwidget.datetime.at.widget import YearWidget
        from plone.formwidget.datetime.base import AbstractYearWidget
        from plone.formwidget.datetime.at.widget import DateWidget
        self.assertTrue(YearWidget, (AbstractYearWidget, DateWidget))

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
                'show_day': False,
                'show_month': False,
                'macro': 'year_input',
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
