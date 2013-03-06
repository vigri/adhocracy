#!/usr/bin/env python
# -*- coding: utf-8 -*-

import selenium001
import unittest


from selenium001 import selTest, additionalInfoOnException, jsRequired

class Test_basic(selTest):

    @additionalInfoOnException
    def test_title_adhocracy(self):
        self.loadPage()
        title_tag = self.waitCSS('title')
        self.assertTrue("Adhocracy" in title_tag.text)

    @additionalInfoOnException
    def test_create_instance_path(self):
        self.ensure_login(login_as_admin=True)
        self.loadPage()

        l_instances = self.waitCSS('#nav_instances > a')
        l_instances.click()

        l_instance_new = self.waitCSS('div.top_actions.title a.button.title.add')
        l_instance_new.click()
        
    @additionalInfoOnException
    def test_create_instance(self):
        instanceName = "Selenium Test Instance"
        instanceDescription = "Selenium Test Instance"
        instanceKey = "selTest"

        self.ensure_login(login_as_admin=True)
        self.loadPage("/instance/new")

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
    def test_create_proposal(self):
        proposalName = "Selenium Test Proposal"
        proposalDescription = "Selenium Test Proposal"
        proposalTags = "Test Tag"

        self.ensure_login(login_as_admin=True)
        self.loadPage("/i/seltest/proposal/new")

        i_label = self.waitCSS('form[name="create_proposal"] input[name="label"]')
        i_label.send_keys(proposalName)
        
        i_tags = self.waitCSS('form[name="create_proposal"] input[name="tags"]')
        i_tags.send_keys(proposalTags)
        
        t_description = self.waitCSS('form[name="create_proposal"] textarea[name="text"]')
        t_description.send_keys(proposalDescription)
        
        b_submit = self.waitCSS('form[name="create_proposal"] button[type="submit"]')
        b_submit.click()

        self.waitCSS('#discussions')

    @additionalInfoOnException
    def test_register(self):
        self.force_logout()
        
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
if __name__ == '__main__':
    unittest.main()