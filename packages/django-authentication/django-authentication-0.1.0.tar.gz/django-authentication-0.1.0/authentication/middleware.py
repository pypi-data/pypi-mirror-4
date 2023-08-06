# coding: utf8

import logging

from django.http import HttpResponsePermanentRedirect
from django.conf import settings

log = logging.getLogger('authentication.middleware.SecureRequiredMiddleware')


class SecureRequiredMiddleware(object):
    def __init__(self):
        self.paths = getattr(settings, 'SECURE_REQUIRED_PATHS')
        self.enabled = self.paths and getattr(settings, 'HTTPS_SUPPORT')

    def process_request(self, request):
        if self.enabled and not request.is_secure():
            full_path = request.get_full_path()

            for path in self.paths:
                if full_path.startswith(path):

                    secure_url = request.build_absolute_uri(full_path).replace(
                        'http://', 'https://'
                    )

                    log.debug('Redirecting to: %s' % secure_url)

                    return HttpResponsePermanentRedirect(secure_url)
        return None
