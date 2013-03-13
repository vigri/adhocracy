#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import shutil
import subprocess
import shlex
import os
import signal
import errno
import re
import httplib
import urllib
import urllib2
import json
import datetime
import base64
import ConfigParser
import multiprocessing

from pyvirtualdisplay import Display
from check_port_free import check_port_free
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from ElementNotFound import ElementNotFound


def setupAll():
    print "setup class"

def _displayInformation(e):
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    selTest.logfile.flush()
    log  = open('logfile', 'r').read()

    url = gist_upload("Selenium driven test\n"+dt +"\n%r" % e+"]",selTest.driver.page_source,log,dt)

    print 'Exception: %r' % e
    print 'Sourcecode of website: ' + url
    
    """ Since some drivers have no screenshot-support (such htmlunit) the image upload only can be performed
        if the screenshot function is supported
    """
    try:
        print 'Screenshot: '+ imgur_upload(selTest.driver.get_screenshot_as_base64())
    except Exception:
        print 'Screenshot: not supported'

### Decorators
def additionalInfoOnException(func):
    def wrapper(self):
        try:
            func(self)
        except Exception as e:
            _displayInformation(e)
            raise
    wrapper.__name__ = func.__name__
    return wrapper

def jsRequired(func):
    def wrapper(self):
        if(selTest.driver.desired_capabilities['javascriptEnabled'] == True):
            func(self)
        else:
            print "This function requires JavaScript"
            return
    wrapper.__name__ = func.__name__
    return wrapper

def gist_upload(desc, content,log,date):
    if selTest.adhocracy_remote:
        log = "No logfile available. Using remote adhocracy server"

    d = json.dumps({
        "description":desc,
        "public":False,
        "files":{
                 date+" - Sourcecode.html":{ "content":content },
                 date+" - Logfile.text":{ "content":log }
                }
    })
    res = urllib2.urlopen('https://api.github.com/gists',d).read()
    resd = json.loads(res)
    return resd['html_url']

def imgur_upload(picture):
    #with open(path, 'rb') as f:
        #picture = base64.b64encode(f.read())
    data = urllib.urlencode({ 'key' : selTest.apikey, 'image' : picture })
    req = urllib2.Request(selTest.url, data)
    req.add_header('Authorization', 'Client-ID ' + selTest.clientId)
    json_response = urllib2.urlopen(req)
    json_response = json.load(json_response)
    
    if(json_response['status'] == 200):
        return json_response['data']['link']
    else:
        return "Error on upload"

