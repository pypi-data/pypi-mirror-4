# -*- coding: utf-8 -*-
# Copyright 2012 django-compresshtml authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from django.conf import settings
import re

def compress_html(html_code):

    #remove white spaces between tags
    #use django force_text function to decode text
    html_code = re.sub(r'>\s+<', r'><', html_code)

    
    #keep comments or not
    keep_comments = getattr(settings, 'KEEP_COMMENTS_ON_COMPRESSING', False)    
    if not keep_comments:
        comments_regex = re.compile(r'<!--[^\[](.*?)-->', re.DOTALL)
        html_code = comments_regex.sub(r'', html_code) # .*? make it non greedy | won't remove downlevel-revealed or downlevel-hidden comments

    
    #remove white spaces between two matching tags (<h4> dfsd </h4>)
    html_code = re.sub(r'>\s+(.*?)\s+</', r'>\1</', html_code)

    return html_code
