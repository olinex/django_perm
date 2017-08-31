#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DjangopermConfig(AppConfig):
    name = 'apps.djangoperm'
    verbose_name = _('django permission config')
