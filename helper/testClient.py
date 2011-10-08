#!/usr/bin/python
import xmlrpc.client
from time import sleep
import re
import datetime
import sys

s = xmlrpc.client.ServerProxy('http://localhost:8000')
# Print list of available methods
print(s.system.listMethods())


#Sample call to a function in the server, wait for results and return them
jobTopCarriers=s.topCarriers()
while s.jobresult(jobTopCarriers) in ('','<queued>','<started>'):
	sleep(1)
	print("no result yet...")
	print(s.jobs())	
aresult=s.jobresult(jobTopCarriers)
print('carrier result is:'  + str(aresult))
s.jobdelete(jobTopCarriers)
threatlist=eval(aresult)

for x in range(1,len(threatlist)):
	#print(threatlist[x])
	#print(threatlist[x]['count'])
	#print(threatlist[x]['threatname'])
	print(threatlist[x]['targethostname']    )
sys.exit(0)
#Sample error handling if we've already deleted job results.
try:
	aresult=s.jobresult(jobTopCarriers)
	print('carrier result is:'  + str(aresult))
except Exception as e:
	if (re.search('KeyError',str(e))):
		print('already got this job result')
		pass
	else: 
		print(e)




#detail for a carrier
#Sample call to a function in the server, wait for results and return them
jobCarrierDetail=s.carrierDetail('hn-562.anonpc.id')
while s.jobresult(jobCarrierDetail) in ('','<queued>','<started>'):
	sleep(1)
	print("no result yet...")
	print(s.jobs())	
aresult=s.jobresult(jobCarrierDetail)
#print('carrierDetail result is:'  + str(aresult)[:100])
s.jobdelete(jobCarrierDetail)
carrierDetail=eval(aresult)
for x in range(1,len(carrierDetail)):
	print(carrierDetail[x]['VirusName'])
	print(carrierDetail[x]['FileName'])