'''
Created on 2016年10月17日

@author: ux501
'''


import logging
logging.basicConfig(level=logging.DEBUG)
import json
import re
import time
import hashlib
import base64
import asyncio
from aiohttp import web
from  web_frame  import get,post
from apis import APIError,APIPermissionError,APIResourceNotFoundError,APIValueError
from models import  User,next_id 
from config import configs


_RE_SHA1=re.compile(r'^[0-9a-f]{40}$')
COOKIE_NAME='awesession'
_COOKIE_KEY=configs.session.secret



def user2cookie(user,max_age):
    expires=str(int(time.time()+max_age))
    
    s='%s-%s-%s-%s' %(user.id,user.password,expires,_COOKIE_KEY)
    L=[user.id,expires,hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)
##根据用户信息拼接一个cookie字符串



@asyncio.coroutine
def cookie2user(cookie_str):
    if not cookie_str:
        return None
    try:
        L=cookie_str.split('-')

        if len(L)!=3:
            return None
        uid,expires,sha1=L 
        if int(expires)<time.time():
            return None
        
        user=yield from User.find(uid)
        if user is None:
            return None
        
        s='%s-%s-%s-%s'%(uid,user.password,expires,_COOKIE_KEY)
        if sha1!=hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.password='******'
        return user
    except Exception as e :
        logging.exception(e)
        return None
        
        

@get('/')
def index(request):
    
    return {'__template__':'index.html'          
            }




## rest 访问 URL可以返回机器能直接解析的数据，可以看成是web api   API 把web app的功能全部封装了
##通过API 可以使服务器返回的不只是html页面

@get('/api/users')
def api_get_users(*,page='1'):
    
    return dict(page=1,users='ivy')

@get('/login')
def login(request):    
    return {'__template__':'login.html'          
            }

@get('/register')
def register(request):    
    return {'__template__':'register.html'          
            }    


# @get('/register')
# def api_register_user(*,email,name,passwd):
#     if not name or not name.strip():
#         raise APIValueError(name)
#     if not email or not name.strip():
#         raise APIValueError(name)
#     if not passwd or not name.strip():
#         raise APIValueError(name)
#     
#     users=yield from User.findAll('email=?',[email])
#     if len(users)>0:
#         raise APIError('register:failed','email','Email is already use.')
#    
#     user=User(id=uid,name=name=strip(),email=email,passwd=passwd)
#     yield from user.save()
#     r=web.Response()
#     r.content_type='application/json'
#     r.body=json.dumps(user.ensure_ascii=False).encode('utf-8')
#     return r

@get('/homepage')
def get_main_page(request):
    return {
        '__template__':'homepage.html'
        }


# @get('/register')
# def get_register_page(request):
#     return {   
#         '__template__':'register_page.html'
#         }
    
@get('/sidebar')
def get_sidebar_page(request):
    return{
        '__template__':'sidebar.html'
        
        }
    
    

    
    
@get('/index')
def get_facebook_page(request):
    REDIRECT_URL='http://localhost:9000/data_page'
    APP_ID='365868060416750'
#     ads_management,ads_read,manage_pages,pages_show_list,publish_pages,read_audience_network_insights,read_custom_friendlists,
    perms=['read_insights']
#     login_link='https://www.facebook.com/dialog/oauth?' + urllib.parse.urlencode({'client_id':APP_ID, 'redirect_uri':REDIRECT_URL, 'response_type': 'token', 'scope':'read_insights'})  
    login_link='https://www.facebook.com/dialog/oauth?' +'client_id='+APP_ID+'&redirect_uri='+REDIRECT_URL+'&response_type='+'token'+'&scope='+','.join(perms)  

    return {
        '__template__':'login_facebook.html',
        'login_link':login_link
        }
    

@get('/main_test')
def get_main_test_page(request):
    return{
        '__template__':'test.html'
        }
    
@get('/platformselection')
def get_platfrom_page(request):
    return{
        '__template__':'platformselection.html'
        }
    
@get('/xlsx')
def get_xlsx(request):   
    return{
        '__template__':'table.html'
        }
    
    
@get('/data_page')
def get_access_token(request):
    print(request)
    return{
        '__template__':'data_page.html'
        } 
    
@get('/test_excel')
def get_excel(request):
    return{
        '__template__':'testexcel.html'
        }

@get('/logout')
def api_logout(request):
    referer=request.headers.get('Referer')
    r=web.HTTPFound('/')
    r.set_cookie(COOKIE_NAME,'-deleted-',max_age=0,httponly=True)
    logging.info('user signed out')
    return r
    
@post('/api/access_token')
def post_access_token(*,access_token):
    print('access_token %s'%access_token[13:])
    global __access_token
    __access_token=access_token[13:]
    r=web.Response()
    r.content_type='application/json'
    r.body=json.dumps(access_token,ensure_ascii=False).encode('utf-8')
    return r

@post('/light_control')
def api_light_control(*,status):
    if not status:
        raise APIValueError('status','Invalid status')
    if(status=="open"):
        print("turn on the light")
    else:
        print("turn off the light")
    r=web.Response()
    r.content_type='application/json'
    r_body=dict()
    r.body=json.dumps(r_body,ensure_ascii=False).encode('utf-8')
    return r

@post('/lightness_control')
def api_lightness_control(*,status):
    if not status:
        raise APIValueError('status','Invalid status')
    if(status=="up"):
        print("turn on the light")
    else:
        print("turn off the light")
    r=web.Response()
    r.content_type='application/json'
    r_body=dict()
    r.body=json.dumps(r_body,ensure_ascii=False).encode('utf-8')
    return r

@post('/login')
def api_authenticate(*,username,password):
    if not username:
        raise APIValueError('username','Invalid username')
    if not password :
        raise APIValueError('password','Invalid password')
    
    user=yield from User.findAll('username=?',username)
    if len(user)==0:
        raise APIValueError('username','Username not Found.')
    
    
    user=user[0]
    sha1=hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(password.encode('utf-8'))
      
    if  user.password!=sha1.hexdigest():
        raise APIValueError('password','Invalid password')
    
    r=web.Response()
    r.content_type='application/json'
    r.set_cookie(COOKIE_NAME,user2cookie(user,86400),max_age=86400,httponly=True)
    user.password='******'
    
    
    r.body=json.dumps(user,ensure_ascii=False).encode('utf-8')
    return r


@post('/register')
def api_register_authenticate(*,username,password):
    if not username:
        raise APIValueError('username','Invalid username')
    if not password or not _RE_SHA1.match(password):
        raise APIValueError('password','Invalid password')
#     users = yield from User.findAll('username=?', username)
#     if len(users)> 0:
#         raise APIError('register:failed', 'email', 'Email is already in use.')

    users = yield from User.findAll('username=?', username)
    
    if len(users)> 0:
        raise APIError('register:failed', 'username', 'Username is already in use.')
    
    uid=next_id()
    sha1_passwd='%s:%s'%(uid,password)
    
    user=User(id=uid,username=username.strip(),password=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest())
    yield from user.save()
    r=web.Response()
    r.set_cookie(COOKIE_NAME,user2cookie(user,86400),max_age=86400,httponly=True)
    
    user.password='******'
    
    r.content_type='application/json'
    r.body=json.dumps(user,ensure_ascii=False).encode('utf-8')
    return r