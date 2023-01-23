import os
import socket

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from members.tests.factories import (
    MemberFactory,
)
from members.tests.test_functional.functional_helpers import log_in


"""
This tests the entry page
"""


class EntryPageTest(StaticLiveServerTestCase):
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

    def test_entry_page_as_member(self):
        # Login
        log_in(self, self.member.person)

        self.browser.find_element(By.LINK_TEXT, "Familie")
        self.browser.find_element(By.LINK_TEXT, "Log ud")

    def test_entry_page(self):
        self.browser.get(f"{self.live_server_url}")

        self.browser.find_element(By.LINK_TEXT, "Log ind")
        self.browser.find_element(By.LINK_TEXT, "Tilmeld barn")
        self.browser.find_element(By.LINK_TEXT, "Bliv frivillig")
        self.browser.find_element(By.LINK_TEXT, "Afdelinger")
        self.browser.find_element(By.LINK_TEXT, "Aktiviteter")
        self.browser.find_element(By.LINK_TEXT, "Medlemskaber")
        self.browser.find_element(By.LINK_TEXT, "Støttemedlemskaber")
        links = list(
            map(
                lambda e: e.get_attribute("href"),
                self.browser.find_elements(By.LINK_TEXT, "Aktiviteter"),
            )
        )
        self.assertEqual(links[0], links[1])
        links = list(
            map(
                lambda e: e.get_attribute("href"),
                self.browser.find_elements(By.LINK_TEXT, "Afdelinger"),
            )
        )
        self.assertEqual(links[0], links[1])
        links = list(
            map(
                lambda e: e.get_attribute("href"),
                self.browser.find_elements(By.LINK_TEXT, "Medlemskaber"),
            )
        )
        self.assertEqual(links[0], links[1])
        links = list(
            map(
                lambda e: e.get_attribute("href"),
                self.browser.find_elements(By.LINK_TEXT, "Støttemedlemskaber"),
            )
        )
        self.assertEqual(links[0], links[1])
