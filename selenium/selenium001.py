#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import shutil
import subprocess
import shlex
import os
import signal

from check_port_free import check_port_free   
from selenium import webdriver


class vgTest(unittest.TestCase):
    def start_selenium_server_standalone(self):
        null=open('/dev/null','wb')
        cmd = ['java','-jar','res/selenium-2.26.0/selenium-server-standalone-2.26.0.jar']
        proc = subprocess.Popen(cmd,preexec_fn=os.setsid)
        return proc
    
    def shutdown_server(self,pid):
        os.killpg(pid, signal.SIGTERM)
    
    def start_adhocracy(self):
        null=open('/dev/null','wb')
        ## __file__
        ## os.path.dirname(__file__)
        ## os.pazh.join
        proc = subprocess.Popen('../../../../paster_interactive.sh',preexec_fn=os.setsid)
        return proc
        
    def shutdown_adhocracy(self, pid):
        os.killpg(pid, signal.SIGTERM)    
                  
    def setUp(self):    
        username = "virgil"
        password = "xxx"       
        
        errors = check_port_free([4444,5001], opts_kill='pgid', opts_gracePeriod=10)
        if errors:    
            # Fehler
            raise Exception("\n".join(errors))
        
        # Database isolation - trivial - copy database to some other destination
        shutil.copyfile('../../../var/development.db','bak_db/adhocracy_backup.db')       
    
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
        shutil.copyfile('bak_db/adhocracy_backup.db','../../../var/development.db')
        
    def xtest_title_google(self):
        self.driver.get('http://google.com')
        title_tag = self.driver.find_element_by_tag_name('title')
        self.assertEqual(title_tag.text, 'Google')
        
    def test_title_adhocracy(self):
        self.driver.get('http://adhocracy.lan:5001')
        title_tag = self.driver.find_element_by_tag_name('title')
        #self.assertEqual(title_tag.text, 'Adhocracy')        
        self.assertTrue("Adhocracy" in title_tag.text)

if __name__ == '__main__':
    unittest.main()

                        