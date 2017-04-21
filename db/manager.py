#!/usr/bin/env python3
#-*- coding:utf-8 -*-

'''
Created on 2017年4月17日

@author: olin
'''
from .query import PermQuerySet
from django.db.models.manager import BaseManager

class PermBaseManager(BaseManager):
    def __init__(self,user):
        super(PermBaseManager,self).__init__()
        self._user=user
        
    def get_queryset(self):
        return self._queryset_class(
            user=self._user,
            model=self.model,
            using=self._db,
            hints=self._hints)

class PermManager(PermBaseManager.from_queryset(PermQuerySet)):
    pass
