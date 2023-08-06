# coding: utf8

from django.core.exceptions import ImproperlyConfigured

from ..url import get_url


class SuccessFormViewMixin(object):
    success_url = None
    success_url_name = None

    def get_success_url(self):
        if not self.success_url and self.success_url_name:
            url = get_url(self.success_url_name)
        elif self.success_url:
            url = self.success_url
        else:
            raise ImproperlyConfigured(
                'No URL to redirect to. Provide a success_url or '
                'success_url_name.'
            )
        return url
