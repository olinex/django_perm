#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from .views import test_view
from django.conf.urls import url

urlpatterns = [
    url(r'^$',test_view),
]