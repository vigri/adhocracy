#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import time

from selenium.common.exceptions import TimeoutException
from seleniumBase import selTest


class Test_basic(selTest):

    @selTest.additionalInfoOnException
    def test_title_adhocracy(self):
        self.loadPage()
        title_tag = self.waitCSS('title')
        self.assertTrue("Adhocracy" in title_tag.text)

    @selTest.additionalInfoOnException
    def test_title_instances(self):
        self.loadPage("/instance")
        title_tag = self.waitCSS('title')
        self.assertTrue("Adhocracy" in title_tag.text)

    @selTest.additionalInfoOnException
    def test_title_help(self):
        self.loadPage("/static/help.html")
        title_tag = self.waitCSS('title')
        self.assertTrue("Adhocracy" in title_tag.text)

    @selTest.additionalInfoOnException
    def test_title_imprint(self):
        self.loadPage("/static/imprint.html")
        title_tag = self.waitCSS('title')
        self.assertTrue("Adhocracy" in title_tag.text)

    @selTest.additionalInfoOnException
    def test_create_instance_path(self):
        self.ensure_login(login_as_admin=True)
        self.loadPage()

        l_instances = self.waitCSS('#nav_instances > a')
        l_instances.click()

        l_instance_new = self.waitCSS('div.top_actions.title a.button.title.add')
        l_instance_new.click()

    @selTest.additionalInfoOnException
    def test_create_instance(self):
        creationTime = int(time.time())
        instanceName = "Test " + str(creationTime) + "_" + self.envSelectedBrowser
        instanceDescription = "Selenium Test Instance"
        instanceKey = "t" + str(creationTime)

        self.ensure_login(login_as_admin=True)
        self.loadPage("/instance/new")

        label = self.waitCSS('form[name="create_instance"] input[name="label"]')
        label.send_keys(instanceName)

        key = self.waitCSS('form[name="create_instance"] input[name="key"]')
        key.send_keys(instanceKey)

        description = self.waitCSS('form[name="create_instance"] textarea[name="description"]')
        description.send_keys(instanceDescription)

        submit = self.waitCSS('form[name="create_instance"] button[type="submit"]')
        submit.click()

        self.waitXpath("//h2[contains(text(), '" + instanceName + "')]")
        #require_valid_email
        email_verification = self.waitCSS('form[name="create_instance"] input[name="require_valid_email"]')
        email_verification.click()

        submit2 = self.waitCSS('form[name="create_instance"] button[type="submit"]')
        submit2.click()

        self.waitCSS('form[name="create_instance"] div.alert.alert-success')

        selTest.testInstanceName = instanceName

    @selTest.additionalInfoOnException
    def test_create_proposal_path(self):
        instanceName = "Feedback"

        self.ensure_login()
        self.loadPage()

        instances = self.waitCSS('#nav_instances > a')
        instances.click()

        # Temp. Display bug in adhocracy!!
        self.loadPage("/instance?instances_page=1&instances_size=100&instances_sort=-activity")

        test_instance = self.waitXpath("//div[@id='instance_table']//h3/a[contains(text(), '" + instanceName + "')]")
        test_instance.click()

        proposals = self.waitCSS('#subnav-proposals > a')

        self.ensure_is_member_of_group()

        proposals = self.waitCSS('#subnav-proposals > a')
        proposals.click()

        new_proposal = self.waitCSS('#new-proposal > a')
        new_proposal.click()

        label = self.waitCSS('form[name="create_proposal"] input[name="label"]')

    @selTest.additionalInfoOnException
    def test_create_proposal(self):
        creationTime = int(time.time())
        instanceName = "Feedback"
        proposalName = "Test " + str(creationTime) + "_" + self.envSelectedBrowser
        proposalDescription = "Selenium Test Proposal"
        proposalTags = "Test Tag"

        self.ensure_login()
        self.loadPage("/i/feedback/proposal")

        # Wait for the page to be loaded
        self.waitXpath("//h2[contains(text(), '" + instanceName + "')]")

        self.ensure_is_member_of_group()

        proposals = self.waitCSS('#subnav-proposals > a')
        proposals.click()

        new_proposal = self.waitCSS('#new-proposal > a')
        new_proposal.click()

        label = self.waitCSS('form[name="create_proposal"] input[name="label"]')
        label.send_keys(proposalName)

        tags = self.waitCSS('form[name="create_proposal"] input[name="tags"]')
        tags.send_keys(proposalTags)

        description = self.waitCSS('form[name="create_proposal"] textarea[name="text"]')
        description.send_keys(proposalDescription)

        submit = self.waitCSS('form[name="create_proposal"] button[type="submit"]')
        submit.click()

        self.waitCSS('#discussions')

        currentUrl = self.driver.current_url
        currentUrl_relPath = currentUrl.index('/i/')
        selTest.defaultProposalUrl = currentUrl[currentUrl_relPath:]

    @selTest.additionalInfoOnException
    def test_register(self):
        creationTime = int(time.time())
        userName = str(creationTime) + self.envSelectedBrowser

        self.force_logout()
        self.loadPage()

        login = self.waitCSS('#nav_login > a')
        login.click()

        register = self.waitCSS('form[name="login"] a')
        register.click()

        username = self.waitCSS('form[name="create_user"] input[name="user_name"]')
        username.send_keys(userName)

        email = self.waitCSS('form[name="create_user"] input[name="email"]')
        email.send_keys(userName + "@example.com")

        password = self.waitCSS('form[name="create_user"] input[name="password"]')
        password.send_keys("test")

        password2 = self.waitCSS('form[name="create_user"] input[name="password_confirm"]')
        password2.send_keys("test")

        submit = self.waitCSS('form[name="create_user"] input[type="submit"]')
        submit.click()

        self.waitCSS('#user_menu')
        self.force_logout()

    @selTest.additionalInfoOnException
    def test_follow_proposal(self):
        self.ensure_login()
        self.loadPage("/i/feedback/proposal")

        self.waitCSS('#proposal_list_header')

        self.ensure_is_member_of_group()

        proposals = self.waitCSS('#subnav-proposals > a')
        proposals.click()

        self.waitCSS('#proposal_list_header')

        # Get the first proposal which can be found
        try:
            proposal = self.waitCSS('li.content_box h3 > a', raiseException=False)
        except TimeoutException:
            raise Exception("No proposal has been found")

        # Due to "Element does not exist in cache"-error we need to save the name and cannot use l_proposal.text later
        proposalName = proposal.text
        proposal.click()

        # Click on the follow button
        follow = self.waitCSS('a.follow_paper')
        follow.click()

        # Now lets see if 'following' is active
        self.waitCSS('a.follow_paper.active')

        watchlist = self.waitCSS('#nav_watchlist > a')
        watchlist.click()

        self.waitXpath("//h3//a[contains(text(), '" + proposalName + "')]")

    @selTest.jsRequired
    @selTest.additionalInfoOnException
    def test_create_proposal_comment(self):
        self.ensure_login()

        if hasattr(selTest, 'defaultProposalUrl'):
            self.loadPage(selTest.defaultProposalUrl)
        else:
            raise Exception('Proposal was not created successfully before.')

        self.waitCSS('#discussions')

        for x in range(0, 3):
            self.make_element_visible_by_id("new_toplevel_comment")

            description = self.waitCSS('form[name="new_comment"] textarea[name="text"]')
            description.send_keys("Test comment " + str(x + 1))

            submit = self.waitCSS('form[name="new_comment"] input[type="submit"]')
            submit.click()

            self.waitCSS('a[id="start-discussion-button"]')

    @selTest.jsRequired
    @selTest.additionalInfoOnException
    def test_create_feedback(self):
        # Since the feedback title must be unique, we are using the current timestamp and browser for naming
        creationTime = int(time.time())
        feedbackTitle = str(creationTime) + self.envSelectedBrowser
        feedbackDescription = "Selenium Test-Feedback"

        self.ensure_login()
        self.loadPage()

        feedback_button = self.waitCSS('a#feedback_button')
        feedback_button.click()

        # after the click we wait 2 seconds to see if the feedback-form is visible to the user
        time.sleep(2)
        form_position = self.execute_js("return document.getElementById('feedback').style.right")

        if (form_position != "0px"):
            raise Exception("Element not visible")

        title = self.waitCSS('form[name="create_feedback"] input[name="label"]')
        title.send_keys(feedbackTitle)

        description = self.waitCSS('form[name="create_feedback"] textarea[name="text"]')
        description.send_keys(feedbackDescription)

        submit = self.waitCSS('form[name="create_feedback"] button[type="submit"]')
        submit.click()

        self.waitCSS('#discussions')

if __name__ == '__main__':
    unittest.main()
