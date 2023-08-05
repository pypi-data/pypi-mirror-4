import selenium.webdriver
import unittest



class SeleniumHQTest(unittest.TestCase):
    def setUp(self):
        self.driver = selenium.webdriver.Firefox()
        self.url = "http://seleniumhq.org"
    def test_header_links(self):
        self.driver.get(self.url)
        elements = self.driver.find_elements_by_css_selector("div#header ul>li")
        self.assertTrue(len(elements) > 0)
        expected_link_list = ["Projects", "Download", "Documentation", "Support", "About"]
        actual_link_list = [el.text for el in elements]
        self.assertEquals( sorted(expected_link_list), sorted(actual_link_list))

    def test_about_selenium_heading(self):
        self.driver.get(self.url)
        about_link = self.driver.find_element_by_css_selector("div#header ul>li#menu_about>a")
        about_link.click()
        heading = self.driver.find_element_by_css_selector("#mainContent>h2")
        self.assertEquals(heading.text, "About Selenium")

    def tearDown(self):
        if self.driver:
            self.driver.quit()
