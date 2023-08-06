# coding: utf8

from django.core.urlresolvers import reverse


def get_url(name, **kwargs):
    return reverse(name, kwargs=kwargs)
