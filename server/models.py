'''
Created on 2016年10月18日

@author: ux501
'''


from orm  import Model,StringField
import uuid
import time

def next_id():
    return '%015d%s000'%(int(time.time()),uuid.uuid4().hex)

class User(Model):
    __table__='users'
    username=StringField(primary_key=False,column_type='varchar (50)')
    password=StringField(column_type='varchar(50)')
    id=StringField(primary_key=True,default=next_id,column_type='varchar (50)')