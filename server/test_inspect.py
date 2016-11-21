'''
Created on 2016年10月17日

@author: ux501
'''
import inspect

def f(a,b,c,*,d=4,**kw):
    print(a,b,c,kw)
    
def f2(a):
    
    return (a,)

print(type(f2(1)))

print(inspect.signature(f).parameters)

parms=inspect.signature(f).parameters  
print(type(parms))
for name,param in parms.items():
    if param.kind==inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
        print(name)
        