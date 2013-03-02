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


if __name__ == '__main__':
    unittest.main()