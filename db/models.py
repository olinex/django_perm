#!/usr/bin/env python3
#-*- coding:utf-8 -*-

'''
Created on 2017年4月14日

@author: olin
'''

from .manager import PermManager

class PermModelMixin(object):
    def su(self,user=None):
        '''
        return an instance of PermInstanceWrapper that can auto check 
        permission that user can read/write field
        @param user: an instance of django auth User
        @return: an instance of PermInstanceWrapper
        '''
        from .query import PermInstanceWrapper
        if user is not None:
            self._wrapper=PermInstanceWrapper(self,user)
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
    def sudo(cls,user):
        '''
        init manager's model and user attribute
        @param user: an instance of django auth User
        @return : an instance of django orm manager that have the ability to set each instance's su method
        '''
        manager=PermManager(user)
        manager.model=cls
        return manager
    
    @classmethod
    def field_perm_register(cls):
        return (
            tuple(field.get_perm_tuple('read') for field in cls.all_read_restrict_fields())+
            tuple(field.get_perm_tuple('write') for field in cls.all_write_restrict_fields()))
            