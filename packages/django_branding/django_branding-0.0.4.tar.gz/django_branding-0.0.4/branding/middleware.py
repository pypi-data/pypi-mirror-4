#!/usr/bin/env python
# -*- coding:  utf-8 -*-

from logging import getLogger

from django.conf import settings

logger = getLogger('branding')


class BrandingMiddleware(object):
    """Brand response headers
    """

    def process_response(self, request, response):
        """Add custom headers
        """

        for key, value in settings.BRANDING:
            response[key] = value

        platform = getattr(settings, "PLATFORM")
        server = getattr(settings, "X_SERVER")
        programming = getattr(settings, "X_PROGRAMMING")
        site_name = getattr(settings, "SITE_NAME")
        version = getattr(settings, 'VERSION')
        revision = getattr(settings, 'REVISION')

        if programming:
            response['X-Programming'] = programming

        if server:
            response['Server'] = server

        if platform:
            response['Link'] = "<%s>; rel=\"platform\"" % platform

        if site_name:
            response['X-Powered-By'] = site_name

        if version:
            response['X-Version'] = version

        if revision:
            response['X-Revision'] = revision

        return response


