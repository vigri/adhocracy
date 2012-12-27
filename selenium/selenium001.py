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



from check_port_free import check_port_free   
from selenium import webdriver

if not hasattr(unittest.TestCase, 'assertRegexpMatches'): # Python<2.7
    unittest.TestCase.assertRegexpMatches = (lambda self, text, epat:
	self.assertTrue(re.match(epat, text)))
	
	
class selTest(unittest.TestCase):
    # get adhocracy dir
    adhocracy_dir_arr = os.path.dirname(os.path.abspath(__file__)).split(os.sep)
    adhocracy_dir_arr_len = len(adhocracy_dir_arr)-3 # remove last 3 elements to ensure we have the 'root' of adhocracy
    paster_dir_len = len(adhocracy_dir_arr)-4        # paster_interactive.sh is outside the adhocracy dir
    adhocracy_dir = os.sep+os.path.join(*adhocracy_dir_arr[:adhocracy_dir_arr_len])+os.sep
    paster_dir = os.sep+os.path.join(*adhocracy_dir_arr[:paster_dir_len])+os.sep
    
    # Login / password for admin-user
    adhocracy_login_admin = {'username':'test2','password':'test'}
    
    # Login / password for non-admin-user
    adhocracy_login_user = {'username':'user','password':'pass'}
    
    def is_text_present2(self, text):
	try:
	    el = self.driver.find_element_by_tag_name("body")
	except NoSuchElementException, e:
	    return False
	return text in el.text    

    def check_folder(self,path):
        # Ensure given path exists, if not create it
        try:
            os.makedirs(path)
	    file = open(path,'/.git_keep_this', 'w')
	    file.write('')
	    file.close()
            
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
    def start_selenium_server_standalone(self):
        null=open('/dev/null','wb')
        cmd = ['java','-jar',os.path.join(selTest.adhocracy_dir,'src','adhocracy','selenium','res','selenium-2.26.0','selenium-server-standalone-2.26.0.jar')]
        proc = subprocess.Popen(cmd,stderr=null,stdout=null,preexec_fn=os.setsid)
        return proc
    
    def shutdown_server(self,pid):
        os.killpg(pid, signal.SIGTERM)
    
    def start_adhocracy(self):
        null=open('/dev/null','wb')
        ## __file__
        ## os.path.dirname(__file__)
        ## os.pazh.join
        proc = subprocess.Popen(selTest.paster_dir+'paster_interactive.sh',stderr=null, stdout=null,preexec_fn=os.setsid)
        return proc
        
    def shutdown_adhocracy(self, pid):
        os.killpg(pid, signal.SIGTERM)    
                  
    def setUp(self):    

        self.verificationErrors = []
	
        errors = check_port_free([4444,5001], opts_kill='pgid', opts_gracePeriod=10)
        if errors:    
            # Fehler
            raise Exception("\n".join(errors))
        
        # Ensure bak_db folder exists, if not create it
        self.check_folder('bak_db')
        
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
        
        
    def tearDown(self):
        self.driver.close()

        # Shutdown Selenium Server Standalone
        self.shutdown_server(self.sel_server.pid)
        
        # Shutdown Adhocracy
        self.shutdown_adhocracy(self.adhocracy.pid)        

        # Database isolation - trivial - restore our saved database
        shutil.copyfile(os.path.join(selTest.adhocracy_dir,'src','adhocracy','selenium','bak_db','adhocracy_backup.db'),os.path.join(selTest.adhocracy_dir,'var','development.db'))
        
    def xtest_title_google(self):
        self.driver.get('http://google.com')
        title_tag = self.driver.find_element_by_tag_name('title')
        self.assertEqual(title_tag.text, 'Google')
        
    def xtest_title_adhocracy(self):
        self.driver.get('http://adhocracy.lan:5001')
        title_tag = self.driver.find_element_by_tag_name('title')
        #self.assertEqual(title_tag.text, 'Adhocracy')        
        self.assertTrue("Adhocracy" in title_tag.text)
    
    def test_login(self):
	self.driver.get('http://adhocracy.lan:5001')
	self.driver.find_element_by_css_selector("#nav_login > a").click()
	
	self.driver.find_element_by_name("login").clear()
	self.driver.find_element_by_name("login").send_keys("test2")	

	self.driver.find_element_by_name("password").clear()
	self.driver.find_element_by_name("password").send_keys("test")
	
	self.driver.find_element_by_css_selector("input[type=\"submit\"]").click()	

	
	pwwrong = self.is_text_present2("Benutzername oder falsches Passwort.") # TODO: Multilanguage?
	# TODO: Umlauts are not accepted in search-string. "Ungültiger Benutzername oder flasches Passwort."
	
	if pwwrong:    
	    # Fehler
	    raise Exception(self.driver.page_source)	# Temp
	    #Username or password wrong ("+self.adhocracy_login_admin['username']+")"
    
if __name__ == '__main__':
    unittest.main()

                        