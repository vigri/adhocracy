#!/usr/bin/env python
# -*- coding: utf-8 -*-

import selenium001
import unittest
import time

from selenium001 import selTest, additionalInfoOnException, jsRequired

class Test_basic(selTest):

    @additionalInfoOnException
    def test_title_adhocracy(self):
        self.loadPage()
        title_tag = self.waitCSS('title')
        self.assertTrue("Adhocracy" in title_tag.text)

    @additionalInfoOnException
    def test_title_instances(self):
        self.loadPage("/instance")
        title_tag = self.waitCSS('title')
        self.assertTrue("Adhocracy" in title_tag.text)

    @additionalInfoOnException
    def test_title_help(self):
        self.loadPage("/static/help.html")
        title_tag = self.waitCSS('title')
        self.assertTrue("Adhocracy" in title_tag.text)

    @additionalInfoOnException
    def test_title_imprint(self):
        self.loadPage("/static/imprint.html")
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
        creationTime = int(time.time())
        instanceName = "Test "+str(creationTime)+"_"+self.envSelectedBrowser
        instanceDescription = "Selenium Test Instance"
        instanceKey = "t"+str(creationTime)

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
        #require_valid_email
        c_email_verification = self.waitCSS('form[name="create_instance"] input[name="require_valid_email"]')
        c_email_verification.click()

        b_submit2 = self.waitCSS('form[name="create_instance"] button[type="submit"]')
        b_submit2.click()

        self.waitCSS('form[name="create_instance"] div.alert.alert-success')

        selTest.testInstanceName = instanceName

    @additionalInfoOnException
    def test_create_proposal_path(self):
        instanceName = "Test Instance"

        self.ensure_login()
        self.loadPage()

        l_instances = self.waitCSS('#nav_instances > a')
        l_instances.click()

        # Temp. Display bug in adhocracy!!
        self.loadPage("/instance?instances_page=1&instances_size=100&instances_sort=-activity")

        l_test_instance = self.waitXpath("//div[@id='instance_table']//h3/a[contains(text(), '"+instanceName+"')]")
        l_test_instance.click()

        l_proposals = self.waitCSS('#subnav-proposals > a')
        
        
        #self.waitXpath("//h2[contains(text(), '"+instanceName+"')]")
        try:
            b_join_group = self.waitCSS('.message .register > a',wait=2)
            b_join_group.click()
            # after the click we wait 2 seconds to see if the feedback-form is visible to the user
        except:
            print "no need to join!!!"
            
            
        l_proposals = self.waitCSS('#subnav-proposals > a')
        l_proposals.click()

        l_new_proposal = self.waitCSS('#new-proposal > a')
        l_new_proposal.click()

        i_label = self.waitCSS('form[name="create_proposal"] input[name="label"]')

    @additionalInfoOnException
    def test_create_proposal(self):
        creationTime = int(time.time())
        proposalName = "Test "+str(creationTime)+"_"+self.envSelectedBrowser
        proposalDescription = "Selenium Test Proposal"
        proposalTags = "Test Tag"

        self.ensure_login(login_as_admin=True)
        self.loadPage("/i/test/proposal/new")

        

        i_label = self.waitCSS('form[name="create_proposal"] input[name="label"]')
        i_label.send_keys(proposalName)
        
        i_tags = self.waitCSS('form[name="create_proposal"] input[name="tags"]')
        i_tags.send_keys(proposalTags)
        
        t_description = self.waitCSS('form[name="create_proposal"] textarea[name="text"]')
        t_description.send_keys(proposalDescription)
        
        b_submit = self.waitCSS('form[name="create_proposal"] button[type="submit"]')
        b_submit.click()

        self.waitCSS('#discussions')

        currentUrl = self.driver.current_url
        currentUrl_relPath = currentUrl.index('/i/')
        selTest.defaultProposalUrl = currentUrl[currentUrl_relPath:]
        

    @additionalInfoOnException
    def test_register(self):
        creationTime = int(time.time())
        userName = str(creationTime)+self.envSelectedBrowser
        
        self.force_logout()
        self.loadPage()
        
        l_login = self.waitCSS('#nav_login > a')
        l_login.click()
 
        b_register = self.waitCSS('form[name="login"] a')
        b_register.click()
        
        i_username = self.waitCSS('form[name="create_user"] input[name="user_name"]')
        i_username.send_keys(userName)
        
        i_email = self.waitCSS('form[name="create_user"] input[name="email"]')
        i_email.send_keys(userName+"@example.com")
        
        i_password = self.waitCSS('form[name="create_user"] input[name="password"]')
        i_password.send_keys("test")
        
        i_password2 = self.waitCSS('form[name="create_user"] input[name="password_confirm"]')
        i_password2.send_keys("test")
        
        b_submit = self.waitCSS('form[name="create_user"] input[type="submit"]')
        b_submit.click()

        self.waitCSS('#user_menu')
        
        selTest.pFfmpeg.kill()

    @jsRequired
    @additionalInfoOnException
    def test_create_proposal_comment(self):
        self.ensure_login()
        self.loadPage(self.defaultProposalUrl)

        self.waitCSS('#discussions')

        for x in range(0, 3):
            self.make_element_visible_by_id("new_toplevel_comment")

            t_description = self.waitCSS('form[name="new_comment"] textarea[name="text"]')
            t_description.send_keys("Test comment "+str(x+1))

            b_submit = self.waitCSS('form[name="new_comment"] input[type="submit"]')
            b_submit.click()

            self.waitCSS('a[id="start-discussion-button"]')

    @jsRequired
    @additionalInfoOnException
    def test_create_feedback(self):
        self.ensure_login()
        self.loadPage()

        feedback_button = self.waitCSS('a#feedback_button')
        feedback_button.click()

        # after the click we wait 2 seconds to see if the feedback-form is visible to the user
        time.sleep(2)
        form_position = self.driver.execute_script("return document.getElementById('feedback').style.right")

        if (form_position != "0px"):
            raise Exception("Element not visible")

        feedbackTitle = "Selenium Feedback"
        feedbackDescription = "Selenium Test-Feedback"

        i_title = self.waitCSS('form[name="create_feedback"] input[name="label"]')
        i_title.send_keys(feedbackTitle)

        t_description = self.waitCSS('form[name="create_feedback"] textarea[name="text"]')
        t_description.send_keys(feedbackDescription)
        
        b_submit = self.waitCSS('form[name="create_feedback"] button[type="submit"]')
        b_submit.click()

        self.waitCSS('#discussions')

if __name__ == '__main__':
    unittest.main()