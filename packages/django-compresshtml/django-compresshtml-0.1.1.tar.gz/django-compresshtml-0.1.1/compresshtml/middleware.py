# Copyright 2012 django-compresshtml authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from compresshtml import compress_html
from django.conf import settings

class CompressHtmlMiddleware(object):

    def process_response(self, request, response):
        compress = getattr(settings, "COMPRESS_HTML", not settings.DEBUG)
        if compress:
            response.content = compress_html(response.content)
        return response
