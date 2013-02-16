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

from check_port_free import check_port_free
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait

def _displayInformation(e):
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    url = gist_upload("Selenium driven test\n"+dt +"\n%r" % e+"]",selTest.driver.page_source,dt,"html")
                      
    print 'Exception: %r' % e
    print 'Sourcecode of website: ' + url
    
    """ Since htmlUnit has no screenshot-support the image upload only can be performed
    if the browserName differs from 'htmlUnit'
    """
    try:
        print 'Screenshot: '+ imgur_upload(e.screen)
    except AttributeError:
        print 'Screenshot: not supported'

def additionalInfoOnException(func):
    def test_wrapper(self):
        try:
            func(self)
        except BaseException as e:
            _displayInformation(e)
            raise
    return test_wrapper

def gist_upload(desc, content,date,ext):
    d = json.dumps({
        "description":desc,
        "public":False,
        "files":{
                 date+"."+ext:{
                        "content":content
                        }
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
    login_cookie = ""

    clientId = 'b96e44dc87cf435'
    url = 'https://api.imgur.com/3/image'
    apikey = 'f48846809cc73b8bcabbd41335a08525085ed947'
    opener = urllib2.build_opener(urllib2.ProxyHandler({}))



    # get adhocracy and paster_interactive dir
    adhocracy_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..','..'))+os.sep
    paster_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..','..','..'))+os.sep

    # Login / password for admin-user
    adhocracy_login_admin = {'username':'admin','password':'password'}
    
    # Login / password for non-admin-user
    adhocracy_login_user = {'username':'test2','password':'test'}
    
    def searchAndWait_xpath(self, xpath, wait=10):
        func = lambda driver: driver.find_element_by_xpath(xpath)
        WebDriverWait(self.driver, wait).until(func)
        return func(self.driver)

    def searchAndWait_css(self, xpath, wait=10):
        func = lambda driver: driver.find_element_by_css_selector(xpath)
        WebDriverWait(self.driver, wait).until(func)
        return func(self.driver)

    def searchAndWait_by_tag_name(self, tagName, wait=10):
        func = lambda driver: driver.find_element_by_tag_name(tagName)
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
        cmd = ['java','-Djava.security.egd=file:/dev/./urandom','-jar',os.path.join(selTest.adhocracy_dir,'src','adhocracy','selenium','res','selenium-2.26.0','selenium-server-standalone-2.26.0.jar')]
        proc = subprocess.Popen(cmd,stderr=null,stdout=null,preexec_fn=os.setsid)
        return proc

    def shutdown_server(self,pid):
        os.killpg(pid, signal.SIGTERM)

    def start_adhocracy(self):
        null=open('/dev/null','wb')  
        proc = subprocess.Popen(selTest.paster_dir+'paster_interactive.sh',stderr=null, stdout=null,preexec_fn=os.setsid)
        return proc

    def shutdown_adhocracy(self, pid):
        os.killpg(pid, signal.SIGTERM)

    def setUp(self):
        if not self.setup_done:
            selTest.setup_done = True

            selTest.verificationErrors = []

            errors = check_port_free([4444,5001], opts_kill='pgid', opts_gracePeriod=10)
            if errors:
                raise Exception("\n".join(errors))

            # Database isolation - trivial - copy database to some other destination
            shutil.copyfile(os.path.join(selTest.adhocracy_dir,'var','development.db'),os.path.join(selTest.adhocracy_dir,'src','adhocracy','selenium','bak_db','adhocracy_backup.db'))       

            # Start Selenium Server Standalone
            selTest.sel_server = self.start_selenium_server_standalone()

            # Start Adhocracy
            selTest.adhocracy = self.start_adhocracy()  

            errors = check_port_free([4444, 5001], opts_gracePeriod=30, opts_graceInterval=0.1, opts_open=True)
            if errors:
                raise Exception("\n".join(errors))

            selTest.driver = webdriver.Remote(
            command_executor = 'http://127.0.0.1:4444/wd/hub',
            desired_capabilities={'browserName': 'htmlunit',
                                            'version':'2',
                                            'javascriptEnabled': True
                            })
    def tearDown(self): #tearDownClass
        """self.driver.close()
        # Shutdown Selenium Server Standalone
        self.shutdown_server(self.sel_server.pid)
        
        # Shutdown Adhocracy
        self.shutdown_adhocracy(self.adhocracy.pid)
        
        # Database isolation - trivial - restore our saved database
        shutil.copyfile(os.path.join(selTest.adhocracy_dir,'src','adhocracy','selenium','bak_db','adhocracy_backup.db'),os.path.join(selTest.adhocracy_dir,'var','development.db'))
        """

    @additionalInfoOnException
    def test_title_adhocracy(self):
        self.loadPage()
        self.searchAndWait_by_tag_name('title')
        title_tag = self.driver.find_element_by_tag_name('title')
        self.assertTrue("Adhocracy" in title_tag.text)

    @additionalInfoOnException
    def xtest_register(self):
        self.loadPage()

        self.searchAndWait_css('//div[@class="register"]//a[@class="button link_register_now"]')
        b_register = self.driver.find_element_by_xpath('//div[@class="register"]//a[@class="button link_register_now"]')
        b_register.click()

        self.searchAndWait_css('//form[@name="create_user"]//input[@name="user_name"]')
        i_username = self.driver.find_element_by_xpath('//form[@name="create_user"]//input[@name="user_name"]')
        i_username.send_keys("selenium_user_test")

        i_email = self.driver.find_element_by_xpath('//form[@name="create_user"]//input[@name="email"]')
        i_email.send_keys("selenium_user_test@example.com")

        i_password = self.driver.find_element_by_xpath('//form[@name="create_user"]//input[@name="password"]')
        i_password.send_keys("test")

        i_password2 = self.driver.find_element_by_xpath('//form[@name="create_user"]//input[@name="password_confirm"]')
        i_password2.send_keys("test")

        b_submit = self.driver.find_element_by_xpath('//form[@name="create_user"]//input[@type="submit"]')
        b_submit.click()

        self.searchAndWait_css('#user_menu')

    @additionalInfoOnException
    def login_user(self):
        self.loadPage()
        self.searchAndWait_css('#nav_login > a')
        
        l_login = self.driver.find_element_by_css_selector('#nav_login > a')
        l_login.click()
        self.searchAndWait_css('input[name="login"]')

        i_login = self.driver.find_element_by_css_selector('input[name="login"]')
        i_login.send_keys(self.adhocracy_login['username'])

        i_password = self.driver.find_element_by_css_selector('input[name="password"]')
        i_password.send_keys(self.adhocracy_login['password'])

        b_submit = self.driver.find_element_by_xpath('//form[@id="login"]//input[@type="submit"]')
        b_submit.click()

        self.searchAndWait_css('#user_menu')

        selTest.cookies = self.driver.get_cookies()
        for cookie in selTest.cookies:
            if cookie["name"] == "adhocracy_login":
                selTest.login_cookie = cookie

    def ensure_login(self, login_as_admin):
        # check if the user is currently logged in
        if selTest.login_cookie:
            # only do something if the current login-type differs from the desired login-type
            if self.adhocracy_login['admin'] != login_as_admin:
                # delete the stored var and relevant cookie (force "logout")
                selTest.login_cookie = ""
                selTest.driver.delete_cookie("adhocracy_login")

                if login_as_admin:
                    selTest.adhocracy_login = {'username':self.adhocracy_login_admin['username'],'password':self.adhocracy_login_admin['password'],'admin':True}
                else:
                    selTest.adhocracy_login = {'username':self.adhocracy_login_user['username'],'password':self.adhocracy_login_user['password'],'admin':False}
                self.login_user()
        else:
            if login_as_admin:
                selTest.adhocracy_login = {'username':self.adhocracy_login_admin['username'],'password':self.adhocracy_login_admin['password'],'admin':True}
            else:
                selTest.adhocracy_login = {'username':self.adhocracy_login_user['username'],'password':self.adhocracy_login_user['password'],'admin':False}
            self.login_user()

    @additionalInfoOnException
    def xtest_create_instance(self):
        instanceDescription = "Selenium Test Instance"
        self.ensure_login(login_as_admin=True)
        self.loadPage()
        self.searchAndWait_css('#nav_instances > a')

        l_instances = self.driver.find_element_by_css_selector('#nav_instances > a')
        l_instances.click()
        self.searchAndWait_xpath('//div[@class="top_actions title"]//a[@class="button title add"]')

        l_instance_new = self.driver.find_element_by_xpath('//div[@class="top_actions title"]//a[@class="button title add"]')
        l_instance_new.click()
        self.searchAndWait_xpath('//form[@name="create_instance"]//input[@name="label"]')

        i_label = self.driver.find_element_by_xpath('//form[@name="create_instance"]//input[@name="label"]')
        i_label.send_keys("test instance 2")

        i_key = self.driver.find_element_by_xpath('//form[@name="create_instance"]//input[@name="key"]')
        i_key.send_keys("testinst2")

        t_description = self.driver.find_element_by_xpath('//form[@name="create_instance"]//textarea[@name="description"]')
        t_description.send_keys(instanceDescription)

        b_submit = self.driver.find_element_by_xpath('//form[@name="create_instance"]//bu1tton[@type="submit"]')
        b_submit.click()
        
        # todo wait x seconds until check is performed
        if not self.is_text_present(instanceDescription):
            raise Exception("Creation of instance failed!")

    def loadPage(self,path=""):
        self.driver.get('http://adhocracy.lan:5001'+path)

if __name__ == '__main__':
    unittest.main()