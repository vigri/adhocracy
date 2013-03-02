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
        title_tag = self.waitCSS('title')
        self.assertTrue("Adhocracy" in title_tag.text)

    @additionalInfoOnException
    def test_register(self):
        self.loadPage()
        
        b_register = self.waitCSS('div.register a.button.link_register_now')
        b_register.click()
        
        i_username = self.waitCSS('form[name="create_user"] input[name="user_name"]')
        i_username.send_keys("selenium_user_test1111121")
        
        i_email = self.waitCSS('form[name="create_user"] input[name="email"]')
        i_email.send_keys("selenium_user_test@example11121.com")
        
        i_password = self.waitCSS('form[name="create_user"] input[name="password"]')
        i_password.send_keys("test")
        
        i_password2 = self.waitCSS('form[name="create_user"] input[name="password_confirm"]')
        i_password2.send_keys("test")
        
        b_submit = self.waitCSS('form[name="create_user"] input[type="submit"]')
        b_submit.click()

        self.waitCSS('#user_menu')

    def test_create_instance(self):
        newInstanceName = "New test instance"
        newInstanceDescription = "Selenium Test Instance"

        self.ensure_login(login_as_admin=True)
        self.loadPage()

        l_instances = self.waitCSS('#nav_instances > a')
        l_instances.click()

        l_instance_new = self.waitCSS('div.top_actions.title a.button.title.add')
        l_instance_new.click()

        i_label = self.waitCSS('form[name="create_instance"] input[name="label"]')
        i_label.send_keys(newInstanceName)

        i_key = self.waitCSS('form[name="create_instance"] input[name="key"]')
        i_key.send_keys(newInstanceName.replace(" ", ""))   # since the key cannot have whitespaces we need to repleace them in newInstanceName

        t_description = self.waitCSS('form[name="create_instance"] textarea[name="description"]')
        t_description.send_keys(newInstanceDescription)
    
        b_submit = self.waitCSS('form[name="create_instance"] button[type="submit"]')
        b_submit.click()

        # todo wait x seconds until check is performed
        if not self.is_text_present(newInstanceDescription):
            raise Exception("Creation of instance failed!")

        self.waitCSS('#user_menu')
if __name__ == '__main__':
    unittest.main()