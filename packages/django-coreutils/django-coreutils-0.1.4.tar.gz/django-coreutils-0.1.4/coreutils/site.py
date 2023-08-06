# coding: utf8

from django.conf import settings
from django.contrib.sites.models import Site


def get_default_site_url():
    """
    Returns the url for the default site. If settings.DEBUG is True
    'localhost:8000' will be returned.
    """
    if settings.DEBUG:
        return 'localhost:8000'
    return Site.objects.get_current().domain
