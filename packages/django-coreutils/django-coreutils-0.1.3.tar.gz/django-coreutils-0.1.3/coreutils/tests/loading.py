# coding: utf8


from testutils import BaseTestCase

from ..loading import load_module


class TestLoading(BaseTestCase):
    def test_valid_path(self):
        self.assertEqual(
            load_module('coreutils.loading.load_module'), load_module
        )

    def test_empty_path(self):
        with self.assertRaises(ValueError):
            load_module('')

    def test_invalid_path(self):
        with self.assertRaises(ImportError):
            load_module('core.utils.loading.load_module')
