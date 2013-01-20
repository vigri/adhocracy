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
import random

from check_port_free import check_port_free   
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException  
from selenium.webdriver.support.wait import WebDriverWait

if not hasattr(unittest.TestCase, 'assertRegexpMatches'): # Python<2.7
    unittest.TestCase.assertRegexpMatches = (lambda self, text, epat:
    self.assertTrue(re.match(epat, text)))

    
class selTest(unittest.TestCase):
    
    setup_done = False
    login_cookie = ""
    
    # get adhocracy and paster_interactive dir    
    adhocracy_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..','..'))+os.sep
    paster_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..','..','..'))+os.sep

    # Login / password for admin-user
    adhocracy_login_admin = {'username':'test2','password':'test'}
    
    # Login / password for non-admin-user
    adhocracy_login_user = {'username':'user','password':'pass'}
    
    def is_text_present(self, text):
        try:
            el = self.driver.feinigeind_element_by_tag_name("body")
        except NoSuchElementException, e:
            return False
        return textnot in el.text    
    
    def check_element_exists_by_xpath(self,xpath):
        # Check if an element exists by given xpath
        try:
            self.driver.find_element_by_xpath(xpath),
        except NoSuchElementException:
            return False
        return True
    
    def check_element_exists_by_id(self,dat):
        try:
            self.driver.find_element_by_id(dat)
        except NoSuchElementException:
            return False
        return True
    
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
    def test_title_adhocracy(self):
        self.driver.get('http://adhocracy.lan:5001')
        title_tag = self.driver.find_element_by_tag_name('title')        
        self.assertTrue("Adhocracy" in title_tag.text)
    
    def test_login(self):
        # Just a test
        print "first try"
        self.ensure_login(True)
        print self.login_cookie["value"]
        print "second try"
        self.ensure_login(True)
        print self.login_cookie["value"]
        print "third try"
        self.ensure_login(False)
        print self.login_cookie["value"]
        
    def xtest_register(self):
        self.driver.get('http://adhocracy.lan:5001')
        
        b_register = self.driver.find_element_by_xpath('//div[@class="register"]//a[@class="button link_register_now"]')
        b_register.click()    
        
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
        
        self.driver.find_element_by_id('user_menu')
        
    def login_user(self):
        self.driver.get('http://adhocracy.lan:5001')
        #print self.driver.page_source
        
        l_login = self.driver.find_element_by_css_selector('#nav_login > a')
        l_login.click()
        
        i_login = self.driver.find_element_by_css_selector('input[name="login"]')
        i_login.send_keys(self.adhocracy_login['username'])
        
        i_password = self.driver.find_element_by_css_selector('input[name="password"]')
        i_password.send_keys(self.adhocracy_login['password'])    
        
        b_submit = self.driver.find_element_by_xpath('//form[@id="login"]//input[@type="submit"]')
        b_submit.click()
        #    self.driver.wait_for_page_to_load("20000")        
        # Check if login was successful
        
        #element = WebDriverWait(self.webdriver, 10).until(lambda driver : driver.find_element_by_id('user_menu'))
        w = WebDriverWait(self.driver, 10)
        w.until(lambda driver: driver.find_element_by_id('user_menu'))

        selTest.cookies = self.driver.get_cookies()
        for cookie in selTest.cookies:
            if cookie["name"] == "adhocracy_login":
                selTest.login_cookie = cookie
                
    def ensure_login(self, login_as_admin):
        if selTest.login_cookie:
            print "we are logged in"
            if self.adhocracy_login['admin'] == login_as_admin:
                print "nothing to do"
            else:
                print "new login"
                selTest.login_cookie = ""
                selTest.driver.delete_cookie("adhocracy_login")
                
                if login_as_admin:
                    self.adhocracy_login = {'username':self.adhocracy_login_admin['username'],'password':self.adhocracy_login_admin['password'],'admin':True}
                else:
                    self.adhocracy_login = {'username':self.adhocracy_login_user['username'],'password':self.adhocracy_login_user['password'],'admin':False}
                self.login_user()
        else:
            print "need to login"
            selTest.login_cookie = ""
            selTest.driver.delete_cookie("adhocracy_login")
            
            if login_as_admin:
                self.adhocracy_login = {'username':self.adhocracy_login_admin['username'],'password':self.adhocracy_login_admin['password'],'admin':True}
            else:
                self.adhocracy_login = {'username':self.adhocracy_login_user['username'],'password':self.adhocracy_login_user['password'],'admin':False}
            self.login_user()
            
if __name__ == '__main__':
    unittest.main()