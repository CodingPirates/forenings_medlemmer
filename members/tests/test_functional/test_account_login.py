import os
import socket

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from members.tests.factories import (
    MemberFactory,
)

"""
This test goes to the account login page
"""


class AccountLoginTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    serialized_rollback = True

    def setUp(self):
        self.member = MemberFactory.create()

        self.browser = webdriver.Remote(
            "http://selenium:4444/wd/hub", DesiredCapabilities.CHROME
        )

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/activities_list_final.png")
        self.browser.quit()

    def test_account_login(self):
        self.browser.get(f"{self.live_server_url}/account/login")
        self.assertIn(
            "Log ind",
            [
                e.text
                for e in self.browser.find_elements_by_xpath(
                    "//body/descendant-or-self::*"
                )
            ],
        )
        self.browser.find_element_by_link_text("Log ind")
        self.assertIn(
            "Opret bruger",
            [
                e.text
                for e in self.browser.find_elements_by_xpath(
                    "//body/descendant-or-self::*"
                )
            ],
        )
        self.browser.find_element_by_link_text("Tilmeld barn")
        self.browser.find_element_by_link_text("Bliv frivillig")
