# Copyright 2012 django-compresshtml authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from functools import wraps
from compresshtml import compress_html

def compressed_response(f):
    @wraps(f)
    def compress(*args, **kwargs):
        response = f(*args, **kwargs)
        if response.status_code == 200 and 'text/html' in response['Content-Type']:
            response.content = compress_html(response.content)
        return response

    return compress