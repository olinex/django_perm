#!/usr/bin/env python3
#-*- coding:utf-8 -*-

'''
Created on 2017年4月12日

@author: olin
'''

from django.db import models

class PermFieldMixin(object):

    def __init__(self,*args,perms={'read':False,'write':False},**kwargs):
        '''
        register the default field permissions to fields
        @param perms:a dict that contain both 'read' and 'write' attributes,which value must be the one of True/False/'strict'
        '''
        if len(perms) == 2:
            for key,value in perms.items():
                if key not in ('read','write'):
                    raise ValueError('permission type must be read or write')
                if value not in (True,False,'strict'):
                    raise ValueError("permission value must be True(enable)/False(disable)/'strict'")
        else:
            raise ValueError("perms attributes must contain both 'read' and 'write'")
        self.__perms=perms
        return getattr(models,self.__class__.__name__).__init__(self,*args,**kwargs)
    
    def get_perm_label(self,perm_type):
        '''
        return string of app label,model label and field name
        '''
        if perm_type in ('read','write'):
            return '{}.{}_{}_{}'.format(
                self.model._meta.app_label,
                perm_type,
                self.model._meta.object_name,
                self.name)
        raise ValueError("perm_type must be 'write' or 'read'")
    
    def get_perm_tuple(self,perm_type):
        '''
        return field's permission help text
        '''
        return (
            '{}_{}_{}'.format(
                perm_type,
                self.model._meta.object_name,
                self.name),
            'Can {} {} {} {}'.format(
                perm_type,
                self.model._meta.app_label,
                self.model._meta.object_name,
                self.name))
        
    def deconstruct(self):
        name,path,args,kwargs=getattr(models,self.__class__.__name__).deconstruct(self)
        kwargs['perms'] = self.__perms
        return name, path, args, kwargs
    
    def has_read_perm(self,user):
        if user.is_authenticated and (
            self.__perms['read'] is False
            or user.is_superuser
            or (self.__perms['read'] is not 'strict'
                and user.has_perm(self.get_perm_label('read')))):
            return True
        return False
    
    def has_write_perm(self,user):
        if user.is_authenticated and (
            self.__perms['write'] is False
            or user.is_superuser
            or (self.__perms['write'] is not 'strict'
                and user.has_perm(self.get_perm_label('write')))):
            return True
        return False

#   'Field','BigAutoField','BooleanField','CharField',
#    'CommaSeparatedIntegerField','DateField','DateTimeField',
#    'DecimalField','DurationField','EmailField','FilePathField',
#    'FloatField','IntegerField','BigIntegerField','IPAddressField',
#    'GenericIPAddressField','NullBooleanField','PositiveIntegerField',
#    'PositiveSmallIntegerField','SlugField','SmallIntegerField','TextField',
#    'TimeField','URLField','BinaryField','UUIDField'

class Field(PermFieldMixin,models.Field):
    pass

class AutoField(PermFieldMixin,models.AutoField):
    pass

class BigAutoField(PermFieldMixin,models.BigAutoField):
    pass

class BooleanField(PermFieldMixin,models.BooleanField):
    pass

class CharField(PermFieldMixin,models.CharField):
    pass

class CommaSeparatedIntegerField(PermFieldMixin,models.CommaSeparatedIntegerField):
    pass

class DateField(PermFieldMixin,models.DateField):
    pass

class DateTimeField(PermFieldMixin,models.DateTimeField):
    pass

class DecimalField(PermFieldMixin,models.DecimalField):
    pass

class DurationField(PermFieldMixin,models.DurationField):
    pass

class EmailField(PermFieldMixin,models.EmailField):
    pass

class FilePathField(PermFieldMixin,models.FilePathField):
    pass

class FloatField(PermFieldMixin,models.FloatField):
    pass

class IntegerField(PermFieldMixin,models.IntegerField):
    pass

class BigIntegerField(PermFieldMixin,models.BigIntegerField):
    pass

class GenericIPAddressField(PermFieldMixin,models.GenericIPAddressField):
    pass

class NullBooleanField(PermFieldMixin,models.NullBooleanField):
    pass

class PositiveIntegerField(PermFieldMixin,models.PositiveIntegerField):
    pass

class PositiveSmallIntegerField(PermFieldMixin,models.PositiveSmallIntegerField):
    pass

class SlugField(PermFieldMixin,models.SlugField):
    pass

class SmallIntegerField(PermFieldMixin,models.SmallIntegerField):
    pass

class TextField(PermFieldMixin,models.TextField):
    pass

class TimeField(PermFieldMixin,models.TimeField):
    pass

class URLField(PermFieldMixin,models.URLField):
    pass

class BinaryField(PermFieldMixin,models.BinaryField):
    pass

class UUIDField(PermFieldMixin,models.UUIDField):
    pass

ForeignKey = models.ForeignKey
OneToOneField = models.OneToOneField
ManyToManyField = models.ManyToManyField
