# coding: utf8

from django.conf import settings
from django.test.utils import override_settings

from testutils import BaseTestCase

from ..backends import get_backend


class TestBackend(object):
    """ The test backend! """


class TestBackends(BaseTestCase):
    def setUp(self):
        settings.TEST_BACKEND = 'coreutils.tests.backends.TestBackend'

    def test_valid_path(self):
        self.assertEqual(
            get_backend(
                'TEST_BACKEND',
                settings.TEST_BACKEND,
                instantiate=False
            ), TestBackend
        )

    def test_valid_path_instantiate(self):
        self.assertEqual(
            get_backend(
                'TEST_BACKEND',
                settings.TEST_BACKEND
            ).__class__, TestBackend
        )

    @override_settings(TEST_BACKEND='')
    def test_empty_path(self):
        with self.assertRaises(ValueError):
            get_backend('TEST_BACKEND', None, instantiate=False)

    @override_settings(TEST_BACKEND='core.tests.backends.TestBackend')
    def test_invalid_path(self):
        with self.assertRaises(ImportError):
            get_backend('TEST_BACKEND', None, instantiate=False)
