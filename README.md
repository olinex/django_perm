# djangoperm 1.0-dev
一个开箱即用的视图级/模型级/对象级/字段级的Django权限库

## 简介
djangoperm库的目标是实现开箱即用的django权限库,
可以同时控制视图级/模型级/对象级/字段级四个纬度的权限.
目前的1.0-dev版本已实现了四个维度的权限控制.

## 依赖
djangoperm库是Python3的项目,Python2无法使用
djangoperm库是django的扩展库,依赖于django1.8版本以及其以上的版本.
1.8之前的版本尚未经过测试,故无法保证能正常使用

## 重要的模块
### `djangoperm.db.models`
该模块主要实现了一个`abstract Model`类,这个类封装了有关于所有权限的方法.
当需要使用`djangoperm.db.fields`给自定义的数据表`Table`定义字段时,`Table`必须继承自`djangoperm.db.models`.
该模块引入了`djangoperm.db.fields`的命名空间,因此我们仅需要导入该模块即足够我们实现自己的模型.

### `djangoperm.db.fields`
该模块覆盖了绝大多数`django.db.fields`所定义的字段,我们可以通过定义字段的`perms`参数,限定字段的读写权限.
如果你希望在我们的权限字段的基础上自定义自己的字段类,现阶段我们并不能做到.
* 未覆盖的字段
    * `OneToOneField`
    * `ForeignKey`
    * `ManyToManyField`
    * `IPAddressField`

### `djangoperm.utils`
该模块提供了一个`set_instance_perm`函数,以及一个`@view_perm_required`装饰器,
前者可以设置对象级权限,后者可以装饰视图,控制用户对视图的访问.

## 设置
要使用我们的djangoperm,必须将djangoperm库放置在PYTHONPATH或系统Path下,
并在项目的settings.INSTALLED_APPS下注册djangoperm
```
INSTALLED_APPS = [
    ......

    'djangoperm',
]
```

## 使用

### 字段级权限
```Python
from djangoperm.db import models
from .models import Test
from django.contrib.auth.models import User

class Test(models.Model):
    test_char=models.CharField(
        'test_char',
        max_length=14,
        perms={'read':True,'write':True},
        help_text='a perm CharField')
```

你会发现,我们在实现类和方法尽量切合django,使得在使用djangoperm时尽可能少的修改原有的代码.
要使用权限字段,表模型必须继承自`djangoperm.db.models.Model`,
`djangoperm.db.fields`覆盖了绝大部分的django内置字段,我们只需要像使用`django.db.fields`内的字段一样使用权限字段即可.
不同的是,我们可以设置响应的权限参数`perms`,这个参数的默认值为`{'read':False,'write':False}`,
`read`和`write`分别对应着字段的读权限和写权限,他们的值可以为`True`,`False`和utf8字符串`'strict'`,
当`read`值为`True`的时候,开启该字段的读权限控制,`False`为关闭,
需要注意的是,超级管理员只有在`read`值为`'strict'`时,才会被纳入权限控制的范围内,同理`write`.

#### 迁移
当我们定义好了权限字段以后,无论是否有修改原有字段类型或字段名,都需要进行迁移操作.
需要注意的是,我们的字段权限控制是建立在django原有的Permission框架的基础之上的,
因此想要真正实现不同权限的用户可以访问或修改不同的字段,
必须为字段的读写权限分别在Permission内创建记录并将权限赋予用户方可生效.
而创建权限记录这种工作繁琐而容易出错,因此最好使用我们所提供的manage扩展命令`perm`自动执行这个操作

在project的根目录下执行:
```Bash
Python manage.py perm --field <app> [<app2> <app3> ...]
```
app代表需要自动创建权限记录的应用名.需要强调的是,由于考虑到外键约束问题,
`perm`并不会扫描字段权限的变动并删除已经'自认为是失效的'权限记录,这种工作程序无法代劳,
虽然我们在不久的将来会尝试一种clear命令来帮助使用者清除失效的权限记录,但我们也仍需让使用者自行决定

#### 在程序内控制字段权限
在程序内控制权限非常的简单,我们的权限控制使用了一种`代理模式`,
这种代理更像是一种'君子协议',它不会影响你现有的任何代码,
但却提供了一种捷径让你可以更加简单的控制你的字段的读写.

* 在单个实例内使用:
```Python
from .models import Test
from django.contrib.auth.models import User

user=User.objects.get(id=1)
demo=Test().objects.get(id=1)
wrapper=demo.su(user,raise_error=True)
```

