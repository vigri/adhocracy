#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""
import os
import subprocess
import select
import sys
import inspect


pth = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
misc_folder = os.path.join(pth, '..', 'misc')

if misc_folder not in sys.path:
    sys.path.insert(0, misc_folder)

import pybonjour




try:
    browser = sys.argv[1]
except IndexError:
    browser = 'err'

name    = "selenium Testnode " + sys.platform
regtype = "_selenium._tcp"
port    = 4444



def register_callback(sdRef, flags, errorCode, name, regtype, domain):
    if errorCode == pybonjour.kDNSServiceErr_NoError:
        print '  Registered service:'
        print '    name    =', name
        print '    regtype =', regtype
        print '    domain  =', domain

def isWindows():
    if os.name == 'nt':
        return True
    else:
        # todo: better recognition!
        return False


root_folder = os.path.join(pth, '..')

server_path = os.path.join(root_folder,'res', 'selenium', 'selenium-server-standalone.jar')

# Paths
if isWindows():
    txt_os = "windows"  # txt record for bonjour
    chromedriver = os.path.join(root_folder, 'res','chrome','chromedriver.exe')
    firefox = os.path.join('C:','Programme','Mozilla Firefox','firefox.exe')
    internetexplorer = os.path.join(root_folder, 'res','internetexplorer','IEDriverServer.exe')
else:
    txt_os = "linux" # txt record for bonjour
    chromedriver = os.path.join(root_folder, 'res','chrome','chromedriver')
    firefox = os.path.join(root_folder, 'res:','firefox','firefox-bin')


if browser == "chrome":
    if os.path.isfile(chromedriver):
        cmd = ['java', '-Djava.security.egd=file:/dev/./urandom', '-Dwebdriver.chrome.driver=' + chromedriver, '-jar', server_path]
    else:
        raise Exception('Chromedriver not found')
elif browser == "firefox":
    if os.path.isfile(firefox):
        cmd = ['java', '-Djava.security.egd=file:/dev/./urandom', '-Dwebdriver.firefox.bin=' + firefox, '-jar', server_path]
    else:
        raise Exception('Internet Explorer driver not found')
elif browser == "internetexplorer":
    if os.path.isfile(internetexplorer):
        cmd = ['java', '-Djava.security.egd=file:/dev/./urandom', '-Dwebdriver.ie.driver=' + firefox, '-jar', server_path]
elif browser == "htmlunit":
    cmd = ['java', '-Djava.security.egd=file:/dev/./urandom', '-jar', server_path]
else:
    raise Exception('Please specify a valid browser (chrome | htmlunit | firefox | internetexplorer)')

sdRef = pybonjour.DNSServiceRegister(name = name,
                                     regtype = regtype,
                                     port = port,
                                     txtRecord = pybonjour.TXTRecord({'os': txt_os, 'browser': browser}),
                                     callBack = register_callback)

# Start selenium server
null = open(os.devnull, 'wb')
pSel_server = subprocess.Popen(cmd, stderr=null, stdout=null)

print('Selenium Server started...')
print(' Offered plattform: ' + sys.platform)
print(' Offered browser: ' + browser)
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
