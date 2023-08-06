# coding: utf8


class RequestFormMixin(object):
    def __init__(self, request, *args, **kwargs):
        self.request = request
        return super(RequestFormMixin, self).__init__(*args, **kwargs)
