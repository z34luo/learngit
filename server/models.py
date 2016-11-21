'''
Created on 2016年10月18日

@author: ux501
'''


from orm  import Model,StringField



class User(Model):
    __table__='users'
    username=StringField(primary_key=True,column_type='varchar 50')
    password=StringField(column_type='varchar(50)')
