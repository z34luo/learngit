'''
Created on 2016年10月17日

@author: ux501
'''


import orm 
import asyncio
from orm import *



class User(Model):
    __table__='User'
    id = IntergerField(primary_key=True)
    name=StringField()
    def show(self):
        print(1, '__mappings__:', self.__mappings__)
        print(2, '__table__:', self.__table__)
        print(3, '__primary_key__:', self.__primary_key__)
        print(4, '__fields__:', self.__fields__)
        print(5, '__select__:', self.__select__)
        print(6, '__insert__:', self.__insert__)
        print(7, '__update__:', self.__update__)
        print(8, '__delete__:', self.__delete__)

"""
user = User(id=123, name='Michael', job='engneer')
print('-------create finish-----------')
user.show()
print(9, user)
"""

loop=asyncio.get_event_loop()

@asyncio.coroutine
def test():
    yield from create_pool(loop,host='localhost', port=3306, user='root', password='newpassword', database='test')
    user = User(id=10, name='Ablin')
    yield from user.save()
    r = yield from User.find('10')
    print(r)
    
    yield from destory_pool()
    
loop.run_until_complete(test())
loop.close()
