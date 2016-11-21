'''
Created on 2016年10月17日

@author: ux501
'''

import config_default
 
##重新定义dict类 
class Dict(dict): 

 
    def __init__(self, names=(), values=(), **kw): 
        super(Dict, self).__init__(**kw) 
        for k, v in zip(names, values): 
            self[k] = v 

 
    def __getattr__(self, key): 
        try: 
            return self[key] 
        except KeyError: 
           raise AttributeError(r"'Dict' object has no attribute '%s'" % key) 
 
 
    def __setattr__(self, key, value): 
        self[key] = value 

def merge(default,override):
    r={}
    for k,v in default.items():
        if k in override:
            print(k)
            if isinstance(v,dict):
                print('1',k)
                r[k]=merge(v,override[k])
            else:
                r[k]=override[k]
        else:
            r[k]=v
    return r

def toDict(d):
    D=Dict()
    for k,v in d.items():
        D[k]=toDict(v) if isinstance(v,dict) else v
    return D

try:
    
    import config_override
    configs=config_default.configs
    configs=merge(configs,config_override.configs)

except ImportError:
    pass


configs=toDict(configs)