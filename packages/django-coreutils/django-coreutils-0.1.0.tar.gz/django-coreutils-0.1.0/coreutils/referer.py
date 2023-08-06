# coding: utf8

import re

from django.core.urlresolvers import resolve


def get_referer_url(request, default='/'):
    referer = request.META.get('HTTP_REFERER')
    if not referer:
        return default
    return u'/' + u'/'.join(re.sub('^https?:\/\/', '', referer).split('/')[1:])


def get_referer_url_name(request, default='/'):
    return resolve(get_referer_url(request, default)).url_name
