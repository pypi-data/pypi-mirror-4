# coding: utf8


class BaseViewMixin(object):
    def get_context_data(self, **kwargs):
        context = super(BaseViewMixin, self).get_context_data(**kwargs)
        context['page_title'] = self.page_title
        return context
