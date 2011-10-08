#! /usr/bin/python2
import fileinput
import getopt
import os 
import re 
import string, sys, time
import osclib

#takes inbound cisco asa firewall log lines from stdin 
#parses them and sends them out as OSC messages
#2011 jeff bryner


ciscologre=re.compile(r"""(PIX.*|FWSM.*|ASM.*|ASA.*)""")
protocolre= re.compile(r"""TCP|UDP|ICMP""",re.IGNORECASE)
interfacere = re.compile(r""" on interface (.*)""",re.IGNORECASE)
ipre = re.compile(r"""((?:\d{1,3}\.){3}\d{1,3})""")

def main():
    HOST = 'localhost'
    PORT = 7111

    client = osclib.Client()
    client.connect((HOST, PORT))
    while 1: 
        line=sys.stdin.readline().strip()
        if not line:
            client.close()
            
            break
        else:
            
            #print("< %s >" %line)
            if re.search(ciscologre,line):
                for ciscotext in ciscologre.findall(line):
                    #defaults
                    action="unknown"
                    protocol="unknown"
                    sourceinterface="unknown"
                    destinationinterface="unknown"
                    sourceport=0
                    destport=0
                    sourceip='0.0.0.0'
                    destip='0.0.0.0'                    
                    if re.search(r'302013|302015',ciscotext): 
                        #%ASA-6-302013: Built inbound TCP connection 733280 for outside:192.168.208.63/51606 (192.168.208.63/51606) to inside:192.168.150.70/80 (192.168.150.70/80)
                        action="allow"
                        for foundProtocol in protocolre.findall(ciscotext):
                            protocol=foundProtocol.upper()

                        if len(ipre.findall(ciscotext))==4:
                            sourceip=ipre.findall(ciscotext)[0]
                            destip = ipre.findall(ciscotext)[2]

                        #make a regex with the sourceip we just found to get the source port just after it
                        sourceportre=re.compile(sourceip + r"""\/([a-zA-Z0-9]+)""")
                        
                        for port in sourceportre.findall(ciscotext):
                            sourceport=port
                        #make a regex with the destination ip we just found to get the destination port just after it                        
                        destportre=re.compile(destip + r"""\/([a-zA-Z0-9]+)""")
                        
                        for port in destportre.findall(ciscotext):
                            destport=port
                        
                        #try the interfaces again if there in front of the ip like interface:ipaddress/port
                        if sourceinterface=="unknown":
                            sourceinterfacere=re.compile(r""" ([a-zA-Z0-9]+)\:""" + sourceip)
                            for interface in sourceinterfacere.findall(ciscotext):
                                sourceinterface=interface
                        if destinationinterface=="unknown":
                            destinationinterfacere=re.compile(r""" ([a-zA-Z0-9]+)\:""" + destip)
                            for interface in destinationinterfacere.findall(ciscotext):
                                destinationinterface=interface
                    elif re.search(r'302020',ciscotext):
                        #%ASA-6-302020: Built ICMP connection for faddr 192.168.208.63/15343 gaddr 192.168.150.70/0 laddr 192.168.150.70/0
                        action="allow"
                        for foundProtocol in protocolre.findall(ciscotext):
                            protocol=foundProtocol.upper()

                        if len(ipre.findall(ciscotext))==3:
                            sourceip=ipre.findall(ciscotext)[0]
                            destip = ipre.findall(ciscotext)[2]
                    elif re.search(r'400014',ciscotext):
                        #400014: IDS:2004 ICMP echo request from 192.220.74.179 to 192.168.150.77 on interface outside
                        action="allow"
                        for foundProtocol in protocolre.findall(ciscotext):
                            protocol=foundProtocol.upper()
                            
                        for foundInterface in interfacere.findall(ciscotext):
                            sourceinterface=foundInterface.upper()
                        
                        if len(ipre.findall(ciscotext))==2:
                            sourceip=ipre.findall(ciscotext)[0]
                            destip = ipre.findall(ciscotext)[1]
                            
                    elif re.search(r'Drop|Deny|discarded|denied|Invalid transport',ciscotext):		
                    #catch all parsing for the myriad of cisco messages such as:
                    #       ASA-2-106001: Inbound TCP connection denied from 10.21.144.12/8076 to 192.168.21.15/3360 flags SYN ACK  on interface LAN
                    #       ASA-3-305005: No translation group found for icmp src DMZ:192.168.244.236 dst INTERNET:17.9.239.251 (type 0, code 0) 
                    #       ASA-4-106023: Deny protocol 49 src INTERNET:218.106.119.133 dst DMZ:17.7.239.93 by access-group "INTERNET_acl" [0x0, 0x0]     

                        action="block"
                        for foundProtocol in protocolre.findall(ciscotext):
                            protocol=foundProtocol.upper()
                            
                        for foundInterface in interfacere.findall(ciscotext):
                            sourceinterface=foundInterface.upper()
                        
                        if len(ipre.findall(ciscotext))==2:
                            sourceip=ipre.findall(ciscotext)[0]
                            destip = ipre.findall(ciscotext)[1]
                        
                        #make a regex with the sourceip we just found to get the source port just after it
                        sourceportre=re.compile(sourceip + r"""\/([a-zA-Z0-9]+)""")
                        
                        for port in sourceportre.findall(ciscotext):
                            sourceport=port
                        #make a regex with the destination ip we just found to get the destination port just after it                        
                        destportre=re.compile(destip + r"""\/([a-zA-Z0-9]+)""")
                        
                        for port in destportre.findall(ciscotext):
                            destport=port
                        
                        #try the interfaces again if there in front of the ip like interface:ipaddress/port
                        if sourceinterface=="unknown":
                            sourceinterfacere=re.compile(r""" ([a-zA-Z0-9]+)\:""" + sourceip)
                            for interface in sourceinterfacere.findall(ciscotext):
                                sourceinterface=interface
                        if destinationinterface=="unknown":
                            destinationinterfacere=re.compile(r""" ([a-zA-Z0-9]+)\:""" + destip)
                            for interface in destinationinterfacere.findall(ciscotext):
                                destinationinterface=interface
                                
                    print ("%s: %s %s:%s:%s --> %s:%s:%s" %(action, protocol, sourceinterface, sourceip, sourceport, destinationinterface, destip, destport))
                               
                    client.send(osclib.Message('/asalog', action, protocol, sourceinterface, sourceip, sourceport, destinationinterface, destip, destport))
                    
                
                


main()