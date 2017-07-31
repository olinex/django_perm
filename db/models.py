#!/usr/bin/env python3
#-*- coding:utf-8 -*-

'''
Created on 2017年4月14日

@author: olin
'''

from django.db import models
from .manager import PermManager
from django.contrib.auth.models import AnonymousUser

class Model(models.Model):
    def su(self,user=AnonymousUser(),*,raise_error=False):
        '''
        return an instance of PermInstanceWrapper that can auto check 
        permission that user can read/write field
        @param user: an instance of django auth User
        @return: an instance of PermInstanceWrapper
        '''
        from .query import PermInstanceWrapper
        if user is not None:
            self._wrapper=PermInstanceWrapper(self,user,raise_error=raise_error)
        return self._wrapper
    
    @classmethod
    def is_field_name(cls,name):
        '''
        if name is one of Model's field name,then return True
        @param name:a string of field name
        @return: True/False 
        '''
        if name in [field.name for field in cls._meta.fields]:
            return True
        return False
    
    @classmethod
    def all_read_restrict_fields(cls):
        return [field for field in cls._meta.fields if hasattr(field,'has_read_perm')]
    
    @classmethod
    def all_write_restrict_fields(cls):
        return [field for field in cls._meta.fields if hasattr(field,'has_write_perm')]
    
    @classmethod
    def readable_fields_name(cls,user):
        return[field.name for field in cls._meta.fields if (not hasattr(field,'has_read_perm') or field.has_read_perm(user))]
        
    @classmethod
    def writeable_fields_name(cls,user):
        return[field.name for field in cls._meta.fields if (not hasattr(field,'has_write_perm') or field.has_write_perm(user))]
    
    @classmethod
    def sudo(cls,user,*,raise_error=False):
        '''
        init manager's model and user attribute
        @param user: an instance of django auth User
        @return : an instance of django orm manager that have the ability to set each instance's su method
        '''
        manager=PermManager(user,raise_error=raise_error)
        manager.model=cls
        return manager
    
    @classmethod
    def field_perm_register(cls):
        return (
            tuple(field.get_perm_tuple('read') for field in cls.all_read_restrict_fields())+
            tuple(field.get_perm_tuple('write') for field in cls.all_write_restrict_fields()))
    
    @classmethod
    def has_model_perm(cls,perm_type,user):
        if user.is_authenticated and (user.is_superuser or 
            user.has_perm('{}.{}_{}'.format(
            cls._meta.app_label,
            perm_type,
            cls._meta.object_name))):
            return True
        return False
        
    class Meta:
        abstract=True