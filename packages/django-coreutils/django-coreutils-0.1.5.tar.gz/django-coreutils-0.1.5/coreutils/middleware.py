# coding: utf8

import logging
from urlparse import urlparse

from .context_processors import site_url

log = logging.getLogger('coreutils.middleware')


class SiteUrlMiddleware(object):
    def process_request(self, request):
        request.site_url = site_url()


class SubdomainMiddleware(object):
    def process_request(self, request):
        request.hostname = urlparse(
            request.build_absolute_uri()
        ).hostname

        bits = request.hostname.split('.')

        if len(bits) == 3:
            request.subdomain = bits[0]
            request.domain = bits[1]
        else:
            request.subdomain = None
            request.domain = bits[0]

        request.tld = bits[-1]

        log.debug('domain: %s subdomain: %s tld: %s' % (
            request.domain,
            request.subdomain,
            request.tld
        ))
