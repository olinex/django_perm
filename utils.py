#!/usr/bin/env python3
#-*- coding:utf-8 -*-

'''
Created on 2017年4月23日

@author: olin
'''

from .models import PermInstance

set_perm=PermInstance.set_perm

def has_view_perm(request):
    '''
    check uesr's permission of view
    '''
    if request.user.has_perm(
        'djangoperm.{}_{}_{}'.format(
            request.method.upper(),
            request.resolver_match.app_name,
            request.resolver_match.url_name)):
        return True
    return False

def view_perm_required(func):
    '''
    a decorator that required user must have method permission
    '''
    def wrapper(*args,**kwargs):
        from django.http.request import HttpRequest
        from django.views.defaults import permission_denied
        first=args[0]
        if isinstance(first,HttpRequest):
            request=first
        else:
            request=args[1]
        if has_view_perm(request):
            return func(*args,**kwargs)
        return permission_denied(request,'permission denied')
    return wrapper

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