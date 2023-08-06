# coding: utf8

from testutils import BaseTestCase

from ..url import get_url


class TestUrls(BaseTestCase):
    urls = 'coreutils.test_urls'

    def test_get_url(self):
        self.assertEqual(get_url('home'), '/')
