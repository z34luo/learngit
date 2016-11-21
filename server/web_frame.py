'''
Created on 2016年10月17日

@author: ux501
'''

import asyncio
import os
import logging

import functools
import inspect

from urllib import  parse
from aiohttp import web
from apis import APIError


import types




def get(path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args,**kw):
            return func(*args,**kw)
        wrapper.__method__='GET'
        wrapper.__path__=path
        return wrapper
    return decorator

def post(path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args,**kw):
            return func(*args,**kw)
        wrapper.__method__='POST'
        wrapper.__path__=path
        return wrapper
    return decorator

# ---------------------------- 使用inspect模块中的signature方法来获取函数的参数，实现一些复用功能-- 
# 关于inspect.Parameter 的  kind 类型有5种： 
# POSITIONAL_ONLY        只能是位置参数 
# POSITIONAL_OR_KEYWORD    可以是位置参数也可以是关键字参数 
# VAR_POSITIONAL            相当于是 *args 
# KEYWORD_ONLY            关键字参数且提供了key，相当于是 *,key 
# VAR_KEYWORD            相当于是 **kw 


def get_required_kw_args(fn):
    # 如果url处理函数需要传入命名关键字参数，且默认是空的话，在函数定义中没有默认值，获取这个key
    args=[]
    params=inspect.signature(fn).parameters
    for name, param in params.items():
        
        if param.kind==inspect.Parameter.KEYWORD_ONLY and param.default==inspect.Parameter.empty:
            args.append(name)
    return tuple(args)

def get_named_kw_args(fn):
    params=inspect.signature(fn).parameters
    args=[]
    for name,param in params.items():
        
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)

##判断是否有命名关键字参数
def has_named_kw_args(fn):
    params=inspect.signature(fn).parameters
    for name,param in params.items():
        
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True
      
##判断是否有关键字参数
def has_var_kw_arg(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True

#是否存在一个参数叫做request，并且该参数要在所有位置参数之后，即属于*kw或者**kw或者*或者*args之后的参数
def has_request_arg(fn):
    
    print('I am here has_request_arg',fn.__name__)
    params= inspect.signature(fn).parameters
    found=False
    
    for name, param in params.items():
        print(name)
        if name=='request':
            found=True
            continue 
        if found and (param.kind!= inspect.Parameter.VAR_POSITIONAL
                      and param.kind!= inspect.Parameter.KEYWORD_ONLY
                      and param.kind!=inspect.Parameter.VAR_KEYWORD):
            raise ValueError("request paramater must be the last named parameter in function:%s"%fn.__name__)
        
    return found
    

 #RequestHandler目的就是从URL函数中分析其需要接收的参数，从request中获取必要的参数， 

 # 调用URL函数，然后把结果转换为web.Response对象，这样，就完全符合aiohttp框架的要求： 
#把URL处理函数改造成self._func(**kw) 的形式， 提取request的参数


class RequestHandler(object):
    
    def __init__(self,app,fn):
        self._app=app
        self._func=fn
        self._has_request_arg = has_request_arg(fn) 
        self._has_var_kw_arg = has_var_kw_arg(fn) 
        self._has_named_kw_args = has_named_kw_args(fn) 
        self._named_kw_args = get_named_kw_args(fn) 
        self._required_kw_args = get_required_kw_args(fn) 

    @asyncio.coroutine
    
    def __call__(self,request):
        kw=None
        if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:
            
            if request.method == 'POST':
                
                if not request.content_type:
                    return web.HTTPBadRequest('Missing Content-type.')
                
                ct =request.content_type.lower()
                print('content_type %s' % ct)
                if ct.startswith('application/json'):
                    ##content_type 为json的话，说明消息主体是序列化后的json，所以要提取出来
                    params=yield from request.json()
                    if not isinstance(params, dict):
                        return web.HTTPBadRequest('JSON body must be object.')
                    
                    kw=params
                elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                    
                    
                    params=yield from request.post()
                    print(params)
                    
                    #dict(**kwargs) -> new dictionary initialized with the name=value pairs

                    #in the keyword argument list.  For example:  dict(one=1, two=2)
        
                    kw=dict(**params)
                else:
                    return web.HTTPBadRequest('Unsupported Content-Type:%s'%request.content_type)
            if request.method=='GET':
                qs = request.query_string
                print(qs)
                if qs:
                    kw=dict()
                    for k,v in parse.parse_qs(qs,True).items():
                        kw[k]=v[0]                  
        ##说明之前的request提取不了数据              
        if kw is None:
            kw=dict(**request.match_info)
                ##保存路由路径中的参数
        else:
            if not self._has_var_kw_arg and self._named_kw_args:
                ##没有关键字参数和 有命名关键字参数，检测request过来的命名参数与url处理函数的命名参数一致
                copy=dict()
                for name in self._named_kw_args:##所需的函数参数
                    if name in kw: ##在kw中选择所需的函数参数
                        copy[name]=kw[name]
                kw=copy
                
                    
            for k,v in request.match_info.items():
                if k in kw:
                    logging.warning('Duplicate arg name in named arg an dkw args:%s' %k)
                kw[k]=v
            
            
        if self._has_request_arg:
            kw['request']=request
            
        if self._required_kw_args:
   
            for name in self._required_kw_args:
                if name not in kw:
                    return web.HTTPBadRequest('Missing argument:%s'%name)
        
        print(request)
        #logging.INFO('call with args:%s'% str(kw))
        try:
            r=yield from self._func(**kw)
            return r
                ##  返回响应头
                
        except APIError as e:
            return dict(error=e.error,data=e.date,message=e.message)
                                
            
                

def add_static(app):
    path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'static')
    print(path)
    app.router.add_static('/static/',path)
    logging.info('add static %s => %s' % ('/static/', path))


        

def add_route(app,fn):
    
    
    method =getattr(fn,'__method__',None)
    path=getattr(fn,'__path__',None)
    
    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s'% str(fn))
    
    if not asyncio.iscoroutine(fn) or not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)
    logging.info('add route  %s %s => %s (%s)'%(method,path,fn.__name__,','.join(inspect.signature(fn).parameters.keys())))
    ##注册url处理函数，fn要先丢去request handler中进行api接口统一化
    app.router.add_route(method,path,RequestHandler(app,fn))
                
                
                
def add_routes(app,module_name):
    ## url函数都放在handlers.py这个文件中
    n= module_name.rfind('.')
    logging.info('in web_frame,lack of .py n=%s',n)
    
    if n==-1:
        mod=__import__(module_name,globals(),locals())

        logging.info('globals = %s',globals()['__name__'])
                
    else:
        mod=__import__(module_name[:n],globals(),locals())    
           
    for attr in dir(mod):
        
        if attr.startswith('_'):
            continue
        
        fn =getattr(mod,attr)
        if isinstance(fn,types.FunctionType):
            method =getattr(fn,'__method__',None)
            path=getattr(fn,'__path__',None)

            if method and path:
                add_route(app,fn)
                
                
                
        
        