#!/usr/bin/python
import xmlrpc.client
from time import sleep

s = xmlrpc.client.ServerProxy('http://localhost:8000')
# Print list of available methods
print(s.system.listMethods())


print(s.pow(2,3))  # Returns 2**3 = 8
print(s.add(2,3))  # Returns 5

muljob=s.mul(5,2)
print(muljob)

while s.jobresult(muljob) in ('','<queued>','<started>'):
	sleep(1)
	print("no result yet...")

aresult=s.jobresult(muljob)
print('result is:'  + str(aresult))


psjob=s.pscount()
while s.jobresult(psjob) in ('','<queued>','<started>'):
	sleep(1)
	print("no result yet...")
aresult=s.jobresult(psjob)
print('pscount result is:'  + str(aresult))






