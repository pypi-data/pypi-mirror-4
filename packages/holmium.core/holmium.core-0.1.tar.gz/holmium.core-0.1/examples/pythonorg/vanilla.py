# -*- coding: utf-8 -*-
import selenium.webdriver
import unittest



class PythonOrgTest(unittest.TestCase):
    def setUp(self):
        self.driver = selenium.webdriver.Firefox()

    def test_links(self):
        self.driver.get("http://www.python.org")
        elements = self.driver.find_elements_by_css_selector("ul.level-one li>a")
        assert len(elements) > 0
        link_list = [u"ABOUT", u"NEWS", u"DOCUMENTATION", u"DOWNLOAD", u"下载", u"COMMUNITY", u"FOUNDATION", u"CORE DEVELOPMENT"]
        for element in zip(elements, link_list):
            assert element[0].text == element[1], element[0].text

    def test_about_python_heading(self):
        self.driver.get("http://www.python.org")
        elements = self.driver.find_elements_by_css_selector("ul.level-one li>a")
        about_link = [ k for k in elements if k.text == u"ABOUT"][0]
        about_link.click()
        h1_title = self.driver.find_element_by_css_selector("h1.title")
        assert h1_title.text == u"About Python"

    def tearDown(self):
        if self.driver:
            self.driver.quit()
