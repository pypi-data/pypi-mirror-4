# coding: utf8

from django.core.exceptions import ImproperlyConfigured

from ..url import get_url


class CancelUrlViewMixin(object):
    cancel_url = None
    cancel_url_name = None

    def get_cancel_url(self):
        if not self.cancel_url and self.cancel_url_name:
            url = get_url(self.cancel_url_name)
        elif self.cancel_url:
            url = self.cancel_url
        else:
            raise ImproperlyConfigured(
                'No URL to redirect to. Provide a cancel_url or '
                'cancel_url_name.'
            )
        return url

    def get_context_data(self, **kwargs):
        context = super(CancelUrlViewMixin, self).get_context_data(**kwargs)
        context['cancel_url'] = self.get_cancel_url()
        return context
