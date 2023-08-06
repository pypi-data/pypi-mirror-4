# coding: utf8

from django.conf import settings

from testutils import BaseTestCase

from ..settings import get_setting


class TestSettings(BaseTestCase):
    def test_single_valid_without_default(self):
        self.assertEqual(get_setting('USE_I18N'), settings.USE_I18N)

    def test_multiple_valid_without_default(self):
        self.assertEqual(get_setting('USE_I18NN', 'SITE_ID'), settings.SITE_ID)

    def test_single_invalid_without_default(self):
        self.assertEqual(get_setting('USE_I18NN'), None)

    def test_multiple_invalid_without_default(self):
        self.assertEqual(get_setting('USE_I18NN', 'SITE_IDD'), None)

    def test_single_valid_with_default(self):
        self.assertEqual(
            get_setting('USE_I18N', default='test'), settings.USE_I18N
        )

    def test_multiple_valid_with_default(self):
        self.assertEqual(
            get_setting('USE_I18NN', 'SITE_ID', default='test'),
            settings.SITE_ID
        )

    def test_single_invalid_with_default(self):
        self.assertEqual(get_setting('USE_I18NN', default='test'), 'test')

    def test_multiple_invalid_with_default(self):
        self.assertEqual(
            get_setting('USE_I18NN', 'SITE_IDD', default='test'), 'test'
        )
