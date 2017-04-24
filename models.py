#!/usr/bin/env python3
#-*- coding:utf-8 -*-

'''
Created on 2017年4月23日

@author: olin
'''

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

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
        unique_together=('user','instanceId','instanceId')
        
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
    def set_perm(cls,codename,user,obj):
        '''
        create a permission about obj and user
        @param codename: a string about the permission
        @param user:an instance if User
        @param obj:an Model instance
        '''
        ct=ContentType.objects.get_for_model(obj)
        return cls.objects.get_or_create(
            codename=codename,
            user=user,
            contentType=ct,
            instanceId=obj.pk)