# -*- coding: UTF-8 -*-
"""
Url definitions.

Copyright (C) 2012 Corp B2C S.A.C.

Authors:
    Nicolas Valcarcel Scerpella <nvalcarcel@corpb2c.com>

"""
from django.conf import settings
from django.conf.urls import patterns, url


def build_app_urls(app, models):
    add_url = url(
        r'^(?P<app_url>%s)/(?P<model_url>%s)/add/$' % (
            app, '|'.join(models)),
        'add_or_modify',
        name='%s_add' % app
    )

    modify_url = url(
        r'^(?P<app_url>%s)/(?P<model_url>%s)/add/(?P<obj_id>\d+)/$' % (
            app, '|'.join(models)),
        'add_or_modify',
        name='%s_modify' % app
    )

    return add_url, modify_url

def build_urlpatterns():
    if hasattr(settings, 'DTRANS_CONF') and 'include' in settings.DTRANS_CONF:
        conf = settings.DTRANS_CONF

        regex_list = ['dtrans']
        for app, models in conf['include'].iteritems():
            add_url, modify_url = build_app_urls(app, models)

            regex_list += [add_url, modify_url]

        return patterns(*regex_list)

urlpatterns = build_urlpatterns()