所有继承自`djangoperm.db.models.Model`的类的实例都拥有`su`方法,
这个方法需要一个必须的`user`参数(默认值为django的`AnonymousUser`),
指明了需要鉴权的用户,一个可选的`raise_error`参数(默认为False,且必须以key-value形式传参),
这个参数控制了用户无权设置权限字段时,是否抛出`PermissionError`.
注意,即使`raise_error`为True,读取没有对应权限的字段也不会报错.
`wrapper`便是我们的代理,通过代理可以访问或设置demo的属性和方法,但在使用者不可视的内部,我们进行了鉴权.
需要注意的是,`wrapper`并不是模型实例.

```Python
>>> wrapper is demo
False
```

* 通过manage使用:
```Python
from .models import Test
from django.contrib.auth.models import User

user=User.objects.get(id=1)
query=Test.sudo(user,raise_error=True).all()
```
所有继承自`djangoperm.db.models.Model`的类的实例都拥有`sudo`管理器,
这个管理器重写了django的manager,并覆盖了django的Iterable,
使得它返回的所有实例都自动获得了user(必须)和raise_error(可选)参数.
不但如此,djangoperm还增加了values和values_list的权限过滤,
你不需要再自己操心序列化的字段权限问题了

#### 返回

* NotAllow
权限字段在进行未授权访问时,会返回`NotAllow`类的实例,这个类重写了所有的运算符重载方法,
对它以及包含它的所有表达式求布尔值都将返回False,无论对它进行任何的数值运算,都将会返回其自身:
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

### 对象级权限

#### 设置对象级权限
```Python
from djangoperm.utils import set_instance_perm
from .models import Test
from django.contrib.auth.models import User

user=User.objects.get(id=1)
demo=Test().objects.get(id=1)
set_instance_perm('delete',user,demo)
```

对象级权限是针对具体模型实例的权限,一般是指对应的数据表内的某一条具体的记录,
在具体实现上,我们创建了`PermInstance`模型,
通过`set_instance_perm('delete',user,demo)`将权限记录写入该模型,
指明某个user对demo对象拥有'delete'权限,
需要提醒的是,`'delete'`只是一个标识字符串,它可以是任意非空字符串.

#### 使用对象级权限
```Python
user.has_perm('delete',obj=demo)
```
通过user的has_perm方法我们可以判断用户是否拥有`'delete'`权限,需要注意的是,
我们只能判断user对demo是否拥有某个权限,但并不能控制user是否真的能删除demo,
这些操作都要由你自行决定

### 模型级权限

#### 设置模型级权限
django在创建model并迁移时,默认会向Permission数据表内写入model的`'add','change','delete'`
权限,对应model的增删改权限( 查权限较为复杂,django并没对此做出控制,而这就是我们现在正在做的 ).
django已经为我做了足够多,因此在绝大多数情况下,我们并不需要为模型级权限做更多的事情.
如果你需要自定义模型权限,我们建议通过models的Meta class配置:
```Python
from djangoperm.db import models

class Test(models.Model):
    ...

    class Meta:
        default_permissions=('add','change','delete','active')
```
`default_permissions是一个元组,前三者为django默认添加的增删改权限,
'active'则是我们希望添加的模型权限.

#### 控制模型级权限
```Python
from .models import Test
from django.contrib.auth.models import User

user=User.objects.get(id=1)
Test.has_model_perm('add',user)
```

### 视图级权限

#### 设置试图级权限
视图级权限是通过url路由与绑定实现自动设置的,一个视图可以有多个url,但一个url仅能有一个视图.
同时对视图的访问存在不同的请求方法,因此我们可以根据不同的请求方法进行鉴权.
我们只需要三步便能配置并使用视图级权限:
##### 第一步
在settings.py配置文件内,配置允许的全局请求方法:
```Python
ALLOWED_METHODS = ['GET','POST','HEAD','PUT','PATCH','OPTIONS','DELETE']
```
`ALLOW_METHODS`仅影响自动生成视图权限时所生成的权限实例以及被`@view_perm_required`
包装的视图

##### 第二步
为每个app下的url配置好`name`属性,并不需要过于紧张,只要你正常的进行django开发,
这一步操作事实上已经你已经做好
```Python
urlpatterns = [
    url(r'^$', your_view, name='first_request'),
]
```

##### 第三步
```Bash
Python manage.py perm --view <app> [<app2> <app3> ...]
```
通过我们提供的perm命令行,可以自动扫描指定的app下的urls模块,并自动注册视图权限

最后我们只需要使用装饰器`@view_perm_required`便可控制用户对视图的访问
```Python
from django.shortcuts import HttpResponse
from djangoperm.utils import view_perm_required

@view_perm_required
def your_view(request,*args,**kwargs):
    return HttpResponse('hello world')
```








