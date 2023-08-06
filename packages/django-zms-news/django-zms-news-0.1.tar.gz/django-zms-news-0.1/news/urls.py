# -*- coding: utf-8 -*-
from django.conf.urls import url, patterns

urlpatterns = patterns('',
        url(r'^$', 'news.views.list', name='new_list'),
        url(r'^(?P<id>\d+)-(?P<slug>([\w,-]+))/$', 'news.views.new_detail', name='new_detail'),
    )