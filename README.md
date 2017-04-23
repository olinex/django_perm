# djangoperm 1.0-dev
Django的权限库,可以通过继承或使用我们所提供的fields和manager控制实例的读写权限

## 简介
djangoperm库的目标是实现开箱即用的django权限库,可以同时控制视图级/模型级/对象级/字段级四个纬度的权限.
目前的1.0-dev版本仅实现了字段级的权限控制,且尚在进行测试.

## 依赖
djangoperm库是Python3的项目,Python2无法使用
djangoperm库是django的扩展库,依赖于django1.8版本以及其以上的版本,1.8之前的版本尚未经过测试,故无法保证能正常使用

## 使用

### 设置
要使用我们的djangoperm,必须将djangoperm库放置在PYTHONPATH或系统Path下,并在项目的settings.INSTALLED_APPS下注册djangoperm

### 重要的模块
* `djangoperm.db.models`
该库主要实现了一个`abstract Model`类,这个类封装了有关于所有权限的方法.当需要使用`djangoperm.db.fields`给自定义的数据表`Table`定义字段时,`Table`必须继承自`djangoperm.db.models`

* `djangoperm.db.fields`
该库覆盖了所有`django.db.fields`所定义的字段,我们可以通过定义字段的`perms`参数,限定字段的读写权限.如果你希望在我们的权限字段的基础上自定义自己的字段类,现阶段我们并不能做到.

### 定义权限字段
让我们首先看一下实例:
```Python
from djangoperm.db import fields
from djangoperm.db import models

class Test(models.Model):
	test_char=fields.CharField(
        'test_char',
        max_length=14,
        perms={'read':True,'write':True},
        help_text='a perm CharField')
```

你会发现,我们在实现类和方法尽量切合django,使得在使用djangoperm时尽可能少的修改原有的代码.
要使用权限字段,表模型必须继承自`djangoperm.db.models.Model`,`djangoperm.db.fields`覆盖了绝大部分的django内置字段(除了`IPAddressField`,因为这个字段已经被django所废弃),我们只需要像使用`django.db.fields`内的字段一样使用权限字段即可.
不同的是,我们可以设置响应的权限参数`perms`,这个参数的默认值为`{'read':False,'write':False}`,`read`和`write`分别对应着字段的读权限和写权限,他们的值可以为`True`,`False`和utf8字符串`'strict'`,当`read`值为`True`的时候,开启该字段的读权限控制,`False`为关闭,需要注意的是,超级管理员只有在`read`值为`'strict'`时,才会被纳入权限控制的范围内,同理`write`.

### 迁移
当我们定义好了权限字段以后,无论是否有修改原有字段类型或字段名,都需要进行迁移操作.需要注意的是,我们的字段权限控制是建立在django原有的Permission框架的基础之上的,因此想要真正实现不同权限的用户可以访问或修改不同的字段,必须为字段的读写权限分别在Permission内创建记录并将权限赋予用户方可生效.而创建权限记录这种工作繁琐而容易出错,因此最好使用我们所提供的manage扩展命令`permregister`自动执行这个操作

在project的根目录下执行:
```Bash
Python manage.py permregister <app> [<app2> <app3> ...]
```
app代表需要自动创建权限记录的应用.需要强调的是,由于考虑到外键约束问题,`permregister`并不会扫描字段权限的变动并删除已经'自认为是失效的'权限记录,这种工作程序无法代劳,虽然我们在不久的将来会尝试一种clear命令来帮助使用者清除失效的权限记录,但我们也仍需让使用者自行决定

### 在程序内控制权限
在程序内控制权限非常的简单,我们的权限控制使用了一种`代理模式`,这种代理更像是一种'君子协议',它不会影响你现有的任何代码,但却提供了一种捷径让你可以更加简单的控制你的字段的读写

* 在单个实例内使用:
```Python
user=User.objects.get(id=1)
demo=Test().objects.get(id=1)
wrapper=demo.su(user,raise_error=True)
```
所有继承自`djangoperm.db.models.Model`的类的实例都拥有`su`方法,这个方法需要一个必须的`user`参数(默认值为django的`AnonymousUser`),指明了需要鉴权的用户,一个可选的`raise_error`参数(默认为False,且必须以key-value形式传参),这个参数控制了用户无权设置权限字段时,是否抛出`PermissionError`,注意,即使`raise_error`为True,无权读取权限字段也不会报错.
`wrapper`便是我们的代理,通过代理可以访问或设置demo的属性和方法,但在使用者不可视的内部,我们进行了鉴权.需要注意的是,`wrapper`并不是模型实例.
```Python
>>> wrapper is demo
False
```

* 通过manage使用:
```Python
user=User.objects.get(id=1)
query=Test.sudo(user,raise_error=True).all()
```
所有继承自`djangoperm.db.models.Model`的类的实例都拥有`sudo`管理器,这个管理器重写了django的manager,并monkey-patch了django的Iterable,使得它返回的所有实例都自动获得了user(必须)和raise_error(可选)参数.不但如此,djangoperm还增加了values和values_list的权限过滤,你不需要再自己操心序列化的字段权限问题了

### 返回

* NotAllow
权限字段在进行未授权访问时,会返回`NotAllow`类的实例,这个类重写了所有的运算符重载方法,对它以及包含它的所有表达式求布尔值都将返回False,无论对它进行任何的数值运算,都将会返回其自身:
```Python
>>> test=Test()
>>> wrapper=test.su()
>>> value=wrapper.test_char
>>> value
<djangoperm.db.query.NotAllow object at 0x007291F0>
>>> -value
<djangoperm.db.query.NotAllow object at 0x007291F0>
>>> +value
<djangoperm.db.query.NotAllow object at 0x007291F0>
>>> 1+value > 0
False
>>> 0+value > 0
False
>>> 0+value-value > 0
False
>>> 0+value-value == 0
False
>>> 0+value-value < 0
False
```

# djangoperm 1.0-dev
A django project that can freely control view/model/instance/field permissions.
