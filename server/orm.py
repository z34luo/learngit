'''
Created on 2016年10月16日

@author: ux501
'''

import logging;
logging.basicConfig(level=logging.INFO)

import asyncio,os,json,time,aiomysql

from builtins import isinstance

def log(sql,args=()):
    logging.info('SQL:%s'%sql)
    

@asyncio.coroutine
def create_pool(loop,**kw):
    
    logging.info('create database connection pool...')
    
    global __pool
    
    __pool=yield from aiomysql.create_pool(
        host=kw.get('host','localhost'),  ##使,用get设置默认值
        port=kw.get('port',3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['database'],
        charset=kw.get('charset','utf8'),
        autocommit=kw.get('autocommit',True),
        maxsize=kw.get('maxsize',10),
        minsize=kw.get('minsize',1),
        loop=loop
        )
    
    

@asyncio.coroutine
def destory_pool():
    global __pool
    if __pool is not None :
        __pool.close()
        yield from __pool.wait_closed()


@asyncio.coroutine
def select(sql,args,size=None):
    
    log(sql,args)
    global __pool
    with (yield from __pool) as conn:
        cur = yield from conn.cursor(aiomysql.DictCursor)
        print(sql)
        yield from cur.execute(sql.replace('?','%s'),args)
        if size:
            rs=yield from cur.fetchmany(size)
        else:
            rs=yield from cur.fetchall()
        yield from cur.close()
        logging.info('rows returned %s'% len(rs))

    return rs

  
@asyncio.coroutine
def execute(sql,args,autocommit=True):
    log(sql,args)
    
    global __pool
    
    with (yield from __pool) as conn:
        
        cur =yield from conn.cursor(aiomysql.DictCursor)
        print(sql)
        try:
            yield from cur.execute(sql.replace('?','%s'),args ) #args 是list 切记
            affected=cur.rowcount
            if not autocommit:
                yield from cur.commit()
            yield from cur.close()
        except BaseException as e:
            if not autocommit:
                yield from conn.rollback()
            raise e 
        return affected
    
#********************************************
class ModelMetaclass(type):

    def __new__(cls,name,bases,attrs):  #创建类的对象 user，类的名字User(表名)，类继承的父类集合，类的方法集合
        
        if(name=='Model'):
            return type.__new__(cls,name,bases,attrs)
        
        
        tableName=attrs.get('__table__',None)or name
        logging.info('found model:%s (tables):%s' % (name,tableName))
        
        #获取所有的列和主键
        mappings=dict()
        primaryKey=None
        fields=[]
        for k,v in attrs.items():
            if isinstance(v, Field):
                print('Found Mapping %s==>%s'%(k,v))
                mappings[k]=v
                print(v.primary_key)
                if v.primary_key:
                    if primaryKey:
                        raise RuntimeError("Duplicate primary Key Error $s"%k)
                    primaryKey=k
                else:
                    fields.append(k)   ##L列的名字集合
        
        if not primaryKey:
            raise RuntimeError("Primary key is not known")
        for k in mappings.keys():
            attrs.pop(k)
            
        escaped_fields=list(map(lambda x: str(x),fields))
        attrs['__mapping__']=mappings
        attrs['__table__']=tableName
        attrs['__primary_key__']=primaryKey
        attrs['__fields__']=fields
        attrs['__select__']='select `%s`,%s from `%s`'%(primaryKey,','.join(escaped_fields),tableName)
        attrs['__insert__']='insert into `%s` (%s,`%s`) values(%s)' % (tableName,','.join(escaped_fields),primaryKey,create_args_string(len(escaped_fields)+1))
        attrs['__update__']='update `%s` set %s where `%s`=?'%(tableName,','.join(map(lambda f:'`%s`=?'%(mappings.get(f).name or f),fields)),primaryKey)
        attrs['__delete__']='delete from `%s` where `%s`=?'%(tableName,primaryKey)

        return type.__new__(cls,name,bases,attrs)
    
def create_args_string(size):
    return('?,'*size)[:-1] #不是返回tuple 返回字符串  去倒数第一个字符串之前











class Model(dict,metaclass=ModelMetaclass):
    
    def __init__(self,**kw):
        super(Model,self).__init__(**kw)
        
    def __getattr__(self,key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)
    
    def __setattr__(self, key, value):
        
        self[key]=value
        
    def getValue(self,key):
        return getattr(self,key,None)  ##
    
    def getValueOrDefault(self,key):
        value=getattr(self,key,None)
        if value is None:
            field=self.__mappings__[key]
            
            if field.default is not None:
                value=field.default() if callable(field.default) else field.default  ## 查询该列是否存在默认值
                logging.debug('using default value for %s: %s'% (key,str(value)))
                setattr(self,key,value)
        return value


    @classmethod 
    @asyncio.coroutine
    def find(cls,pk):
        rs= yield from select('%s where %s=?'%(cls.__select__,cls.__primary_Key__),[pk],1)
        if len(rs)==0:
            return None
        return cls(**rs[0])  ##由于只返回一行，所以取[0]
    
    
    @classmethod
    @asyncio.coroutine
    def findAll(cls,where=None,args=None,**kw):
        sql=[cls.__select__]
        
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args=[]
        orderBy=kw.get('orderBy',None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        
        limit = kw.get('limit',None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit,int):
                sql.append('?')
                args.append(limit)
            if isinstance(limit,tuple):
                sql.append('?,?')
                args.extend(limit)
                ##list拓展用extend　并且接受tuple的数据
            else:
                raise ValueError('Invalid limit value %s'%str(limit))
   
        rs= yield from select(' '.join(sql),args)
        return [cls(**r) for r in rs]
    
    
#     @classmethod
#     @asyncio.coroutine
#     def insertone(cls,**kw):
#         sql=[cls.__insert__]
    ##>>> nums = [1, 2, 3]
    ##   >>> calc(*nums)
    ##    14
    
    ##>>> extra = {'city': 'Beijing', 'job': 'Engineer'}
    ##    >>> person('Jack', 24, **extra)
    ##    name: Jack age: 24 other: {'city': 'Beijing', 'job': 'Engineer'}
    
    #定义为命名关键参数的话， 自身不成为字典，只是像往常一样的参数一样复制即可
    #调用时必须以 参数=值的形式显示， 并且在填入参数时，命名关键参数必须定义值
    
    ## 定义为classmethod 因此子类继承时，调用该类方法时，传入的类变量cls是子类，而非父类
    ##而且可以对于类方法，可以通过类来调用，就像C.f()
    
    
    @asyncio.coroutine
    def save(self): ## 仅保存一行信息
        args=list(map(self.getValueOrDefault,self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows=yield from execute(self.__insert__, args)
        if rows!=1:
            logging.warn('failed to insert recored:affected  rows:%s'%rows)
            
            
            
    
    
    
#****************************
class Field(object):
    
    def __init__(self,name,column_type,primary_key,default):
        
        self.name=name
        self.column_type=column_type
        self.primary_key=primary_key
        self.default=default
    
    def __str__(self): ##print(Field()时自动调用
        return '<%s,%s,%s,%s>' % (self.__class__.__name__,self.column_type,self.name,self.primary_key)  ##__class__.__name__ 所属类的名字
    
    
class StringField(Field):
    
    def __init__(self,name=None,primary_key=False,default=None,column_type='varchar (100)'):
        super().__init__(name,column_type,primary_key,default)
 
class BooleanField(Field):
    def __init__(self,name=None,default=False):
        super().__init__(name,'boolean',False,default)       


class IntergerField(Field):
    
    def __init__(self,name=None,primary_key=False,default=0):
        super().__init__(name,'bigint',primary_key,default)

class FloatField(Field):
    def __init__(self,name=None,primary_key=False,default=0.0):
        super().__init__(name,'float',primary_key,default)
         
class TextField(Field):
    def __init__(self,name=None,default=None):
        super().__init__(name,'text',False,default)    


#***********************************




