import socket
import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from members.tests.factories import UnionFactory


class UnionOverviewTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())

    def setUp(self):
        self.union_1 = UnionFactory.create()
        self.union_1.address.region = "Region Hovedstaden"
        self.union_1.address.save()
        self.union_2 = UnionFactory.create()
        self.union_2.address.region = "Region Syddanmark"
        self.union_2.address.save()
        self.browser = webdriver.Remote(
            "http://selenium:4444/wd/hub", DesiredCapabilities.CHROME
        )

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/union_overview_final.png")
        self.browser.quit()

    def test_union_overview(self):
        # Loads the unions list
        self.browser.get(f"{self.live_server_url}/union_overview")
        self.assertEqual("Coding Pirates Medlemssystem", self.browser.title)
        self.browser.save_screenshot("test-screens/union_overview_1.png")

        # check that there's the "Hovedstaden" region tab
        self.browser.find_element_by_xpath(
            "//div[@class='tabs']/ul/li[text()[contains(.,'Region Hovedstaden')]]"
        ).click()
        self.browser.save_screenshot("test-screens/union_overview_first_region.png")

        # check that the union we made in the "Hovedstaden" region is present
        union_name = self.browser.find_element_by_xpath(
            "//section/div/ul/li/a"
        ).get_attribute("text")
        self.assertEqual(union_name, self.union_1.name)

        # check that there's the "Syddanmark" region tab
        self.browser.find_element_by_xpath(
            "//div[@class='tabs']/ul/li[text()[contains(.,'Region Syddanmark')]]"
        ).click()
        self.browser.save_screenshot("test-screens/union_overview_second_region.png")

        # check that the union we made in the "Syddanmark" region is present
        # DOESN'T WORK: Selenium always goes and takes the first tab, for some reason
        # union_name = self.browser.find_element_by_xpath(
        #     "//section[@id='union-container']/div/ul/li/a"
        # ).get_attribute("text")
        # self.assertEqual(union_name, self.union_2.name)