class selTest(unittest.TestCase):
    setup_done = False

    adhocracy_remote = False
    login_cookie = ""

    #Imgur vars
    clientId = 'b96e44dc87cf435'
    url = 'https://api.imgur.com/3/image'
    apikey = 'f48846809cc73b8bcabbd41335a08525085ed947'
    opener = urllib2.build_opener(urllib2.ProxyHandler({}))

    logfile = open('logfile', 'w')
    
    Config = ConfigParser.ConfigParser()
    # get adhocracy and paster_interactive dir
    adhocracy_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..','..'))+os.sep
    paster_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..','..','..'))+os.sep

    # Login / password for admin-user
    adhocracy_login_admin = {'username':'admin','password':'password'}

    # Login / password for non-admin-user
    adhocracy_login_user = {'username':'test2','password':'test'}
    
    def waitCSS(self, css, wait=10):
        func = lambda driver: driver.find_element_by_css_selector(css)
        WebDriverWait(self.driver, wait).until(func,css)
        return func(self.driver)

    def waitXpath(self,xpath, wait=10):
        func = lambda driver: driver.find_element_by_xpath(xpath)
        WebDriverWait(self.driver, wait).until(func)
        return func(self.driver)

    def is_text_present(self, text):
        try:
            el = self.driver.find_element_by_tag_name("body")
        except NoSuchElementException, e:
            return False
        return text in el.text    

    def start_selenium_server_standalone(self):
        null=open('/dev/null','wb')

        cmd = ['java','-Djava.security.egd=file:/dev/./urandom','-jar','-Dwebdriver.chrome.driver=res/chromedriver_x64_26.0.1383.0',os.path.join(selTest.adhocracy_dir,'src','adhocracy','selenium','res','selenium-2.26.0','selenium-server-standalone-2.26.0.jar')]

        proc = subprocess.Popen(cmd,stderr=null,stdout=null,preexec_fn=os.setsid)
        return proc

    def shutdown_server(self,pid):
        os.killpg(pid, signal.SIGTERM)

    def start_adhocracy(self):
        null=open('/dev/null','wb')  
        
        proc = subprocess.Popen(selTest.paster_dir+'paster_interactive.sh',stderr=self.logfile, stdout=self.logfile, shell=True, preexec_fn=os.setsid)
        
        return proc

    def shutdown_adhocracy(self, pid):
        os.killpg(pid, signal.SIGTERM)

    def setUp(self):
        if not self.setup_done:
            selTest.setup_done = True
            if not os.path.isfile("selenium.ini"):
                raise Exception("Configuration file not found!")

            # Path to configuration file
            selTest.Config.read("selenium.ini")

            selTest.verificationErrors = []

            selTest.testInstanceName = ""
            selTest.testInstanceKey = ""
            
            
            # Check for first free virtual display number
            display_number = 0
            while True:
                display_number += 1
                if not os.path.isfile("/tmp/.X"+str(display_number)+"-lock"):
                    break

            subprocess.Popen(['Xvfb', ':'+str(display_number),'-ac','-screen','0','1024x768x16'])
            os.environ["DISPLAY"]=":"+str(display_number)

            # Database isolation - trivial - copy database to some other destination
            #shutil.copyfile(os.path.join(selTest.adhocracy_dir,'var','development.db'),os.path.join(selTest.adhocracy_dir,'src','adhocracy','selenium','bak_db','adhocracy_backup.db'))       

            # Temp!
            # Database isolation - trivial - restore our saved database
            shutil.copyfile(os.path.join(selTest.adhocracy_dir,'src','adhocracy','selenium','bak_db','adhocracy_backup.db'),os.path.join(selTest.adhocracy_dir,'var','development.db'))

            selTest.adhocracy_remote = False

            if not self.adhocracy_remote:
                errors = check_port_free([5001], opts_kill='pgid', opts_gracePeriod=10)
                if errors:
                    raise Exception("\n".join(errors))

                # Start Adhocracy
                selTest.adhocracy = self.start_adhocracy()  

                errors = check_port_free([5001], opts_gracePeriod=30, opts_graceInterval=0.1, opts_open=True)
                if errors:
                    raise Exception("\n".join(errors))

            # Check which browser has been selected. If none, use htmlunit
            try:  
                selTest.selectedBrowser = os.environ["selenium.browser"]
            except KeyError: 
                selTest.selectedBrowser = "CHROME"  # HTMLUNIT

            try:  
                selTest.disableJs = os.environ["selenium.disableJs"]
            except KeyError: 
                selTest.disableJs = "0"


            # Setup driver based on selected browser
            if self.selectedBrowser == "HTMLUNIT":
                errors = check_port_free([4444], opts_kill='pgid', opts_gracePeriod=10)
                if errors:
                    raise Exception("\n".join(errors))
            
                # Start Selenium Server Standalone
                selTest.sel_server = self.start_selenium_server_standalone()
                
                errors = check_port_free([4444], opts_gracePeriod=30, opts_graceInterval=0.1, opts_open=True)
                if errors:
                    raise Exception("\n".join(errors))

                desired_caps = webdriver.DesiredCapabilities.HTMLUNIT
                desired_caps['version'] = "2"

                if(selTest.disableJs == "1"):
                    desired_caps['javascriptEnabled'] = "False"
                else:
                    desired_caps['javascriptEnabled'] = "True"

                selTest.driver = webdriver.Remote(
                command_executor = 'http://127.0.0.1:4444/wd/hub',
                desired_capabilities=desired_caps
                )
            elif self.selectedBrowser == "FIREFOX":
                fp = webdriver.FirefoxProfile()
                
                if(selTest.disableJs == "1"):
                    fp.SetPreference("javascript.enabled", False);
                
                selTest.driver = webdriver.Firefox(firefox_profile=fp,)
            elif self.selectedBrowser == "CHROME":
                selTest.driver = webdriver.Chrome('res/chromedriver_x64_26.0.1383.0',)
                
                # No javascript-disable support for chrome!

    def tearDown(self): #tearDownClass
        #print "Teardown"
        """self.driver.close()
        # Shutdown Selenium Server Standalone
        self.shutdown_server(self.sel_server.pid)
        
        # Shutdown Adhocracy
        self.shutdown_adhocracy(self.adhocracy.pid)
        
        # Database isolation - trivial - restore our saved database
        shutil.copyfile(os.path.join(selTest.adhocracy_dir,'src','adhocracy','selenium','bak_db','adhocracy_backup.db'),os.path.join(selTest.adhocracy_dir,'var','development.db'))
        
        TODO: Remove logfile
        
        
        """



    def ensure_proposal_exists(self,instance_name,proposal_name):
        self.ensure_login(login_as_admin=True)
        self.loadPage("/instance")
        l_instance = self.waitXpath("//li[contains(text(), 'instance_name')]")
        #l_instance.click();
        
        # search and wait
        if not self.is_text_present(proposal_name):
            # instance doesn't exists. We need to create it
            self._test_create_proposal(proposal_name)


    
    def _login_user(self):
        self.loadPage()
        
        l_login = self.waitCSS('#nav_login > a')
        l_login.click()
        
        i_login = self.waitCSS('input[name="login"]')
        i_login.send_keys(self.adhocracy_login['username'])

        i_password = self.waitCSS('input[name="password"]')
        i_password.send_keys(self.adhocracy_login['password'])

        b_submit = self.waitCSS('form#login input[type="submit"]') #self.driver.find_element_by_xpath('//form[@id="login"]//input[@type="submit"]')
        b_submit.click()

        self.waitCSS('#user_menu')

        selTest.cookies = self.driver.get_cookies()
        for cookie in selTest.cookies:
            if cookie["name"] == "adhocracy_login":
                selTest.login_cookie = cookie

    #@additionalInfoOnException
    def ensure_login(self, login_as_admin):
        # check if the user is currently logged in
        if selTest.login_cookie:
            # only do something if the current login-type differs from the desired login-type
            if self.adhocracy_login['admin'] != login_as_admin:
                # delete the stored cookie-var and relevant cookie
                self.force_logout()

                if login_as_admin:
                    selTest.adhocracy_login = {'username':self.adhocracy_login_admin['username'],'password':self.adhocracy_login_admin['password'],'admin':True}
                else:
                    selTest.adhocracy_login = {'username':self.adhocracy_login_user['username'],'password':self.adhocracy_login_user['password'],'admin':False}
                self._login_user()
        else:
            if login_as_admin:
                selTest.adhocracy_login = {'username':self.adhocracy_login_admin['username'],'password':self.adhocracy_login_admin['password'],'admin':True}
            else:
                selTest.adhocracy_login = {'username':self.adhocracy_login_user['username'],'password':self.adhocracy_login_user['password'],'admin':False}
            self._login_user()

    def force_logout(self):
        # Delete the login-cookie (if existent) to ensure the user is not logged in
        selTest.login_cookie = ""
        selTest.driver.delete_cookie("adhocracy_login")

    def make_element_visible_by_id(self,elementId):
        self.driver.execute_script("document.getElementById('"+elementId+"').style.display = 'block';")

    def ConfigSectionMap(self,section):
        dict1 = {}
        options = self.Config.options(section)
        for option in options:
            try:
                dict1[option] = self.Config.get(section, option)
                if dict1[option] == -1:
                    DebugPrint("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
        return dict1

    def loadPage(self,path=""):
        self.driver.get('http://adhocracy.lan:5001'+path)

if __name__ == '__main__':
    unittest.main()