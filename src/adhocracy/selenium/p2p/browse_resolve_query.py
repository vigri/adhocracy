import select
import socket
import sys
import pybonjour
import time

regtype  = "_test._tcp" #sys.argv[1]
timeout  = 5
queried  = []
resolved = []


def query_record_callback(sdRef, flags, interfaceIndex, errorCode, fullname,
                          rrtype, rrclass, rdata, ttl):
    if errorCode == pybonjour.kDNSServiceErr_NoError:
        print socket.inet_ntoa(rdata)
        queried.append(True)


def resolve_callback(sdRef, flags, interfaceIndex, errorCode, fullname,
                     hosttarget, port, txtRecord):
    if errorCode != pybonjour.kDNSServiceErr_NoError:
        return

    print '#####'
    print fullname
    print hosttarget
    print port

    query_sdRef = \
        pybonjour.DNSServiceQueryRecord(interfaceIndex = interfaceIndex,
                                        fullname = hosttarget,
                                        rrtype = pybonjour.kDNSServiceType_A,
                                        callBack = query_record_callback)

    try:
        while not queried:
            ready = select.select([query_sdRef], [], [], timeout)
            if query_sdRef not in ready[0]:
                print 'Query record timed out'
                break
            pybonjour.DNSServiceProcessResult(query_sdRef)
        else:
            queried.pop()
    finally:
        query_sdRef.close()

    resolved.append(True)


def browse_callback(sdRef, flags, interfaceIndex, errorCode, serviceName,
                    regtype, replyDomain):
    if errorCode != pybonjour.kDNSServiceErr_NoError:
        return

    if not (flags & pybonjour.kDNSServiceFlagsAdd):
        print 'Service removed'
        return

    print 'Service added; resolving'

    resolve_sdRef = pybonjour.DNSServiceResolve(0,
                                                interfaceIndex,
                                                serviceName,
                                                regtype,
                                                replyDomain,
                                                resolve_callback)

    try:
        while not resolved:
            ready = select.select([resolve_sdRef], [], [], timeout)
            if resolve_sdRef not in ready[0]:
                print 'Resolve timed out'
                break
            pybonjour.DNSServiceProcessResult(resolve_sdRef)
        else:
            resolved.pop()
    finally:
        resolve_sdRef.close()

    
browse_sdRef = pybonjour.DNSServiceBrowse(regtype = regtype,
                                          callBack = browse_callback)



tmax = 3
first_time = time.time()

"""
try:
    try:
        while True:
            ready = select.select([browse_sdRef], [], [])

            if browse_sdRef in ready[0]:
                pybonjour.DNSServiceProcessResult(browse_sdRef)

            new_time = time.time()
            print new_time
            print first_time
            print new_time - first_time
            
            if  new_time - first_time > tmax:
                print "timeout"
                sys.exit(0)
            else:
                print "no"
    except KeyboardInterrupt:
        pass
finally:
    browse_sdRef.close()
    
"""

x=0
while(x<20):
    ready = select.select([browse_sdRef], [], [])
    
    if browse_sdRef in ready[0]:
        pybonjour.DNSServiceProcessResult(browse_sdRef)
    x = x+1
browse_sdRef.close()