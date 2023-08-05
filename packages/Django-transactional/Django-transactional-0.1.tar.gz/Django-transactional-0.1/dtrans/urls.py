# -*- coding: UTF-8 -*-
"""
Url definitions.

Copyright (C) 2012 Corp B2C S.A.C.

Authors:
    Nicolas Valcarcel Scerpella <nvalcarcel@corpb2c.com>

"""
from django.conf.urls import patterns, include, url

urlpatterns = patterns('dtrans',
    url(
        r'^(?P<app_name>\w+)/(?P<model_name>\w+)/add/$',
        'add_or_modify',
        name='add'
    ),
    url(
        r'^(?P<app_name>\w+)/(?P<model_name>\w+)/add/(?P<obj_id>\d+)/$',
        'add_or_modify',
        name='modify'
    ),
)
