# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from asv_media.settings import settings as AMS

URLS = {}

def lib_urls(request):
    if not URLS:
        for i in dir(AMS):
            if i.startswith('ASV_MEDIA'):
                URLS[i] = getattr(AMS, i)
    return URLS
