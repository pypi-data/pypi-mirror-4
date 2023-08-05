#!/usr/bin/python
# -*- coding: utf-8 -*-
from pybb_extensions.pluggable.views import AddPostView

try:
    from django.conf.urls import url, patterns
except ImportError:
    from django.conf.urls.defaults import url, patterns


urlpatterns = patterns('pybb_extensions.pluggable.views',
                       url('^(?P<plug_id>\d+)/post/dodaj/$', AddPostView.as_view(), name='add_post'),
                       )
