#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
Created on 2017年4月23日

@author: olin
'''
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import Permission
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import PROTECT,CASCADE,SET_NULL,SET,SET_DEFAULT,DO_NOTHING
from apps.djangoperm.db.models import Model
from apps.djangoperm.db.fields import *


class Test(Model):
    '''
    test perm field
    '''
    test_big_auto = BigAutoField(
        default=1,
        primary_key=True, perms={'read': True, 'write': True})

    test_bool = BooleanField(
        default=False,
        perms={'read': True, 'write': True})

    test_date = DateField(
        auto_now_add=True,
        perms={'read': True, 'write': True})

    test_date_time = DateTimeField(
        auto_now_add=True,
        perms={'read': True, 'write': True})

    test_decimal = DecimalField(
        default=0.00,
        decimal_places=2,
        max_digits=8,
        perms={'read': True, 'write': True})

    test_duration = DurationField(
        default=timedelta(microseconds=100),
        perms={'read': True, 'write': True})

    test_email = EmailField(
        default='test@test.com',
        perms={'read': True, 'write': True})

    test_filepath = FilePathField(
        default='',
        perms={'read': True, 'write': True})

    test_float = FloatField(
        default=0.0,
        perms={'read': True, 'write': True})

    test_big_int = BigIntegerField(
        default=0,
        perms={'read': True, 'write': True})

    test_generic_ip = GenericIPAddressField(
        default='192.168.1.1',
        perms={'read': True, 'write': True})

    test_null_bool = NullBooleanField(
        default=None,
        perms={'read': True, 'write': True})

    test_pos_int = PositiveIntegerField(
        default=1,
        perms={'read': True, 'write': True})

    test_pos_small_int = PositiveSmallIntegerField(
        default=2,
        perms={'read': True, 'write': True})

    test_slug = SlugField(
        default='',
        perms={'read': True, 'write': True})

    test_small_int = SmallIntegerField(
        default=3,
        perms={'read': True, 'write': True})
    test_text = TextField(
        default='test for text',
        perms={'read': True, 'write': True})

    test_time = TimeField(
        auto_now_add=True,
        perms={'read': True, 'write': True})

    test_url = URLField(
        default='www.google.com',
        perms={'read': True, 'write': True})

    test_bin = BinaryField(
        default=b'111',
        perms={'read': True, 'write': True})
    test_uuid = UUIDField(
        default=uuid.uuid4,
        perms={'read': True, 'write': True})

    test_char = CharField(
        'test_char',
        max_length=14,
        perms={'read': True, 'write': True},
        help_text='a perm CharField')

    test_int = IntegerField(
        'test_int',
        default=1,
        perms={'read': True, 'write': True},
        help_text='a perm IntegerField')

    test_json_list = JSONField(
        'test_json_list',
        json_type='list',
        default=[1, 2, 3, 4],
        perms={'read': True, 'write': True},
        help_text="json list"
    )

    test_json_dict = JSONField(
        'test_json_dict',
        json_type='dict',
        perms={'read': True, 'write': True},
        default={'read': True, 'write': False},
        help_text="json dict"
    )


class PermInstance(models.Model):
    '''
    This table related the Model instance and user that can control user's 
    accessing of instance
    '''
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name=_('access user'),
        help_text=_('user who can access the instance'))

    codename = models.CharField(
        _('code name'),
        max_length=94,
        null=False,
        blank=False,
        help_text=_("object permission's code name"))

    content_type = models.ForeignKey(
        ContentType,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        verbose_name=_('model'),
        help_text=_("instance's model"))

    instance_id = models.PositiveIntegerField(
        _('instance id'),
        null=False,
        blank=False,
        db_index=True,
        help_text=_("instance's id"))

    create_time = models.DateTimeField(
        _('create time'),
        auto_now_add=True,
        db_index=True)

    obj = GenericForeignKey('content_type', 'instance_id')

    class Meta:
        verbose_name = _('object permission instance')
        verbose_name_plural = _('object permission instances')
        unique_together = ('user', 'codename', 'instance_id', 'content_type')

    @classmethod
    def get_all_codenames(cls, user, obj=None):
        '''
        when obj is a django Model,it will return all codenames about the user and Model
        when obj is a Model instance,it will return all codenames about the user and instance
        @param user:an instance of User
        @param obj:a Model or an instance
        @return: set of codenames
        '''
        option = {'user': user}
        if isinstance(obj, models.Model):
            option['content_type'] = ContentType.objects.get_for_model(obj)
            option['instance_id'] = obj.pk
        elif type(models.Model) is type(obj):
            option['content_type'] = ContentType.objects.get_for_model(obj)
        else:
            return set()
        return set(cls.objects.filter(**option).values_list('codename', flat=True))

    @classmethod
    def set_instance_perm(cls, codename, user, obj):
        '''
        create a permission about obj and user
        @param codename: a string about the permission
        @param user:an instance if User
        @param obj:an Model instance
        '''
        if user.is_authenticated:
            ct = ContentType.objects.get_for_model(obj)
            return cls.objects.get_or_create(
                codename=codename,
                user=user,
                content_type=ct,
                instance_id=obj.pk)
        return (None, False)

    @classmethod
    def clear_perm(cls, user=None, obj=None, codename=None):
        '''
        clear all permissions which select out by user and obj
        :param user: None or instance of User
        :param obj: None or instance of Model
        :return: None
        '''
        from django.db.models import Q
        if user or obj or codename:
            query = Q()
            if user:
                query &= Q(user=user)
            if obj:
                ct = ContentType.objects.get_for_mode(obj)
                query &= Q(content_type=ct) & Q(instance_id=obj.pk)
            if codename:
                query &= Q(codename=codename)
            cls.objects.filter(query).delete()

class View(models.Model):
    '''
    the model of every view
    '''
    app_label = models.CharField(
        _('app label'),
        null=False,
        blank=False,
        max_length=30,
        help_text=_("view's app name")
    )

    name = models.CharField(
        _('view name'),
        null=False,
        blank=False,
        max_length=30,
        help_text=_("view's name")
    )

    method = models.CharField(
        _('access method'),
        null=False,
        blank=False,
        max_length=10,
        choices=((method, method.lower()) for method in settings.ALLOWED_METHODS),
        help_text=_("the method to access view"),
    )

    permission = models.ForeignKey(
        Permission,
        null=False,
        blank=False,
        verbose_name=_('about permission'),
        help_text=_("The permission of the view")
    )

    class Meta:
        verbose_name = _('view permission')
        verbose_name_plural = _('view permissions')
        unique_together = [
            ('app_label', 'method', 'name'),
        ]
