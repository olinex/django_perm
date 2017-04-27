#!/usr/bin/env python3
#-*- coding:utf-8 -*-

'''
Created on 2017年4月23日

@author: olin
'''

from .models import PermInstance

set_perm=PermInstance.set_perm

class view_perm_required(object):
    '''
    a decorator that required user must have method permission
    if strict is True,method must be one of the methods
    '''
    def __init__(self,*methods,strict=False):
        self.methods=methods
        self.strict=strict
        self.all_methods=(
            'GET','POST','HEAD',
            'PUT','DELETE','OPTIONS',
            'TRACE','PATCH')
        
    def __call__(self,func):
        self.func=func
        return self.__wrapper
    
    def __wrapper(self,*args,**kwargs):
        from django.http.request import HttpRequest
        from django.views.defaults import permission_denied
        allow_methods=[method.upper() for method in self.methods 
            if method.upper() in self.all_methods]
        first=args[0]
        if isinstance(first,HttpRequest):
            request=first
        else:
            request=args[1]
        if request.method in allow_methods:
            if request.user.has_perm(
                '{}.VIEW_{}_{}'.format(
                    request.resolver_match.app_name,
                    request.method,
                    self.func.__name__)):
                return self.func(*args,**kwargs)
        elif not self.strict:
            return self.func(*args,**kwargs)
        return permission_denied(request,'permission denied')
    
    def get_perm_tuple(self,app_label,method):
        '''
        return view's permission help text
        '''
        return (
            '{}.VIEW_{}_{}'.format(app_label,method,self.func.__name__),
            'Can {} {} view'.format(method,app_label,self.func.__name__))
    
    def view_perm_register(self,app_label):
        return tuple(self.get_perm_tuple(app_label,method) 
                     for method in self.all_methods)

# def method_view_perm_required(*methods,strict=False):
#     '''
#     a decorator that required user must have method permission
#     if strict is True,method must be one of the methods
#     '''
#     def wrapper(func):
#         def inner_wrapper(*args,**kwargs):
#             from django.http.request import HttpRequest
#             from django.views.defaults import permission_denied
#             all_methods=('GET','POST','HEAD','PUT','DELETE','OPTIONS','TRACE','PATCH')
#             allow_methods=[method.upper() for method in methods 
#                      if method.upper() in all_methods]
#             first=args[0]
#             if isinstance(first,HttpRequest):
#                 request=first
#             else:
#                 request=args[1]
#             if request.method in allow_methods:
#                 if request.user.has_perm(
#                     '{}.VIEW_{}_{}'.format(
#                         request.resolver_match.app_name,
#                         request.method,
#                         func.__name__)):
#                     return func(*args,**kwargs)
#             elif not strict:
#                 return func(*args,**kwargs)
#             return permission_denied(request,'permission denied')
#         return inner_wrapper
#     return wrapper