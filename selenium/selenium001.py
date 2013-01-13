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

if not hasattr(unittest.TestCase, 'assertRegexpMatches'): # Python<2.7
    unittest.TestCase.assertRegexpMatches = (lambda self, text, epat:
	self.assertTrue(re.match(epat, text)))
	
	
class selTest(unittest.TestCase):
    
    # get adhocracy and paster_interactive dir    
    adhocracy_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..','..'))+os.sep
    paster_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','..','..','..'))+os.sep

    # Login / password for admin-user
    adhocracy_login_admin = {'username':'test2','password':'test'}
    
    # Login / password for non-admin-user
    adhocracy_login_user = {'username':'user','password':'pass'}
    
    login_as_admin = True # TODO: Read command line argument to set the user-type
    
    if login_as_admin:
	adhocracy_login = {'username':adhocracy_login_admin['username'],'password':adhocracy_login_admin['password']}
    else:
	adhocracy_login = {'username':adhocracy_login_user['username'],'password':adhocracy_login_user['password']}
	
    def is_text_present(self, text):
	try:
	    el = self.driver.find_element_by_tag_name("body")
	except NoSuchElementException, e:
	    return False
	return text in el.text    

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
        self.verificationErrors = []
	
        errors = check_port_free([4444,5001], opts_kill='pgid', opts_gracePeriod=10)
        if errors:
            raise Exception("\n".join(errors))
	
        # Database isolation - trivial - copy database to some other destination
        shutil.copyfile(os.path.join(selTest.adhocracy_dir,'var','development.db'),os.path.join(selTest.adhocracy_dir,'src','adhocracy','selenium','bak_db','adhocracy_backup.db'))       
    
        # Start Selenium Server Standalone
        self.sel_server = self.start_selenium_server_standalone()
        
        # Start Adhocracy
        self.adhocracy = self.start_adhocracy()  

        errors = check_port_free([4444, 5001], opts_gracePeriod=30, opts_graceInterval=0.1, opts_open=True)
        if errors:            
            raise Exception("\n".join(errors))
       
        self.driver = webdriver.Remote(
        command_executor = 'http://127.0.0.1:4444/wd/hub',
        desired_capabilities={'browserName': 'htmlunit',
                                        'version':'2',
                                        'javascriptEnabled': True
                        })
        #self.driver = webdriver.Firefox()
    
    def tearDown(cls): #tearDownClass
        cls.driver.close()

        # Shutdown Selenium Server Standalone
        cls.shutdown_server(cls.sel_server.pid)
        
        # Shutdown Adhocracy
        cls.shutdown_adhocracy(cls.adhocracy.pid)        

        # Database isolation - trivial - restore our saved database
        shutil.copyfile(os.path.join(selTest.adhocracy_dir,'src','adhocracy','selenium','bak_db','adhocracy_backup.db'),os.path.join(selTest.adhocracy_dir,'var','development.db'))
        
    def xtest_title_adhocracy(self):
        self.driver.get('http://adhocracy.lan:5001')
        title_tag = self.driver.find_element_by_tag_name('title')        
        self.assertTrue("Adhocracy" in title_tag.text)
	
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

    def test_login(self):
	
	self.driver.get('http://adhocracy.lan:5001')
	
	l_login = self.driver.find_element_by_css_selector('#nav_login > a')
	l_login.click()
	
	i_login = self.driver.find_element_by_css_selector('input[name="login"]')
	i_login.send_keys(self.adhocracy_login['username'])
	
	i_password = self.driver.find_element_by_css_selector('input[name="password"]')
	i_password.send_keys(self.adhocracy_login['password'])	
	
	b_submit = self.driver.find_element_by_xpath('//form[@id="login"]//input[@type="submit"]')
	b_submit.click()

	# Check if login was successful
	self.driver.find_element_by_id('user_menu')
	
	cookies = self.driver.get_cookies()
	#for cookie in cookies:
	#    cookie["name"] cookie["value"]

if __name__ == '__main__':
    unittest.main()

                        