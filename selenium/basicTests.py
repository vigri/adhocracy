#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium001 import additionalInfoOnException


@additionalInfoOnException
def test_test(self):
    self.loadPage()
    self.ensure_login(login_as_admin=True)
    #self.searchAndWait_by_tag_name('title')
    #title_tag = self.driver.find_element_by_tag_name('title')
    #self.assertTrue("Adhocracy" in title_tag.text)


@additionalInfoOnException
def xtest_title_adhocracy(self):
    self.loadPage()
    self.searchAndWait_by_tag_name('title')
    title_tag = self.driver.find_element_by_tag_name('title')
    self.assertTrue("Adhocracy" in title_tag.text)


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