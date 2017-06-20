
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoperm_test.settings")
django.setup()

import random
import string
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, Client
from .models import Test
from django.conf import settings
from djangoperm.db.query import NotAllow
from django.contrib.auth import get_user_model

User=get_user_model()

class ViewPermDecoratorCase(TestCase):

    def setUp(self):
        self.client=Client(enforce_csrf_checks=True)
        self.passwd=''.join(random.sample(string.ascii_letters,10))
        self.superuser=User.objects.create_superuser(
            username='testsuperuser',
            email='demosuperuser@163.com',
            password=self.passwd)
        self.normaluser=User.objects.create_user(
            username='testnormaluser',
            email='demouser@163.com',
            password=self.passwd)
        self.anonuser=AnonymousUser()

    def test_all_methods(self):
        methods=('GET','POST','HEAD','PUT','DELETE','OPTIONS','TRACE','PATCH')
        self.assertTrue(self.client.login(username='testsuperuser',password=self.passwd))
        self.assertEqual(self.client.get('/test',follow=True).status_code,200)
        self.assertEqual(self.client.post('/test',follow=True).status_code,200)
        self.assertEqual(self.client.head('/test',follow=True).status_code,200)
        self.assertEqual(self.client.put('/test',follow=True).status_code,200)
        self.assertEqual(self.client.delete('/test',follow=True).status_code,200)
        self.assertEqual(self.client.options('/test',follow=True).status_code,200)
        self.assertEqual(self.client.patch('/test',follow=True).status_code,200)
        self.assertTrue(self.client.login(username='testnormaluser',password=self.passwd))
        self.assertEqual(self.client.get('/test',follow=True).status_code,403)
        self.assertEqual(self.client.post('/test',follow=True).status_code,403)
        self.assertEqual(self.client.head('/test',follow=True).status_code,403)
        self.assertEqual(self.client.put('/test',follow=True).status_code,403)
        self.assertEqual(self.client.delete('/test',follow=True).status_code,403)
        self.assertEqual(self.client.options('/test',follow=True).status_code,403)
        self.assertEqual(self.client.patch('/test',follow=True).status_code,403)

class PermInstanceCase(TestCase):
    
    def setUp(self):
        from djangoperm.models import PermInstance
        self.demo=PermInstance
        self.superuser=User.objects.create_superuser(
            username='testsuperuser',
            email='demosuperuser@163.com',
            password=''.join(random.sample(string.ascii_letters,10)))
        self.normaluser=User.objects.create_user(
            username='testnormaluser',
            email='demouser@163.com',
            password=''.join(random.sample(string.ascii_letters,10)))
        self.anonuser=AnonymousUser()
        self.demo.set_instance_perm('test',self.superuser,self.superuser)
        self.demo.set_instance_perm('test',self.normaluser,self.normaluser)
        self.demo.set_instance_perm('test',self.anonuser,self.anonuser)
        self.demo.set_instance_perm('test1',self.superuser,self.superuser)
        self.demo.set_instance_perm('test1',self.normaluser,self.normaluser)
        self.demo.set_instance_perm('test1',self.anonuser,self.anonuser)
        self.demo.set_instance_perm('test2',self.superuser,self.superuser)
        self.demo.set_instance_perm('test2',self.normaluser,self.normaluser)
        self.demo.set_instance_perm('test2',self.anonuser,self.anonuser)
        
    def test_set_instance_perm(self):
        from djangoperm.utils import set_instance_perm
        for perm in ['test','test1','test2']:
            superuser_perm=set_instance_perm(perm,self.superuser,self.superuser)
            normaluser_perm=set_instance_perm(perm,self.normaluser,self.normaluser)
            anonuser_perm=set_instance_perm(perm,self.anonuser,self.anonuser)
            self.assertIsInstance(superuser_perm[0],self.demo)
            self.assertIsInstance(normaluser_perm[0],self.demo)
            self.assertIsNone(anonuser_perm[0])
            self.assertFalse(superuser_perm[1])
            self.assertFalse(normaluser_perm[1])
            self.assertFalse(anonuser_perm[1])
        
    def test_get_all_codenames(self):
        self.assertCountEqual(
            self.demo.get_all_codenames(self.superuser,self.superuser),
            {'test','test1','test2'})
        self.assertCountEqual(
            self.demo.get_all_codenames(self.normaluser,self.normaluser),
            {'test','test1','test2'})
        self.assertCountEqual(
            self.demo.get_all_codenames(self.anonuser,self.anonuser),
            set())
        
    def test_has_obj_perm(self):
        self.assertTrue(self.superuser.has_perm('test',obj=self.superuser))
        self.assertTrue(self.superuser.has_perm('test1',obj=self.superuser))
        self.assertTrue(self.superuser.has_perm('test2',obj=self.superuser))
        self.assertTrue(self.superuser.has_perm('test3',obj=self.superuser))
        self.assertTrue(self.normaluser.has_perm('test',obj=self.normaluser))
        self.assertTrue(self.normaluser.has_perm('test1',obj=self.normaluser))
        self.assertTrue(self.normaluser.has_perm('test2',obj=self.normaluser))
        self.assertFalse(self.normaluser.has_perm('test3',obj=self.normaluser))
        self.assertFalse(self.anonuser.has_perm('test',obj=self.anonuser))
        self.assertFalse(self.anonuser.has_perm('test1',obj=self.anonuser))
        self.assertFalse(self.anonuser.has_perm('test2',obj=self.anonuser))
        self.assertFalse(self.anonuser.has_perm('test3',obj=self.anonuser))

