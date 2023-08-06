# coding: utf8

from ..referer import get_referer_url


class RefererSuccessUrlMixin(object):
    @property
    def success_url(self):
        return get_referer_url(self.request)


class RefererCancelUrlMixin(object):
    def get_context_data(self, **kwargs):
        context = super(RefererCancelUrlMixin, self).get_context_data(**kwargs)
        context['cancel_url'] = get_referer_url(self.request)
        return context
