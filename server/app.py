'''
Created on 2016年10月16日

@author: ux501
'''



import logging; 
logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time
from datetime import datetime

from aiohttp import web
from web_frame import add_routes, add_static

import orm
from config import configs
from jinja2 import Environment,FileSystemLoader
from handlers import cookie2user,COOKIE_NAME


def init_jinja2(app,**kw):
    logging.info('init jinja2...')
    options=dict(autoescape=kw.get('autoescape',True),
                 block_start_string=kw.get('block_start_string','{%'),
                 block_end_string=kw.get('block_end_starting','%}'),
                 variable_start_string=kw.get('variable_start_string','{{'),
                 variable_end_string=kw.get('variable_end_string','}}'),
                 auto_reload=kw.get('auto_reload',True)
                 )
                
    path=kw.get('path',None)
    if path is None:
         ##os.path.dirname(os.path.abspath(__file__)) 获取当前工作目录的地址
        path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'template')
    logging.info('set jinja2 template path:%s'%path)
    
    env=Environment(loader=FileSystemLoader(path),**options)
    
    filters=kw.get('filters',None)
    
    if filters is not None:
        for name,f in filters.items():
            env.filters[name]=f
            
    app['__templating__']=env
                    




@asyncio.coroutine
def logger_factory(app,handler):
    @asyncio.coroutine
    def logger(request):
        logging.info('Request:%s,%s'%(request.method,request.path))
        r=yield from handler(request)
        return r
    return logger

@asyncio.coroutine
def data_factory(app,handler):
    @asyncio.coroutine
    def parse_data(request):
        if request.method=="post":
            if request.content_type.startswith('application/json'):
                request.__data__=yield from request.json() ##json decoder
                logging.info('request json: %s '%str(request.__data__))
            elif request.content_type.startswith('application/x-www-form-urlencoded'): ## 窗体数据被编码为名称/值对
                request.__data__=yield from request.post() 
                logging.info('request json: %s '%str(request.__data__))
        return (yield from handler(request))
    return parse_data

@asyncio.coroutine
def auth_factory(app,handler):
    @asyncio.coroutine
    def auth(request):
        logging.info('check user:%s %s'%(request.method,request.path))
        request.__user__=None
        
        cookie_str=request.cookies.get(COOKIE_NAME)
        print(cookie_str)
        if cookie_str:
            user=yield from cookie2user(cookie_str)
            print(user)
            if user:
                logging.info('set current user:%s'% user.username)
                request.__user__=user
        if request.path.startswith('/homepage')and request.__user__ is None:
            return web.HTTPFound('/')
        return (yield from handler(request))
    return auth      
                
@asyncio.coroutine
def response_factory(app,handler):
    @asyncio.coroutine
    def response(request):
        logging.info('Response handler..')
        r= yield from handler(request)
        logging.info('r=%s '%str(r))
        print(r)
        
        if isinstance(r,web.StreamResponse):
            return r
        
        if isinstance(r,bytes):
            resp=web.Response(body=r)
            resp.content_type='application/octet-stream'
            return resp
        
        if isinstance(r,str):
            if r.startwith('redirect:'):
                return web.HTTPFound(r[9:])
            resp=web.Response(body=r.encode('utf-8'))
            resp.content_type='text/html;charst=utf-8'
            return resp
         
        if isinstance(r,dict):
            
            template=r.get('__template__')
            if template is None:
                
                resp = web.Response(body=json.dumps(
                    r,ensure_ascii=False,default=lambda o : o.__dict__).encode('utf-8'))
                resp.content_type='application/json;charst=utf-8'
                return resp
            else:
                ##r['__user__']=request.__user__
                resp=web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
                resp.content_type='text/html;charset=utf-8'
                return resp
            
        if isinstance(r, int) and r >= 100 and r < 600: 
            return web.Response(r) 
        # 如果响应结果为tuple且数量为2 
        if isinstance(r, tuple) and len(r) == 2: 
            t, m = r 
            # 如果tuple的第一个元素是int类型且在100到600之间，这里应该是认定为t为http状态码，m为错误描述 
            # 或者是服务端自己定义的错误码+描述 
            if isinstance(t, int) and t >= 100 and t < 600: 
                return web.Response(status=t, text=str(m)) 
            # default: 默认直接以字符串输出 
        resp = web.Response(body=str(r).encode('utf-8')) 
        resp.content_type = 'text/plain;charset=utf-8' 
        return resp 
    return response 


def datetime_filter(t):
    delta=int(time.time()-t)
    if delta<60:
        return '1分钟前'   
    if delta<3600:
        return '%s分钟前' % (delta//60)
    if delta<86400:
        return '%s小时前' % (delta//3600)
    if delta<604800:
        return '%s天前' % (delta//86400)
    dt=datetime.fromtimestamp()
    return '%s年%s月%s日'%(dt.year,dt.month,dt.day)

                
            

@asyncio.coroutine
def init(loop):
    yield from orm.create_pool(loop=loop,**configs.db)
    app=web.Application(loop=loop,middlewares=[logger_factory,auth_factory,response_factory])
    init_jinja2(app,filters=dict(datetime=datetime_filter))
    
    add_routes(app,'handlers')
    add_static(app)
    #127.0.0.1
    srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv
  
loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()