class FieldPermMethodCase(TestCase):
    
    def setUp(self):
        self.demo=Test.objects.create()
        self.superuser=User.objects.create_superuser(
            username='testsuperuser',
            email='demosuperuser@163.com',
            password=''.join(random.sample(string.ascii_letters,10)))
        self.normaluser=User.objects.create_user(
            username='testnormaluser',
            email='demouser@163.com',
            password=''.join(random.sample(string.ascii_letters,10)))
        self.anonuser=AnonymousUser()
        
    def tearDown(self):
        Test.objects.all().delete()
        
    def test_field_get_perm_label(self):
        '''all perm field can return perm label'''
        for field in self.demo._meta.fields:
            self.assertEqual(
                field.get_perm_label('write'),
                '{}.{}_{}_{}'.format(
                    Test._meta.app_label,
                    'write',
                    Test._meta.object_name,
                    field.name))
            self.assertEqual(
                field.get_perm_label('read'),
                '{}.{}_{}_{}'.format(
                    Test._meta.app_label,
                    'read',
                    Test._meta.object_name,
                    field.name))
            
    def test_get_perm_tuple(self):
        '''all perm field can return perm tuple'''
        for field in self.demo._meta.fields:
            self.assertEqual(
                field.get_perm_tuple('write'), 
                (
                '{}_{}_{}'.format(
                    'write',
                    Test._meta.object_name,
                    field.name),
                'Can {} {} {} {}'.format(
                    'write',
                    Test._meta.app_label,
                    Test._meta.object_name,
                    field.name)))
            
    def test_has_perm(self):
        for field in self.demo._meta.fields:
            field.perms['read']=False
            field.perms['write']=False
            self.assertTrue(
                field.has_read_perm(self.superuser))
            self.assertTrue(
                field.has_write_perm(self.superuser))
            self.assertTrue(
                field.has_read_perm(self.normaluser))
            self.assertTrue(
                field.has_write_perm(self.normaluser))
            self.assertFalse(
                field.has_read_perm(self.anonuser))
            self.assertFalse(
                field.has_write_perm(self.anonuser))
            
            field.perms['read']=True
            field.perms['write']=True
            self.assertTrue(
                field.has_read_perm(self.superuser))
            self.assertTrue(
                field.has_write_perm(self.superuser))
            self.assertFalse(
                field.has_read_perm(self.normaluser))
            self.assertFalse(
                field.has_write_perm(self.normaluser))
            self.assertFalse(
                field.has_read_perm(self.anonuser))
            self.assertFalse(
                field.has_write_perm(self.anonuser))
            
            field.perms['read']='strict'
            field.perms['write']='strict'
            self.assertTrue(
                field.has_read_perm(self.superuser))
            self.assertTrue(
                field.has_write_perm(self.superuser))
            self.assertFalse(
                field.has_read_perm(self.normaluser))
            self.assertFalse(
                field.has_write_perm(self.normaluser))
            self.assertFalse(
                field.has_read_perm(self.anonuser))
            self.assertFalse(
                field.has_write_perm(self.anonuser))
            
class ModelPermMethodCase(TestCase):
    
    def setUp(self):
        self.demo=Test
        self.instance=self.demo.objects.create()
        self.superuser=User.objects.create_superuser(
            username='testsuperuser',
            email='demosuperuser@163.com',
            password=''.join(random.sample(string.ascii_letters,10)))
        self.normaluser=User.objects.create_user(
            username='testnormaluser',
            email='demouser@163.com',
            password=''.join(random.sample(string.ascii_letters,10)))
        self.anonuser=AnonymousUser()
    
    def test_is_field_name(self):
        for field in self.demo._meta.fields:
            self.assertEqual(
                self.demo.is_field_name(field.name),
                True)
            
    def test_model_perm(self):
        for perm_type in ['create','update','delete']:
            self.assertTrue(self.demo.has_model_perm(perm_type,self.superuser))
            self.assertFalse(self.demo.has_model_perm(perm_type,self.normaluser))
            self.assertFalse(self.demo.has_model_perm(perm_type,self.anonuser))
            
