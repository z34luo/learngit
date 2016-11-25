'''
Created on 2016年11月26日

@author: ux501
'''
import time,threading

global global_signal
global_signal=''

local_school = threading.local()

def process_student():
    # 获取当前线程关联的student:
    std = local_school.student
    global global_signal
    global_signal=std
    while True:
        if(global_signal=='Bob'):
            print("end of %s" % threading.current_thread().name)
            break;
        time.sleep(1)
        print('Hello, %s (in %s)' % (std, threading.current_thread().name))
        print(global_signal)

def process_thread(name):
    # 绑定ThreadLocal的student:
    local_school.student = name
    process_student()

t1 = threading.Thread(target= process_thread, args=('Alice',), name='Thread-A')
t2 = threading.Thread(target= process_thread, args=('Bob',), name='Thread-B')
t1.setDaemon(True)
t2.setDaemon(True)
t1.start()
time.sleep(2)
t2.start()
print("t2 start")
time.sleep(10)

