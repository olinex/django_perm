#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
Created on 2017年4月23日

@author: olin
'''

__all__ = ('set_instance_perm','clear_perm','has_view_perm','view_perm_required')

from .models import PermInstance
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.deconstruct import deconstructible
from django.urls import RegexURLPattern, RegexURLResolver

set_instance_perm = PermInstance.set_instance_perm
clear_perm = PermInstance.clear_perm


def has_view_perm(request):
    '''
    check uesr's permission of view
    '''
    if request.user.has_perm(
            'django_perm.{}_{}_{}'.format(
                request.method.upper(),
                request.resolver_match.app_name,
                request.resolver_match.url_name)):
        return True
    return False


def view_perm_required(func):
    '''
    a decorator that required user must have method permission
    '''

    def wrapper(*args, **kwargs):
        from django.http.request import HttpRequest
        from django.views.defaults import permission_denied
        first = args[0]
        if isinstance(first, HttpRequest):
            request = first
        else:
            request = args[1]
        if has_view_perm(request):
            return func(*args, **kwargs)
        return permission_denied(request, _('permission denied'))

    return wrapper

@deconstructible
class UserPermissionValidator(object):
    message = _('Ensure user %(user)s has permissions %(permissions)s')
    code = 'user_permission'

    def __init__(self,*permissions):
        self.permissions = set(permissions)

    def __call__(self, value):
        if not value.has_perms(self.permissions):
            raise ValidationError(
                self.message,
                code=self.code,
                params={'user': value, 'permissions': ','.join(self.permissions)}
            )

def url_recursive(urls):
    url_set = set()
    for url in urls.urlpatterns:
        if RegexURLPattern == type(url):
            if url.name:
                url_set.add(url.name)
            else:
                raise AttributeError(
                    "The url of {} must have name".format(url.callback.__name__)
                )
        elif RegexURLResolver == type(url):
            url_set |= url_recursive(url)
        else:
            raise TypeError(
                "unknown url {} contain in {}".format(
                    url.__name__,
                    urls.__name__
                )
            )
    return url_set

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