class NotAllowCase(TestCase):
    
    def setUp(self):
        demo=Test.objects.create()
        self.na=demo.su().test_char
        
    def test_string(self):
        from django.conf import settings
        if not hasattr(settings, 'PERM_NOT_ALLOW_NOTICE'):
            self.assertEqual(str(self.na),'')
        else:
            self.assertEqual(str(self.na),settings.PERM_NOT_ALLOW_NOTICE)
        
        
    def test_all(self):
        self.assertFalse(self.na==self.na)
        self.assertFalse(self.na!=self.na)
        self.assertFalse(self.na>self.na)
        self.assertFalse(self.na<self.na)
        self.assertFalse(self.na>=self.na)
        self.assertFalse(self.na<=self.na)
        self.assertFalse(bool(self.na))
        self.assertFalse(False and self.na)
        self.assertFalse(False or self.na)
        self.assertIs(+self.na,self.na)
        self.assertIs(-self.na,self.na)
        self.assertIs(~self.na,self.na)
        self.assertIs(abs(self.na),self.na)
        self.assertIs(self.na+self.na,self.na)
        for i in range(-100,101):
            self.assertIs(i+self.na,self.na)
            self.assertIs(i-self.na,self.na)
            self.assertIs(i*self.na,self.na)
            self.assertIs(i/self.na,self.na)
            self.assertIs(i//self.na,self.na)
            self.assertIs(i**self.na,self.na)
            self.assertIs(self.na+i,self.na)
            self.assertIs(self.na-i,self.na)
            self.assertIs(self.na*i,self.na)
            self.assertIs(self.na/i,self.na)
            self.assertIs(self.na//i,self.na)
            self.assertIs(self.na**i,self.na)
            self.assertIs(i&self.na,self.na)
            self.assertIs(i^self.na,self.na)
            self.assertIs(i>>self.na,self.na)
            self.assertIs(i|self.na,self.na)
            self.assertIs(i<<self.na,self.na)
            self.assertIs(self.na&i,self.na)
            self.assertIs(self.na^i,self.na)
            self.assertIs(self.na|i,self.na)
            self.assertIs(self.na>>i,self.na)
            self.assertIs(self.na<<i,self.na)
        self.assertEqual(len(self.na),0)
        self.assertEqual(int(self.na),0)
        self.assertEqual(bin(self.na),bin(0))
        self.assertEqual(oct(self.na),oct(0))
        self.assertEqual(hex(self.na),hex(0))
        self.assertEqual(float(self.na),float(0))
        
class PermManagerCase(TestCase):
    
    def setUp(self):
        self.demo=Test
        self.instance=self.demo.objects.create()
        self.superuser=User.objects.create_superuser(
            username='testsuperuser',
            email='demosuperuser@163.com',
            password=''.join(random.sample(string.ascii_letters,10)))
        self.normaluser=User.objects.create_user(
            username='testnormaluser',
            email='demouser@163.com',
            password=''.join(random.sample(string.ascii_letters,10)))
        self.anonuser=AnonymousUser()
        
    def test_su(self):
        wrapper=self.instance.su(self.superuser,raise_error=False)
        for field in self.demo._meta.fields:
            self.assertIs(
                getattr(wrapper,field.name),
                getattr(self.instance,field.name))
            
        wrapper=self.instance.su(self.superuser,raise_error=True)
        for field in self.demo._meta.fields:
            self.assertIs(
                getattr(wrapper,field.name),
                getattr(self.instance,field.name))
            
        wrapper=self.instance.su(self.normaluser,raise_error=False)
        for field in self.demo._meta.fields:
            self.assertIsInstance(
                getattr(wrapper,field.name),
                NotAllow)
            
        wrapper=self.instance.su(self.normaluser,raise_error=True)
        for field in self.demo._meta.fields:
            self.assertIsInstance(
                getattr(wrapper,field.name),
                NotAllow)
            
        wrapper=self.instance.su(self.anonuser,raise_error=False)
        for field in self.demo._meta.fields:
            self.assertIsInstance(
                getattr(wrapper,field.name),
                NotAllow)
            
        wrapper=self.instance.su(self.anonuser,raise_error=True)
        for field in self.demo._meta.fields:
            self.assertIsInstance(
                getattr(wrapper,field.name),
                NotAllow)
        
    def test_values(self):
        values=self.demo.sudo(self.superuser).values()
        for item in list(values):
            for k,v in item.items():
                self.assertEqual(getattr(self.instance,k),v)
        values=self.demo.sudo(self.anonuser).values()
        for item in list(values):
            for k,v in item.items():
                self.assertIsInstance(v,NotAllow)