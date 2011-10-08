import socketserver
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import time
import multiprocessing
import random
import sys 
from subprocess import * 

jobs={}

# Threaded mix-in to handle more than one client at a time.
class AsyncXMLRPCServer(socketserver.ThreadingMixIn,SimpleXMLRPCServer): pass

#http://code.activestate.com/recipes/576684-simple-threading-decorator/
def run_async(func):
    """
    run_async(func)
	    function decorator, intended to make "func" run in a separate
	    thread (asynchronously).
	    Returns the created Thread object

	    E.g.:
	    @run_async
	    def task1():
		    do_something

	    @run_async
	    def task2():
		    do_something_too

	    t1 = task1()
	    t2 = task2()
	    ...
	    t1.join()
	    t2.join()
    """
    from threading import Thread
    from multiprocessing import Process	
    from functools import wraps

    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = Thread(target = func, args = args, kwargs = kwargs)
#        func_hl = Process(target = func, args = args, kwargs = kwargs)			
        func_hl.start()
        return func_hl

    return async_func
    

def mypow( x, y):
    return pow(x, y)

def myadd(x, y) :
    return x + y

def mydivide( x, y):
    return float(x) / float(y)

@run_async
def mymul(myname, x, y):
    jobs[myname]='<started>'
    time.sleep(random.uniform(0,5))
    jobs[myname]= x * y

@run_async
def mypscount(myname):
    jobs[myname]='<started>'
    sout=getoutput("sleep 3;ps -ef | wc -l ")
    jobs[myname]=sout

         
#public class
class mathCalls:
        
    def pow(self, x, y):
        return mypow(x, y)
 
    def add(self, x, y) :
        return myadd(x, y)
 
    def divide(self, x, y):
        return mydivide(x,y)

    def mul(self, x, y):
        jobid='mul:'+str(time.time())
        jobs[jobid]='<queued>'        
        mymul(jobid,x,y)
        return jobid

    def pscount(self):
        jobid='pscount:'+str(time.time())
        jobs[jobid]='<queued>'        
        mypscount(jobid)
        return jobid

    def jobresult(self,jobid):
        return(jobs[jobid])

    def jobs():
        return(jobs)
 
if __name__ == '__main__':
    # Instantiate and bind to localhost
    server = AsyncXMLRPCServer(('localhost', 8000), SimpleXMLRPCRequestHandler)

    # Register example object instance
    server.register_instance(mathCalls())
    server.register_introspection_functions()

    # run!
    server.serve_forever()
