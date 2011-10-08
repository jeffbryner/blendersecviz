#!/usr/bin/python
import socketserver
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import time
import multiprocessing
import random
import sys 
from subprocess import * 
import os

jobs={}

#transaction/middle layer xmlrpc server to run commands and fetch data for blender
#2011: Jeff Bryner
#Called using xmlrpc, this server is multithreaded and async
#and will initialize a job reference for blender to use to drop off and pick up results. 
#
#Sample client/blender Code: 
#import xmlrpc.client
#from time import sleep
#s = xmlrpc.client.ServerProxy('http://localhost:8000')
# #Print list of available methods
#print(s.system.listMethods())
# #Call a function in the server and print results when they are ready:
#psjob=s.pscount()
#while s.jobresult(psjob) in ('','<queued>','<started>'):
#	sleep(1)
#	print("no result yet...")
#aresult=s.jobresult(psjob)
#print('pscount result is:'  + str(aresult))






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
        func_hl.start()
        return func_hl

    return async_func
    

@run_async
def myTopCarriers(myid):
    jobs[myid]='<started>'    
    #uncomment to add a random amount (0 to 5 secs) of real life delay
    #time.sleep(random.uniform(0,5))
    sout=getoutput("cat ./data/anon.topcarriers.dict ")
    jobs[myid]=sout


@run_async
def mycarrierDetail(myid,carrierName):
    jobs[myid]='<started>'    
    #uncomment to add a random amount (0 to 5 secs) of real life delay
    #time.sleep(random.uniform(0,5))
    sfile="./data/" + carrierName + ".detail.dict"
    if os.path.isfile(sfile):
        scmd="cat " + sfile
        sout=getoutput(scmd)
    else:
        sout=[]
    jobs[myid]=sout

class secData:
    def jobresult(self,jobid):
        return(jobs[jobid])

    def jobs(self):
        return(jobs)
    
    def jobdelete(self,jobid):
        jobs.pop(jobid,'')

    def topCarriers(self):
        jobid='carriers:'+str(time.time())
        jobs[jobid]='<queued>'        
        myTopCarriers(jobid)
        return jobid

    def carrierDetail(self,carrierName):
        jobid='carrierDetail:'+str(time.time())
        jobs[jobid]='<queued>'        
        mycarrierDetail(jobid,carrierName)
        return jobid    
 
if __name__ == '__main__':
    # Instantiate and bind to localhost
    server = AsyncXMLRPCServer(('localhost', 8000), SimpleXMLRPCRequestHandler,allow_none=True)

    # Register example object instance
    server.register_instance(secData())
    server.register_introspection_functions()

    # run!
    server.serve_forever()
