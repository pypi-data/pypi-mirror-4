# coding: utf8

from testutils import BaseTestCase

from coreutils.templatetags.range import get_range


class TestRange(BaseTestCase):
    def test_get_range(self):
        self.assertEquals(range(10), get_range(10))
