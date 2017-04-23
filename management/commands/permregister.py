#!/usr/bin/env python3
#-*- coding:utf-8 -*-

'''
Created on 2017年4月20日

@author: olin
'''

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help='write all field permissions into django Permission table'
    
    def add_arguments(self, parser):
        parser.add_argument('app_names',nargs='+',type=str)
        
    def handle(self,*args,**options):
        from django.apps import apps
        from django.conf import settings
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        error_apps=[app for app in options['app_names'] if app not in settings.INSTALLED_APPS]
        if error_apps:
            raise CommandError('Unknown apps:{}'.format(','.join(error_apps)))
        for app_name in options['app_names']:
            for model in apps.all_models[app_name].values():
                for codename,name in model.field_perm_register():
                    model_content=ContentType.objects.get_for_model(model)
                    perm=Permission.objects.get_or_create(
                        codename=codename,
                        name=name,
                        content_type=model_content)
                    self.stdout.write(
                        self.style.SUCCESS('Successfully create permission {}'.format(perm)))
