# -*- coding: utf-8 -*-
from holmium.core import HolmiumTestCase, PageObject, PageElement, Locators, PageElementMap


class SeleniumHQPage(PageObject):
    nav_links = PageElementMap( Locators.CSS_SELECTOR
                                        , "div#header ul>li"
                                        , key = lambda element : element.find_element_by_tag_name("a").text
                                        , value = lambda element: element.find_element_by_tag_name("a") )

    header_text = PageElement(Locators.CSS_SELECTOR, "#mainContent>h2")


class SeleniumHQTest(HolmiumTestCase):
    def setUp(self):
        self.page = SeleniumHQPage(self.driver, "http://seleniumhq.org")

    def test_header_links(self):
        self.assertTrue( len(self.page.nav_links) > 0 )
        self.assertEquals( sorted(["Projects", "Download", "Documentation", "Support", "About"])
                        ,  sorted(self.page.nav_links.keys() ) )

    def test_about_selenium_heading(self):
        self.page.nav_links["About"].click()
        self.assertEquals(self.page.header_text.text, "About Selenium")

