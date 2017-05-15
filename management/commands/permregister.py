#!/usr/bin/env python3
#-*- coding:utf-8 -*-

'''
Created on 2017年4月20日

@author: olin
'''

from django.urls import RegexURLPattern,RegexURLResolver
from django.core.management.base import BaseCommand, CommandError



def url_recursive(urls):
    url_set=set()
    for url in urls.urlpatterns:
        if RegexURLPattern == type(url):
            if url.name:
                url_set |= set((url.name,))
            else:
                raise CommandError(
                    "The url of {} must have name".format(url.callback.__name__)
                )
        elif RegexURLResolver == type(url):
            url_set |= url_recursive(url)
        else:
            raise CommandError(
                "unknown url {} contain in {}".format(
                    url.__name__,
                    urls.__name__
                )
            )
    return url_set

class Command(BaseCommand):
    '''write all field permissions into django Permission table'''
    
    def add_arguments(self, parser):
        parser.add_argument('app_names',nargs='+',type=str)
        
    def handle(self,*args,**options):
        import importlib
        from django.apps import apps
        from django.conf import settings
        from functools import reduce
        from django.db import transaction
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        from djangoperm.models import View
        error_apps=[app for app in options['app_names'] if app not in settings.INSTALLED_APPS]
        if error_apps:
            raise CommandError('Unknown apps:{}'.format(','.join(error_apps)))
        view_content=ContentType.objects.get_for_model(View)
        with transaction.atomic():
            for app_name in options['app_names']:
                app=importlib.import_module(app_name)
                for name in url_recursive(app.urls):
                    for method in settings.ALLOWED_METHODS:
                        perm=Permission.objects.get_or_create(
                            codename='{}_{}_{}'.format(method,app_name,name),
                            name='Can {} {} {}'.format(method,app_name,name),
                            content_type=view_content,
                        )
                        View.objects.get_or_create(
                            app_label=app_name,
                            name=name,
                            method=method,
                            permission=perm[0],
                        )
                models=[
                    model for model in apps.all_models[app_name].values()
                    if hasattr(model,'field_perm_register')
                ]
                for model in models:
                    for codename,name in model.field_perm_register():
                        model_content=ContentType.objects.get_for_model(model)
                        perm=Permission.objects.get_or_create(
                            codename=codename,
                            name=name,
                            content_type=model_content)
                        self.stdout.write(
                            self.style.SUCCESS('Successfully create permission {}'.format(perm)))

