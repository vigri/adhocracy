#!/usr/bin/env python
# -*- coding: utf-8 -*-

import selenium001
import unittest


from selenium001 import selTest, additionalInfoOnException, jsRequired

class Test_basic(selTest):
    print "blubb"
    #@jsRequired
    @additionalInfoOnException
    def test_title_adhocracy(self):
        self.loadPage()
        title_tag = self.waitCSS('title')
        self.assertTrue("AdhocrCacy" in title_tag.text)

    @additionalInfoOnException
    def xtest_register(self):
        self.loadPage()
        
        b_register = self.waitCSS('div.register a.button.link_register_now')
        b_register.click()
        
        i_username = self.waitCSS('form[name="create_user"] input[name="user_name"]')
        i_username.send_keys("selenium_0753")
        
        i_email = self.waitCSS('form[name="create_user"] input[name="email"]')
        i_email.send_keys("selenium_user_test@0753.com")
        
        i_password = self.waitCSS('form[name="create_user"] input[name="password"]')
        i_password.send_keys("test")
        
        i_password2 = self.waitCSS('form[name="create_user"] input[name="password_confirm"]')
        i_password2.send_keys("test")
        
        b_submit = self.waitCSS('form[name="create_user"] input[type="submit"]')
        b_submit.click()

        self.waitCSS('#user_menu')

    @additionalInfoOnException
    def xtest_create_test_instance(self):
        instanceName = "Selenium Test Instance"
        instanceDescription = "Selenium Test Instance"
        instanceKey = "selTest"

        self.ensure_login(login_as_admin=True)
        self.loadPage()

        l_instances = self.waitCSS('#nav_instances > a')
        l_instances.click()

        l_instance_new = self.waitCSS('div.top_actions.title a.button.title.add')
        l_instance_new.click()

        i_label = self.waitCSS('form[name="create_instance"] input[name="label"]')
        i_label.send_keys(instanceName)

        i_key = self.waitCSS('form[name="create_instance"] input[name="key"]')
        #i_key.send_keys(instanceName.replace(" ", ""))   # since the key cannot have whitespaces we need to repleace them in instanceName
        i_key.send_keys(instanceKey)

        t_description = self.waitCSS('form[name="create_instance"] textarea[name="description"]')
        t_description.send_keys(instanceDescription)
    
        b_submit = self.waitCSS('form[name="create_instance"] button[type="submit"]')
        b_submit.click()

        self.waitXpath("//h2[contains(text(), '"+instanceName+"')]")

    @additionalInfoOnException
    def xtest_test_instance_exists(self):
        instance_name = "Selenium Test Instance"
        
        self.ensure_login(login_as_admin=True)
        self.loadPage("/instance?instances_page=1&instances_size=999&instances_sort=order.title")
        self.waitXpath("//h3/a[contains(text(), '"+instance_name+"')]")

    @additionalInfoOnException
    def xtest_create_proposal(self):
        proposalName = "Selenium Test Proposal1"
        proposalDescription = "Selenium Test Proposal"
        proposalTags = "Test Tag"
        instanceName = "Selenium Test Instance"
 
        self.ensure_login(login_as_admin=True)
        self.loadPage("/i/seltest/proposal/new")

        i_label = self.waitCSS('form[name="create_proposal"] input[name="label"]')
        i_label.send_keys(proposalName)
        
        for option in self.waitCSS('option'):
            if option.text == instanceName:
                option.click()

        i_tags = self.waitCSS('form[name="create_proposal"] input[name="tags"]')
        i_tags.send_keys(proposalTags)
        
        t_description = self.waitCSS('form[name="create_proposal"] textarea[name="text"]')
        t_description.send_keys(proposalDescription)
        
        b_submit = self.waitCSS('form[name="create_proposal"] button[type="submit"]')
        b_submit.click()

        self.waitCSS('#discussions')

if __name__ == '__main__':
    unittest.main()