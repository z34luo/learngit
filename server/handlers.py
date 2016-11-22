'''
Created on 2016年10月17日

@author: ux501
'''


import logging
logging.basicConfig(level=logging.DEBUG)
import json

from aiohttp import web
from  web_frame  import get,post
from apis import APIError,APIPermissionError,APIResourceNotFoundError,APIValueError
from models import  User 
import urllib

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
    r=web.Response()
    r.content_type='application/json'
    #r.body=dict()
    return r


@post('/login')
def api_authenticate(*,username,password):
    if not username:
        raise APIValueError('username','Invalid username')
    if not password:
        raise APIValueError('password','Invalid password')
    
    user=yield from User.findAll('username=?',username)
    if len(user)==0:
        raise APIValueError('username','Username not Found.')
    user=user[0]
    if  user.password!=password:
        raise APIValueError('password','Invalid password')
    r=web.Response()
    r.content_type='application/json'
    r.body=json.dumps(user,ensure_ascii=False).encode('utf-8')
    return r


@post('/register')
def api_register_authenticate(*,username,password):
    if not username:
        raise APIValueError('username','Invalid username')
    if not password:
        raise APIValueError('password','Invalid password')
#     users = yield from User.findAll('username=?', username)
#     if len(users)> 0:
#         raise APIError('register:failed', 'email', 'Email is already in use.')
    print(username)
    print(password)
    users = yield from User.findAll('username=?', username)
    if len(users)> 0:
        raise APIError('register:failed', 'username', 'Username is already in use.')
    user=User(username=username,password=password)
    yield from user.save()
    r=web.Response()
    r.content_type='application/json'
    r.body=json.dumps(user,ensure_ascii=False).encode('utf-8')
    return r