# coding: utf8

from datetime import timedelta

from django.utils.timezone import now

from testutils import BaseTestCase

from coreutils.templatetags.timeleft import get_timeleft


class TestTimeleft(BaseTestCase):
    def test_get_timeleft(self):
        self.assertEquals(
            '59 minutes', get_timeleft(now() + timedelta(hours=1))
        )

        self.assertEquals(
            '6 days, 23 hours', get_timeleft(now() + timedelta(weeks=1))
        )

        self.assertEquals(
            '0 minutes', get_timeleft(now() - timedelta(hours=1))
        )

        self.assertEquals(
            '0 minutes', get_timeleft(now() - timedelta(weeks=1))
        )
