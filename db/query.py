#!/usr/bin/env python3
#-*- coding:utf-8 -*-

'''
Created on 2017年4月16日

@author: olin
'''

from django.db import models

def NotAllowMethod(*args,**kwargs):
    '''
    A method that replace all model instance method that always return False
    '''
    return False

class NotAllow(object):
    '''
    when perm field was checked and not allow by user,the instance of the class will return
    '''
    def __init__(self,value,name,field):
        if isinstance(field,models.Field):
            self._value=value
            self._name=name
            self._field=field
        else:
            raise AttributeError('field must be an instance of django Field')
        
    def __eq__(self,other):
        return False
    
    __bool__ = __ge__ = __gt__ = __le__ = __lt__ = __ne__ = __eq__
    
    def __pos__(self):
        return self
    
    __neg__ = __abs__ = __pos__
    
    def __add__(self,other):
        return self
    
    __sub__ = __mul__ = __floordiv__ = __div__ = __mod__ = __divmod___ = __add__
    __mod__ = __divmod___ = __pow__ = __lshift__ = __rshift__ = __and__ = __or__ = __xor__ = __add__
    
    __rsub__ = __rmul__ = __rfloordiv__ = __rdiv__ = __rmod__ = __rdivmod___ = __rxor__= __radd__ = __add__
    __rmod__ = __rdivmod___ = __rpow__ = __rlshift__ = __rrshift__ = __rand__ = __ror__  = __add__
    
    def __str__(self):
        return 'NotAllow'
    
    def repr__(self):
        return 'NotAllow {}:{}'.format(self._name,self._value)
    
    def __sizeof__(self):
        return 0

class PermInstanceWrapper(object):
    '''
    a wrapper that contain model instance and user attrs that can check field permission
    when writting or reading permission restrict fields
    '''
    def __init__(self,instance,user,*,raise_error=False):
        self._instance=instance
        self._user=user
        self._raise_error=raise_error
        
    def __getattr__(self,name):
        inst=self.__getattribute__('_instance')
        user=self.__getattribute__('_user')
        value=getattr(inst,name)
        if inst.__class__.is_field_name(name):
            field=inst._meta.get_field(name)
            if not hasattr(field,'has_read_perm') or field.has_read_perm(user):
                return value
            return NotAllow(value,name,field)
        return value
    
    def __setattr__(self,name,value):
        if name in ('_instance','_user','_raise_error'):
            self.__dict__[name]=value
        else:
            inst=self.__dict__['_instance']
            user=self.__dict__['_user']
            if inst.__class__.is_field_name(name):
                field=inst._meta.get_field(name)
                if not hasattr(field,'has_write_perm') or field.has_write_perm(user):
                    setattr(inst,name,value)
                elif self.__dict__['_raise_error']:
                    raise PermissionError(
                        'No permission to set attribute {} of {}'.format(
                            name,inst._meta.object_name))
                return
            setattr(inst, name, value)
            
class PermBaseIterable(models.query.BaseIterable):
    def __init__(self,queryset,chunked_fetch=False,*,user,raise_error=False):
        super(PermBaseIterable,self).__init__(queryset,chunked_fetch=False)
        self._user=user
        self._raise_error=raise_error

class PermModelIterable(PermBaseIterable,models.query.ModelIterable):
    def __iter__(self):
        for obj in super(PermModelIterable,self).__iter__():
            obj.su(self._user,raise_error=self._raise_error)
            yield obj
            
class PermValuesIterable(PermBaseIterable,models.query.ValuesIterable):
    def __iter__(self):
        model=self.queryset.model
        readable_fields=model.readable_fields_name(self.queryset._user)
        for values in super(PermValuesIterable,self).__iter__():
            yield {
                k:(v if (k in readable_fields or not model.is_field_name(k)) else NotAllow(v,k,model._meta.get_field(k))) 
                for k,v in values.items()}
            
class PermValuesListIterable(PermBaseIterable,models.query.ValuesListIterable):
    def __iter__(self):
        queryset = self.queryset
        query = queryset.query
        compiler = query.get_compiler(queryset.db)
        model=self.queryset.model
        readable_fields=model.readable_fields_name(self.queryset._user)

#         if not query.extra_select and not query.annotation_select:
#             for row in compiler.results_iter():
#                 yield tuple(row)
#         else:
        field_names = list(query.values_select)
        extra_names = list(query.extra_select)
        annotation_names = list(query.annotation_select)

        # extra(select=...) cols are always at the start of the row.
        names = extra_names + field_names + annotation_names

        if queryset._fields:
            # Reorder according to fields.
            fields = list(queryset._fields) + [f for f in annotation_names if f not in queryset._fields]
        else:
            fields = names

        for row in compiler.results_iter():
            data = dict(zip(names, row))
            yield tuple(data[f] if (f in readable_fields or not model.is_field_name(f)) else NotAllow(data[f],f,model._meta.get_field(f)) for f in fields)
                
class PermFlatValuesListIterable(PermBaseIterable,models.query.FlatValuesListIterable):
    def __iter__(self):
        queryset=self.queryset
        name=queryset._fields[0]
        field=queryset.model._meta.get_field(name)
        if field.has_read_perm(queryset._user):
            for value in super(PermFlatValuesListIterable,self).__iter__():
                yield value
        else:
            for value in super(PermFlatValuesListIterable,self).__iter__():
                yield NotAllow(value,name,field)
            
class PermQuerySet(models.query.QuerySet):
    def __init__(self, model=None, query=None, using=None, hints=None,*,user,raise_error=False):
        '''
        must provide user value when QuerySet is initializing
        '''
        super(PermQuerySet,self).__init__(model,query,using,hints)
        self._user=user
        self._raise_error=raise_error
        self._iterable_class=PermModelIterable
        
    def _fetch_all(self):
        if self._result_cache is None:
            self._result_cache = list(
                self._iterable_class(
                    self,user=self._user,
                    raise_error=self._raise_error))
        if self._prefetch_related_lookups and not self._prefetch_done:
            self._prefetch_related_objects()
        
    def _clone(self, **kwargs):
        query = self.query.clone()
        if self._sticky_filter:
            query.filter_is_sticky = True
        clone = self.__class__(
            user=self._user,
            raise_error=self._raise_error,
            model=self.model, 
            query=query, 
            using=self._db, 
            hints=self._hints)
        clone._for_write = self._for_write
        clone._prefetch_related_lookups = self._prefetch_related_lookups
        clone._known_related_objects = self._known_related_objects
        clone._iterable_class = self._iterable_class
        clone._fields = self._fields

        clone.__dict__.update(kwargs)
        return clone
    
    def values(self,*fields,**expressions):
        clone=super(PermQuerySet,self).values(*fields,**expressions)
        clone._iterable_class = PermValuesIterable
        return clone
    
    def values_list(self,*fields,**kwargs):
        flat=kwargs.get('flat', False)
        clone=super(PermQuerySet,self).values_list(*fields,**kwargs)
        clone._iterable_class = PermFlatValuesListIterable if flat else PermValuesListIterable
        return clone