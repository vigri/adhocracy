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
    def test_register(self):
        self.loadPage()
        
        b_register = self.searchAndWait_css('div.register a.button.link_register_now')
        b_register.click()
        
        i_username = self.searchAndWait_css('form[name="create_user"] input[name="user_name"]')
        i_username.send_keys("selenium_user_test111112")
        
        i_email = self.searchAndWait_css('form[name="create_user"] input[name="email"]')
        i_email.send_keys("selenium_user_test@example1112.com")
        
        i_password = self.searchAndWait_css('form[name="create_user"] input[name="password"]')
        i_password.send_keys("test")
        
        i_password2 = self.searchAndWait_css('form[name="create_user"] input[name="password_confirm"]')
        i_password2.send_keys("test")
        
        b_submit = self.searchAndWait_css('form[name="create_user"] input[type="submit"]')
        b_submit.click()

        self.searchAndWait_css('#user_menu')
if __name__ == '__main__':
    unittest.main()