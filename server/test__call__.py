'''
Created on 2016年10月17日

@author: ux501
'''

class Foo(object):
    def __init__(self):
        print('__init__ executed')

    def __call__(self):
           print('_call__ executed')

print(Foo())
print(isinstance(Foo(),Foo))

print(Foo()())

f=Foo()
print(f)