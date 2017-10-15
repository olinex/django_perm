#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DjangoPermConfig(AppConfig):
    name = 'django_perm'
    verbose_name = _('django permission config')
