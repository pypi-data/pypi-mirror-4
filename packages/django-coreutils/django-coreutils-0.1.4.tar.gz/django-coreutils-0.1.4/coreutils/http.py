# coding: utf8

from django.http import HttpResponse


class HttpResponseUnauthorized(HttpResponse):
    def __init__(self, *args, **kwargs):
        super(HttpResponseUnauthorized, self).__init__(*args, **kwargs)
        self.status_code = 401
