import socket
import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from members.tests.factories import DepartmentFactory

"""
This test goes to the root signup page and creates a child and parent.
It uses the address Autocomplete widget to fill the address.

Once the form is filled it uses the generated password and checks that it can be
used to log in.
"""


class DepartmentListTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())

    def setUp(self):
        self.department_1 = DepartmentFactory.create()
        self.department_1.address.region = "Hovedstaden"
        self.department_2 = DepartmentFactory.create()
        self.department_2.address.region = "Syddanmark"
        self.browser = webdriver.Remote(
            "http://selenium:4444/wd/hub", DesiredCapabilities.CHROME
        )

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/department_list_final.png")
        self.browser.quit()

    def test_department_list(self):
        # Loads the departments list
        self.browser.get(f"{self.live_server_url}/departments")
        self.assertEqual("Coding Pirates Medlemssystem", self.browser.title)
        self.browser.save_screenshot("test-screens/department_list_1.png")

        # check that there's the "Hovedstaden" region tab
        self.browser.find_element_by_xpath(
            "//ul[@class='tabs']/li[text()[contains(.,'Hovedstaden')]]"
        ).click()
        self.browser.save_screenshot("test-screens/department_list_first_region.png")

        # check that the department we made in the "Hovedstaden" region is present
        department_name = self.browser.find_elements_by_xpath(
            "//section[@id='department-container']/div/ul/li[text()[contains(.,'Coding Pirates:')]]"
        )[0].text.split(" ")[-1]
        self.assertEqual(department_name, self.department_1.name)

        # check that there's the "Syddanmark" region tab
        self.browser.find_element_by_xpath(
            "//ul[@class='tabs']/li[text()[contains(.,'Syddanmark')]]"
        ).click()
        self.browser.save_screenshot("test-screens/department_list_second_region.png")

        # check that the department we made in the "Syddanmark" region is present
        department_name = self.browser.find_elements_by_xpath(
            "//section[@id='department-container']/div/ul/li[text()[contains(.,'Coding Pirates:')]]"
        )[0].text.split(" ")[-1]
        self.assertEqual(department_name, self.department_2.name)
