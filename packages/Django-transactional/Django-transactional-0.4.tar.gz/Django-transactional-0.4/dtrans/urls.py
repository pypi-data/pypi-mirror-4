# -*- coding: UTF-8 -*-
"""
Url definitions.

Copyright (C) 2012 Corp B2C S.A.C.

Authors:
    Nicolas Valcarcel Scerpella <nvalcarcel@corpb2c.com>

"""
from django.conf import settings
from django.conf.urls import patterns, url

regex = {
    'app': '\w+',
    'model': '\w+'
}

if hasattr(settings, 'DTRANS_CONF'):
    conf = settings.DTRANS_CONF

    if ('force_urls' in conf) and conf['force_urls']:
        for kind in ['app', 'model']:
            key = '%ss_urls' % kind

            if key in conf:
                regex[kind] = '%s' % '|'.join(conf[key].keys())

urlpatterns = patterns('dtrans',
    url(
        r'^(?P<app_url>%s)/(?P<model_url>%s)/add/$' % (
            regex['app'], regex['model']),
        'add_or_modify',
        name='add'
    ),
    url(
        r'^(?P<app_url>%s)/(?P<model_url>%s)/add/(?P<obj_id>\d+)/$' % (
            regex['app'], regex['model']),
        'add_or_modify',
        name='modify'
    ),
)
