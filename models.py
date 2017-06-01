#!/usr/bin/env python3
#-*- coding:utf-8 -*-

'''
Created on 2017年4月23日

@author: olin
'''
import uuid
from django.conf import settings
from datetime import timedelta
from djangoperm.db import fields
from djangoperm.db.models import Model
from django.db import models
from django.contrib.auth.models import User,Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Test(Model):
    '''
    test perm field
    '''
    test_big_auto=fields.BigAutoField(
        default=1,
        primary_key=True,perms={'read':True,'write':True})

    test_bool=fields.BooleanField(
        default=False,
        perms={'read':True,'write':True})

    test_date=fields.DateField(
        auto_now_add=True,
        perms={'read':True,'write':True})

    test_date_time=fields.DateTimeField(
        auto_now_add=True,
        perms={'read':True,'write':True})

    test_decimal=fields.DecimalField(
        default=0.00,
        decimal_places=2,
        max_digits=8,
        perms={'read':True,'write':True})

    test_duration=fields.DurationField(
        default=timedelta(microseconds=100),
        perms={'read':True,'write':True})

    test_email=fields.EmailField(
        default='test@test.com',
        perms={'read':True,'write':True})

    test_filepath=fields.FilePathField(
        default='',
        perms={'read':True,'write':True})

    test_float=fields.FloatField(
        default=0.0,
        perms={'read':True,'write':True})

    test_big_int=fields.BigIntegerField(
        default=0,
        perms={'read':True,'write':True})

    test_generic_ip=fields.GenericIPAddressField(
        default='192.168.1.1',
        perms={'read':True,'write':True})

    test_null_bool=fields.NullBooleanField(
        default=None,
        perms={'read':True,'write':True})

    test_pos_int=fields.PositiveIntegerField(
        default=1,
        perms={'read':True,'write':True})

    test_pos_small_int=fields.PositiveSmallIntegerField(
        default=2,
        perms={'read':True,'write':True})

    test_slug=fields.SlugField(
        default='',
        perms={'read':True,'write':True})

    test_small_int=fields.SmallIntegerField(
        default=3,
        perms={'read':True,'write':True})
    test_text=fields.TextField(
        default='test for text',
        perms={'read':True,'write':True})

    test_time=fields.TimeField(
        auto_now_add=True,
        perms={'read':True,'write':True})

    test_url=fields.URLField(
        default='www.google.com',
        perms={'read':True,'write':True})

    test_bin=fields.BinaryField(
        default=b'111',
        perms={'read':True,'write':True})
    test_uuid=fields.UUIDField(
        default=uuid.uuid4,
        perms={'read':True,'write':True})

    test_char=fields.CharField(
        'test_char',
        max_length=14,
        perms={'read':True,'write':True},
        help_text='a perm CharField')

    test_int=fields.IntegerField(
        'test_int',
        default=1,
        perms={'read':True,'write':True},
        help_text='a perm IntegerField')

    test_json_list=fields.JSONField(
        'test_json_list',
        json_type='list',
        default=[1,2,3,4],
        perms={'read':True,'write':True},
        help_text="json list"
    )

    test_json_dict=fields.JSONField(
        'test_json_dict',
        json_type='dict',
        perms={'read':True,'write':True},
        default={'read':True,'write':False},
        help_text="json dict"
    )

class PermInstance(models.Model):
    '''
    This table related the Model instance and user that can control user's 
    accessing of instance
    '''
    user=models.ForeignKey(
        User,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='access_instance',
        verbose_name='access user',
        help_text="user who can access the instance")
    
    codename=models.CharField(
        'code_name',
        max_length=94,
        null=False,
        blank=False,
        help_text="object permission's code name")
    
    contentType=models.ForeignKey(
        ContentType,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        verbose_name='model',
        help_text="instance's model")
    
    instanceId=models.PositiveIntegerField(
        'instance_id',
        null=False,
        blank=False,
        db_index=True,
        help_text="instance's id")
    
    createTime=models.DateTimeField(
        'create_time',
        auto_now_add=True,
        db_index=True)
    
    obj=GenericForeignKey('contentType','instanceId')
    
    class Meta:
        verbose_name='对象权限实例'
        verbose_name_plural='对象权限实例'
        unique_together=('user','codename','instanceId','contentType')
        
    @classmethod
    def get_all_codenames(cls,user,obj=None):
        '''
        when obj is a django Model,it will return all codenames about the user and Model
        when obj is a Model instance,it will return all codenames about the user and instance
        @param user:an instance of User
        @param obj:a Model or an instance
        @return: set of codenames
        '''
        option={'user':user}
        if isinstance(obj,models.Model):
            option['contentType']=ContentType.objects.get_for_model(obj)
            option['instanceId']=obj.pk
        elif type(models.Model) is type(obj):
            option['contentType']=ContentType.objects.get_for_model(obj)
        else:
            return set()
        return set(cls.objects.filter(**option).values_list('codename',flat=True))
        
    @classmethod
    def set_instance_perm(cls,codename,user,obj):
        '''
        create a permission about obj and user
        @param codename: a string about the permission
        @param user:an instance if User
        @param obj:an Model instance
        '''
        if user.is_authenticated:
            ct=ContentType.objects.get_for_model(obj)
            return cls.objects.get_or_create(
                codename=codename,
                user=user,
                contentType=ct,
                instanceId=obj.pk)
        return (None,False)

class View(models.Model):
    '''
    the model of every view
    '''
    app_label = fields.CharField(
        'app label',
        null=False,
        blank=False,
        max_length=30,
        help_text="view's app name"
    )

    name = fields.CharField(
        'view name',
        null=False,
        blank=False,
        max_length=30,
        help_text="view's name"
    )

    method = fields.CharField(
        'access method',
        null=False,
        blank=False,
        max_length=10,
        choices=((method,method.lower()) for method in settings.ALLOWED_METHODS),
        help_text="the method to access view",
    )

    permission = fields.ForeignKey(
        Permission,
        null=False,
        blank=False,
        verbose_name='about permission',
        help_text="The permission of the view"
    )

    class Meta:
        verbose_name='视图权限实例'
        verbose_name_plural='视图权限实例'
        unique_together=[
            ('app_label','method','name'),
        ]
