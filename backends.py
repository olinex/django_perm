#!/usr/bin/env python3
#-*- coding:utf-8 -*-

'''
Created on 2017年4月23日

@author: olin
'''

from .models import PermInstance

class ObjectPermissionBackend(object):
    '''
    A backend that can reset user's has_perm method
    '''
    def authenticate(self,username,password):
        return None
    
    def get_all_permissions(self, user_obj, obj=None):
        if not user_obj.is_active or not user_obj.is_authenticated:
            return set()
        if obj is not None:
            return PermInstance.get_all_codenames(user_obj,obj)
        else:
            if not hasattr(user_obj, '_perm_cache'):
                user_obj._perm_cache = self.get_user_permissions(user_obj)
                user_obj._perm_cache.update(
                    self.get_group_permissions(user_obj))
            return user_obj._perm_cache

    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_active:
            return False
        return perm in self.get_all_permissions(user_obj, obj)