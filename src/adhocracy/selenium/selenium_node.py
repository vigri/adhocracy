#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Start a selenium node and offer a specific browser
"""

import os
import subprocess
import select
import sys
import inspect


script_path = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
misc_folder = os.path.join(script_path, 'misc')

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



server_path = os.path.join(script_path, 'res', 'all', 'selenium', 'selenium-server-standalone.jar')

if not os.path.isfile(server_path):
    raise Exception('Selenium-Server not found in ' + server_path)

# Paths
if isWindows():
    txt_os = "windows"  # txt record for bonjour
    chromedriver = os.path.join(script_path, 'res', 'windows', 'chrome','chromedriver.exe')
    firefox = os.path.join('C:' + os.sep,'Programme','Mozilla Firefox','firefox.exe')
    internetexplorer = os.path.join(script_path, 'res', 'windows', 'internetexplorer','IEDriverServer.exe')
else:
    txt_os = "linux" # txt record for bonjour
    chromedriver = os.path.join(script_path, 'res', 'linux', 'chrome','chromedriver')
    firefox = os.path.join(script_path, 'res', 'windows', 'firefox', 'firefox-bin')


if browser == "chrome":
    if os.path.isfile(chromedriver):
        cmd = ['java', '-Djava.security.egd=file:/dev/./urandom', '-Dwebdriver.chrome.driver=' + chromedriver, '-jar', server_path]
    else:
        raise Exception('Chromedriver not found')
elif browser == "firefox":
    if os.path.isfile(firefox):
        cmd = ['java', '-Djava.security.egd=file:/dev/./urandom', '-Dwebdriver.firefox.bin=' + firefox, '-jar', server_path]
    else:
        raise Exception('Firefox not found')
elif browser == "internetexplorer":
    if os.path.isfile(internetexplorer):
        cmd = ['java', '-Djava.security.egd=file:/dev/./urandom', '-Dwebdriver.ie.driver=' + internetexplorer, '-jar', server_path]
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

