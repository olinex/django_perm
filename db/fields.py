#!/usr/bin/env python3
#-*- coding:utf-8 -*-

'''
Created on 2017年4月12日

@author: olin
'''

import json
from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ValidationError

def _perm_init(field,perms):
    '''
    register the default field permissions to fields
    @param perms:a dict that contain both 'read' and 'write' attributes,which value must be the one of True/False/'strict'
    '''
    if perms:
        if len(perms) == 2:
            for key,value in perms.items():
                if key not in ('read','write'):
                    raise ValueError('permission type must be read or write')
                if value not in (True,False,'strict'):
                    raise ValueError("permission value must be True(enable)/False(disable)/'strict'")
        else:
            raise ValueError("perms attributes must contain both 'read' and 'write'")
    field.perms=perms if perms else {'read':False,'write':False}

class PermFieldMixin(object):

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
        

    def has_read_perm(self,user):
        if user.is_authenticated and (
            self.perms['read'] is False
            or user.is_superuser
            or (self.perms['read'] is not 'strict'
                and user.has_perm(self.get_perm_label('read')))):
            return True
        return False
    
    def has_write_perm(self,user):
        if user.is_authenticated and (
            self.perms['write'] is False
            or user.is_superuser
            or (self.perms['write'] is not 'strict'
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

class Field(models.Field,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self,perms=perms)
        super(Field,self).__init__(*args,**kwargs)

    def deconstruct(self):
        name,path,args,kwargs=super(Field,self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class AutoField(models.AutoField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self,perms=perms)
        super(AutoField,self).__init__(*args,**kwargs)

    def deconstruct(self):
        name,path,args,kwargs=super(AutoField,self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class BigAutoField(models.BigAutoField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self,perms=perms)
        super(BigAutoField,self).__init__(*args,**kwargs)

    def deconstruct(self):
        name,path,args,kwargs=super(BigAutoField,self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class BooleanField(models.BooleanField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self,perms=perms)
        super(BooleanField,self).__init__(*args,**kwargs)

    def deconstruct(self):
        name,path,args,kwargs=super(BooleanField,self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class CharField(models.CharField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self,perms=perms)
        super(CharField,self).__init__(*args,**kwargs)

    def deconstruct(self):
        name,path,args,kwargs=super(CharField,self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class DateField(models.DateField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self, perms=perms)
        super(DateField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(DateField, self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class DateTimeField(models.DateTimeField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self, perms=perms)
        super(DateTimeField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(DateTimeField, self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class DecimalField(models.DecimalField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self, perms=perms)
        super(DecimalField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(DecimalField, self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class DurationField(models.DurationField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self, perms=perms)
        super(DurationField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(DurationField, self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class EmailField(models.EmailField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self, perms=perms)
        super(EmailField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(EmailField, self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class FilePathField(models.FilePathField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self, perms=perms)
        super(FilePathField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(FilePathField, self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class FloatField(models.FloatField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self, perms=perms)
        super(FloatField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(FloatField, self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class IntegerField(models.IntegerField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self, perms=perms)
        super(IntegerField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(IntegerField, self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class BigIntegerField(models.BigIntegerField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self, perms=perms)
        super(BigIntegerField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(BigIntegerField, self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class GenericIPAddressField(models.GenericIPAddressField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self, perms=perms)
        super(GenericIPAddressField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(GenericIPAddressField, self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class NullBooleanField(models.NullBooleanField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self, perms=perms)
        super(NullBooleanField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(NullBooleanField, self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class PositiveIntegerField(models.PositiveIntegerField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self, perms=perms)
        super(PositiveIntegerField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(PositiveIntegerField, self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class PositiveSmallIntegerField(models.PositiveSmallIntegerField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self, perms=perms)
        super(PositiveSmallIntegerField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(PositiveSmallIntegerField, self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class SlugField(models.SlugField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self, perms=perms)
        super(SlugField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(SlugField, self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class SmallIntegerField(models.SmallIntegerField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self, perms=perms)
        super(SmallIntegerField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(SmallIntegerField, self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class TextField(models.TextField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self, perms=perms)
        super(TextField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(TextField, self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class TimeField(models.TimeField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self, perms=perms)
        super(TimeField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(TimeField, self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class URLField(models.URLField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self, perms=perms)
        super(URLField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(URLField, self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class BinaryField(models.BinaryField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self, perms=perms)
        super(BinaryField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(BinaryField, self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class UUIDField(models.UUIDField,PermFieldMixin):
    def __init__(self,*args,perms=None,**kwargs):
        _perm_init(field=self, perms=perms)
        super(UUIDField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(UUIDField, self).deconstruct()
        kwargs['perms'] = self.perms
        return name, path, args, kwargs

class JSONField(TextField):

    def _json_serializer(self,value):
        if value is None:
            return value
        json_value=json.loads(value)
        if isinstance(json_value,eval(self.json_type)):
            return json_value
        raise ValidationError("value from database must be json string of {}".format(self.json_type))

    def __init__(self,*args,json_type='list',**kwargs):
        type_list=['list','dict']
        if json_type in type_list:
            self.json_type=json_type
            super(JSONField,self).__init__(*args,**kwargs)
        else:
            raise ValueError("json_type must be one of " + ','.join(type_list))

    def deconstruct(self):
        name,path,args,kwargs = super(JSONField,self).deconstruct()
        kwargs['json_type'] = self.json_type
        return name,path,args,kwargs

    def from_db_value(self,value,expression,connection,context):
        return self._json_serializer(value)

    def to_python(self, value):
        return self._json_serializer(value)

    def get_prep_value(self, value):
        if value is None or value == '':
            return value
        if isinstance(value,eval(self.json_type)):
            return json.dumps(value,cls=DjangoJSONEncoder)
        raise ValidationError("value from user must be {} type object".format(self.json_type))

ForeignKey = models.ForeignKey
OneToOneField = models.OneToOneField
ManyToManyField = models.ManyToManyField
