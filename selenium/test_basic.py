#!/usr/bin/env python
# -*- coding: utf-8 -*-

import selenium001
import unittest
#import org.openqa.selenium.JavascriptExecutor

from selenium001 import selTest, additionalInfoOnException, jsRequired

class Test_basic(selTest):
    @additionalInfoOnException
    def test_title_adhocracy(self):
        self.loadPage()
        self.searchAndWait_by_tag_name('title')
        title_tag = self.driver.find_element_by_tag_name('title')
        self.assertTrue("Adhocracy" in title_tag.text)

    @additionalInfoOnException
    def xtest_register(self):
        self.loadPage()
    
        
        b_register = self.searchAndWait_css('//div[@class="register"]//a[@class="button link_register_now"]')
        b_register.click()
    
        i_username = self.searchAndWait_css('//form[@name="create_user"]//input[@name="user_name"]')
        i_username.send_keys("selenium_user_test")
    
        i_email = self.driver.searchAndWait_css('//form[@name="create_user"]//input[@name="email"]')
        i_email.send_keys("selenium_user_test@example.com")
    
        i_password = self.driver.searchAndWait_css('//form[@name="create_user"]//input[@name="password"]')
        i_password.send_keys("test")
    
        i_password2 = self.driver.searchAndWait_css('//form[@name="create_user"]//input[@name="password_confirm"]')
        i_password2.send_keys("test")
    
        b_submit = self.driver.searchAndWait_css('//form[@name="create_user"]//input[@type="submit"]')
        b_submit.click()
    
        self.searchAndWait_css('#user_menu')
        
    @additionalInfoOnException
    def _test_create_proposal_comment(self):
        instance_name = "my instance"
        proposal_name = "new test proposal"
        self.ensure_login(login_as_admin=True)
        self.loadPage()
        #self.ensure_instance_exists(instance_name);
        #self.ensure_proposal_exists(proposal_name);
    
        self.loadPage("/i/myinstance/proposal/23-new_test_proposal")
    
    
        t_description = self.driver.find_element_by_xpath('//form[@name="new_comment"]//textarea[@name="text"]')
        t_description.send_keys("Test comment")
        
        
        
        
        b_submit = self.driver.find_element_by_xpath('//form[@name="new_comment"]//input[@type="submit"]')
        b_submit.click()
        
        self.searchAndWait_css('a[id="start-discussion-button"]')
    
    def _test_create_instance(self,newInstanceName='newInstance12345'):
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
        i_label.send_keys(newInstanceName)
    
        i_key = self.driver.find_element_by_xpath('//form[@name="create_instance"]//input[@name="key"]')
        i_key.send_keys(newInstanceName.replace(" ", ""))
    
        t_description = self.driver.find_element_by_xpath('//form[@name="create_instance"]//textarea[@name="description"]')
        t_description.send_keys(instanceDescription)
    
        b_submit = self.driver.find_element_by_xpath('//form[@name="create_instance"]//button[@type="submit"]')
        b_submit.click()
        
        # todo wait x seconds until check is performed
        if not self.is_text_present(instanceDescription):
            raise Exception("Creation of instance failed!")
    
    
    
    def _test_create_proposal(self,newProposalName='newTestProposal12345'):
        # TODO: Fails if proposal exists
        # <span class="error-message">An entry with this title already exists</span>
    
        # first we need to ensure the user is logged in and the instance for our new proposal exists
        instance_name = "my instance"
        self.ensure_login(login_as_admin=True)
        self.loadPage()
        self.ensure_instance_exists(instance_name);
    
        #l_instances = self.driver.find_element_by_css_selector('#nav_instances > a')
        #l_instances.click()
        #self.searchAndWait_xpath('//div[@class="top_actions title"]//a[@class="button title add"]')
    
        #l_instance = self.searchAndWait_xpath("li[contains(text(), 'my instance')]")
        #l_instance.click();
    
        # temp!!!
        self.loadPage("/i/myinstance/instance/myinstance")
    
    
        l_proposals = self.searchAndWait_css('#subnav-proposals > a')
        l_proposals.click()
        
        l_new_proposal = self.searchAndWait_css('#new-proposal > a')
        l_new_proposal.click()
        
        i_label = self.driver.find_element_by_xpath('//form[@name="create_proposal"]//input[@name="label"]')
        i_label.send_keys(newProposalName)
        
        for option in self.driver.find_elements_by_tag_name('option'):
            if option.text == instance_name:
                option.click()
        
        i_tags = self.driver.find_element_by_xpath('//form[@name="create_proposal"]//input[@name="tags"]')
        i_tags.send_keys("test-tag")
        
        t_description = self.driver.find_element_by_xpath('//form[@name="create_proposal"]//textarea[@name="text"]')
        t_description.send_keys("proposal description")
        
        b_submit = self.driver.find_element_by_xpath('//form[@name="create_proposal"]//button[@type="submit"]')
        b_submit.click()
        
        self.searchAndWait_css('#discussions')
        
if __name__ == '__main__':
    unittest.main()