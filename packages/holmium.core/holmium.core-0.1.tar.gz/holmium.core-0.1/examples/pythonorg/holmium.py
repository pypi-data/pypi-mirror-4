# -*- coding: utf-8 -*-
from holmium.core import HolmiumTestCase, PageObject, PageElement, PageElementMap, PageElements, Locators


class PythonOrgPage(PageObject):
    side_bar_links = PageElementMap( Locators.CSS_SELECTOR
                                        , "ul.level-one li"
                                        , key = lambda element : element.find_element_by_tag_name("a").text
                                        , value = lambda element: element.find_element_by_tag_name("a") )

    header_text = PageElement(Locators.CSS_SELECTOR, "h1.title")


class PythonOrgTest(HolmiumTestCase):

    def setUp(self):
        self.page = PythonOrgPage(self.driver, "http://www.python.org")

    def test_links(self):
        self.page.go_home()
        assert len(self.page.side_bar_links) > 0
        link_list = [u"ABOUT", u"NEWS", u"DOCUMENTATION", u"DOWNLOAD", u"下载", u"COMMUNITY", u"FOUNDATION", u"CORE DEVELOPMENT"]
        assert self.page.side_bar_links.keys() == link_list

    def test_about_python_heading(self):
        self.page.go_home()
        self.page.side_bar_links[u"ABOUT"].click()
        assert self.page.header_text.text == u"About Python"

