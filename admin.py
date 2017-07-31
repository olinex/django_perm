#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from django.contrib import admin

from . import models


@admin.register(models.PermInstance)
class PermInstanceAdmin(admin.ModelAdmin):
    list_display = ('id','codename','user','obj','createTime')
    list_filter = ('createTime',)
    search_fields = ('codename',)
    list_editable = ('codename',)
    fieldsets = (
        (None,{'fields':(
            'codename',
            'user',
            ('contentType','instanceId')
        )}),
    )

@admin.register(models.View)
class ViewAdmin(admin.ModelAdmin):
    list_display = ('id','app_label','name','method','permission')
    list_filter = ('app_label','method')
    search_fields = ('app_label','name')
    list_editable = ('app_label','name','method')
    fieldsets = (
        (None,{'fields':(
            'app_label',
            'name',
            'method',
        )}),
    )


