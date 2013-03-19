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
import time

from check_port_free import check_port_free
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from ElementNotFound import ElementNotFound
from selenium.common.exceptions import TimeoutException







class selTest(unittest.TestCase):

    @classmethod
    def gist_upload(cls,desc, content,log,date):
        if cls.adhocracy_remote:
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
    
    @classmethod
    def imgur_upload(cls,picture):
        #with open(path, 'rb') as f:
            #picture = base64.b64encode(f.read())
        data = urllib.urlencode({ 'key' : cls.apikey, 'image' : picture })
        req = urllib2.Request(cls.url, data)
        req.add_header('Authorization', 'Client-ID ' + cls.clientId)
        json_response = urllib2.urlopen(req)
        json_response = json.load(json_response)
        
        if(json_response['status'] == 200):
            return json_response['data']['link']
        else:
            return "Error on upload"

    @classmethod
    def _displayInformation(cls,e):
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
        cls.logfile.flush()
        log  = open('logfile', 'r').read()
    
        url = cls.gist_upload("Selenium driven test\n"+dt +"\n%r" % e+"]",cls.driver.page_source,log,dt)
    
        print '\n  > Exception: %r' % e
        print '  > Sourcecode of website: ' + url
        
        """ Since some drivers have no screenshot-support (such htmlunit) the image upload only can be performed
            if the screenshot function is supported
        """
        try:
            print '  > Screenshot: '+ cls.imgur_upload(cls.driver.get_screenshot_as_base64())
        except Exception:
            print '  > Screenshot: not supported'

    ### Decorators
    @classmethod
    def additionalInfoOnException(cls,func):
        def wrapper(cls):
            try:
                func(cls)
            except BaseException as e:
                cls._displayInformation(e)
                raise
        wrapper.__name__ = func.__name__
        return wrapper

    @classmethod
    def jsRequired(cls,func):
        def wrapper(cls):
            if(cls.driver.desired_capabilities['javascriptEnabled'] == True):
                func(cls)
            else:
                print "This function requires JavaScript"
                return
        wrapper.__name__ = func.__name__
        return wrapper

    @classmethod
    def waitCSS(cls, css, wait=10, raiseException=True):
        # the raiseException parameter is needed for functions which handle exceptions on their own
        if raiseException:
            try:
                func = lambda driver: driver.find_element_by_css_selector(css)
                WebDriverWait(cls.driver, wait).until(func,css)
                return func(cls.driver)
            except TimeoutException:
                raise ElementNotFound(css)
        else:
            func = lambda driver: driver.find_element_by_css_selector(css)
            WebDriverWait(cls.driver, wait).until(func,css)
            return func(cls.driver)

    def waitXpath(self,xpath, wait=10, raiseException=True):
        if raiseException:
            try:
                func = lambda driver: driver.find_element_by_xpath(xpath)
                WebDriverWait(self.driver, wait).until(func)
                return func(self.driver)
            except TimeoutException:
                raise ElementNotFound(xpath)
        else:
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
        errors = check_port_free([5001], opts_kill='pgid', opts_gracePeriod=10)
        if errors:
            raise Exception("\n".join(errors))

        proc = subprocess.Popen(selTest.adhocracy_dir+'bin/adhocracy_interactive.sh',stderr=self.logfile, stdout=self.logfile, shell=True, preexec_fn=os.setsid)

        errors = check_port_free([5001], opts_gracePeriod=30, opts_graceInterval=0.1, opts_open=True)
        if errors:
            raise Exception("\n".join(errors))

        return proc

    def shutdown_adhocracy(self, pid):
        os.killpg(pid, signal.SIGTERM)

    @classmethod
    def _create_xvfb_display(cls):
        # Used for xvfb output. For debugging purposes this can be set to a file
        null=open('/dev/null','wb')

        # Get virtual display
        # get first free virtual display number
        display_number = 0
        while True:
            display_number += 1
            if not os.path.isfile("/tmp/.X"+str(display_number)+"-lock"):
                break

        subprocess.Popen(['Xvfb',':'+str(display_number),'-ac','-screen','0','1024x768x16'],stderr=null, stdout=null)
        os.environ["DISPLAY"]=":"+str(display_number)

    def _create_video(self):
        # to get a better quality, decrease the qmax parameter

        null=open('/dev/null','wb')

        creationTime = int(time.time())
        video_path = '/tmp/seleniumTest_'+str(creationTime)+'.mpg'
        selTest.pFfmpeg = subprocess.Popen(['ffmpeg','-f','x11grab','-r','25','-s','1024x768','-qmax','6','-i',':0.0','/tmp/blubb.mpg'],stderr=null, stdout=null)

    def _database_backup_create(self):
        # Database isolation - trivial - copy database to some other destination
        shutil.copyfile(os.path.join(selTest.adhocracy_dir,'var','development.db'),os.path.join(selTest.adhocracy_dir,'src','adhocracy','selenium','bak_db','adhocracy_backup.db'))       

    #def _database_backup_restore(self):
        # Database isolation - trivial - restore our saved database
        #shutil.copyfile(os.path.join(selTest.adhocracy_dir,'src','adhocracy','selenium','bak_db','adhocracy_backup.db'),os.path.join(selTest.adhocracy_dir,'var','development.db'))

    @classmethod
    def _create_webdriver(cls,browser):
        if browser == "htmlunit":
            errors = check_port_free([4444], opts_kill='pgid', opts_gracePeriod=10)
            if errors:
                raise Exception("\n".join(errors))
        
            # Start Selenium Server Standalone
            cls.sel_server = cls.start_selenium_server_standalone()
            
            errors = check_port_free([4444], opts_gracePeriod=30, opts_graceInterval=0.1, opts_open=True)
            if errors:
                raise Exception("\n".join(errors))

            desired_caps = webdriver.DesiredCapabilities.HTMLUNIT
            desired_caps['version'] = "2"

            if(cls.envDisableJs):
                desired_caps['javascriptEnabled'] = "False"
            else:
                desired_caps['javascriptEnabled'] = "True"

            cls.driver = webdriver.Remote(
            command_executor = 'http://127.0.0.1:4444/wd/hub',
            desired_capabilities=desired_caps
            )
        elif browser == "firefox":
            fp = webdriver.FirefoxProfile()
            
            if(cls.envDisableJs):
                fp.set_preference("javascript.enabled", False);

            cls.driver = webdriver.Firefox(firefox_profile=fp)
        elif browser == "chrome":
            cls.driver = webdriver.Chrome('res/chromedriver_x64_26.0.1383.0')
            # No javascript-disable support for chrome!
        else:
            raise Exception("Invalid browser selected")

    @classmethod
    def setUpClass(cls):
        print "DEBUG: setUpClass ..."

        cls.setup_done = True
    
        cls.adhocracy_remote = False
        cls.login_cookie = ""
    
        #Imgur vars
        cls.clientId = 'b96e44dc87cf435'
        cls.url = 'https://api.imgur.com/3/image'
        cls.apikey = 'f48846809cc73b8bcabbd41335a08525085ed947'
        cls.opener = urllib2.build_opener(urllib2.ProxyHandler({}))
    
        cls.logfile = open('logfile', 'w')
        
        cls.Config = ConfigParser.ConfigParser()
        # get adhocracy and paster_interactive dir
        cls.adhocracy_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..','..'))+os.sep
        cls.paster_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..','..','..'))+os.sep
    
        # Login / password for admin and non-user
        cls.adhocracy_login_admin = {'username':'admin','password':'password'}
        cls.adhocracy_login_user = {'username':'','password':''}    # will be filled out by _create_default_user
    
        #selTest.setup_done = True
        
        cls.pFfmpeg = None  # Holds the subprocess of ffmpeg - if used
        
        # get configuration File
        #if not os.path.isfile("selenium.ini"):
        #    raise Exception("Configuration file not found!")

        # Path to configuration file
        cls.Config.read("selenium.ini")


        cls.verificationErrors = []
        cls.defaultUser = ""
        cls.defaultUserPassword = ""
        cls.defaultProposalUrl = ""


        ##### Process environment variables

        # disable Xvfb
        cls.envShowTests = os.environ.get("selShowTests","") =="1"

        # create video
        cls.envCreateVideo = os.environ.get("selCreateVideo","") =="1"

        # selected browser
        try:  
            cls.envSelectedBrowser = os.environ["selBrowser"]
        except KeyError:
            cls.envSelectedBrowser = "chrome"

        # javascript
        cls.envDisableJs = os.environ.get("selDisableJS","") =="1"

        # start local adhocracy server
        cls.envStartAdh = os.environ.get("selStartAdh","") =="1"

        # remote adhocracy url
        try:  
            cls.adhocracyUrl = os.environ["selAdhocracyUrl"]
            cls.adhocracy_remote = True
            cls.envStartAdh = False
        except KeyError: 
            cls.adhocracyUrl = "http://adhocracy.lan:5001"
            cls.adhocracy_remote = False


        #### Take actions based on env. vars.

        # Since htmlunit has no real display output, envShowTests and envCreateVideo cannot be used
        if cls.envSelectedBrowser == "htmlunit":
           cls.nvShowTests = False;
           cls.envCreateVideo = False

        cls.envShowTests = True

        if not cls.envShowTests:
            cls._create_xvfb_display()
        else:
            cls.envCreateVideo = False

        if cls.envCreateVideo:
            cls._create_video()
        #self._create_video()
        # Start adhocracy server if specified
        if not cls.adhocracy_remote:
            if cls.envStartAdh:
                # get adhocracy dir
                cls.adhocracy_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..','..'))+os.sep
                # Start Adhocracy
                cls.adhocracy = cls.start_adhocracy()

        # create webdriver based on selected browser
        cls._create_webdriver(browser=cls.envSelectedBrowser)

        cls._create_default_user()
        
    def setUp(self):
        if not self.setup_done:
            raise Exception("Global setup has not been called. Please use Python >=2.7 or nosetests")

    @classmethod
    def tearDownClass(cls):
        print "DEBUG: tearDownClass..."
        cls.driver.close()

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
    
    @classmethod
    #@additionalInfoOnException
    def _create_default_user(cls):
        # This function creates a default user which can be used for other interactions within tests
        creationTime = int(time.time())
        userName = str(creationTime)+cls.envSelectedBrowser
        cls.loadPage('/register')

        i_username = cls.waitCSS('form[name="create_user"] input[name="user_name"]')
        i_username.send_keys(userName)

        i_email = cls.waitCSS('form[name="create_user"] input[name="email"]')
        i_email.send_keys(userName+"@example.com")

        i_password = cls.waitCSS('form[name="create_user"] input[name="password"]')
        i_password.send_keys("test")

        i_password2 = cls.waitCSS('form[name="create_user"] input[name="password_confirm"]')
        i_password2.send_keys("test")

        b_submit = cls.waitCSS('form[name="create_user"] input[type="submit"]')
        b_submit.click()

        cls.waitCSS('#user_menu')
        cls.force_logout()
        cls.adhocracy_login_user['username'] = userName
        cls.adhocracy_login_user['password'] = 'test'

    @classmethod
    def _login_user(cls):
        cls.loadPage()
        
        l_login = cls.waitCSS('#nav_login > a')
        l_login.click()
        
        i_login = cls.waitCSS('input[name="login"]')
        i_login.send_keys(cls.adhocracy_login['username'])

        i_password = cls.waitCSS('input[name="password"]')
        i_password.send_keys(cls.adhocracy_login['password'])

        b_submit = cls.waitCSS('form[name="login"] input[type="submit"]')
        b_submit.click()

        cls.waitCSS('#user_menu')

        cls.cookies = cls.driver.get_cookies()
        for cookie in cls.cookies:
            if cookie["name"] == "adhocracy_login":
                cls.login_cookie = cookie

    @classmethod
    def ensure_login(cls, login_as_admin=False):
        # check if the user is currently logged in
        if cls.login_cookie:
            # only do something if the current login-type differs from the desired login-type
            if cls.adhocracy_login['admin'] != login_as_admin:
                # delete the stored cookie-var and relevant cookie
                cls.force_logout()

                if login_as_admin:
                    cls.adhocracy_login = {'username':cls.adhocracy_login_admin['username'],'password':cls.adhocracy_login_admin['password'],'admin':True}
                else:
                    cls.adhocracy_login = {'username':cls.adhocracy_login_user['username'],'password':cls.adhocracy_login_user['password'],'admin':False}
                cls._login_user()
        else:
            if login_as_admin:
                cls.adhocracy_login = {'username':cls.adhocracy_login_admin['username'],'password':cls.adhocracy_login_admin['password'],'admin':True}
            else:
                cls.adhocracy_login = {'username':cls.adhocracy_login_user['username'],'password':cls.adhocracy_login_user['password'],'admin':False}
            cls._login_user()

    @classmethod
    def force_logout(cls):
        # Delete the login-cookie (if existent) to ensure the user is not logged in
        cls.login_cookie = ""
        cls.driver.delete_cookie("adhocracy_login")

    def ensure_is_member_of_group(self):
        # Check if the user needs to join the instance, if so, click on the 'join' button
        # if an timeoutException occurs, it means, we are allready a member and don't need to join
        # raiseException is set to False, so nothing happens if the 'join' button is not found
        try:
            b_join_group = self.waitCSS('.message .register > a',wait=2,raiseException=False)
            b_join_group.click()
        except TimeoutException:
            pass
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

    @classmethod
    def loadPage(cls,path=""):
        cls.driver.get(cls.adhocracyUrl+path)

if __name__ == '__main__':
    unittest.main()