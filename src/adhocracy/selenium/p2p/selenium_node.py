#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    
"""

import select
import sys
import pybonjour
import subprocess
import os

try:
    browser = sys.argv[1]
except IndexError:
    browser = 'htmlunit'

name    = "selenium_linux_" + browser
regtype = "_test._tcp"
port    = 4444

def register_callback(sdRef, flags, errorCode, name, regtype, domain):
    if errorCode == pybonjour.kDNSServiceErr_NoError:
        print 'Registered service:'
        print '  name    =', name
        print '  regtype =', regtype
        print '  domain  =', domain
        
null = open('/dev/null', 'wb')
server_path = os.path.join('res', 'selenium', 'selenium-server-standalone.jar')

if browser == "chrome":
    if os.path.isfile('res/chrome/chromedriver'):
        cmd = ['java', '-Djava.security.egd=file:/dev/./urandom', '-Dwebdriver.chrome.driver=res/chrome/chromedriver', '-jar', server_path]
    else:
        raise Exception('Chromedriver not found')
elif browser == "htmlunit":
    cmd = ['java', '-Djava.security.egd=file:/dev/./urandom', '-jar', server_path]


sdRef = pybonjour.DNSServiceRegister(name = name, regtype = regtype, port = port, callBack = register_callback)
pSel_server = subprocess.Popen(cmd, stderr=null, stdout=null, preexec_fn=os.setsid)

print('Selenium Server started...')
try:
    try:
        while True:
            ready = select.select([sdRef], [], [])
            if sdRef in ready[0]:
                pybonjour.DNSServiceProcessResult(sdRef)
    except KeyboardInterrupt:
        pass
finally:
    sdRef.close()
    pSel_server.kill()
