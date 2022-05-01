import os
import socket

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
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

        self.browser.find_element_by_link_text("Familie")
        self.browser.find_element_by_link_text("Log ud")

    def test_entry_page(self):
        self.browser.get(f"{self.live_server_url}")

        self.browser.find_element_by_link_text("Log ind")
        self.browser.find_element_by_link_text("Tilmeld barn")
        self.browser.find_element_by_link_text("Bliv frivillig")

        self.browser.find_element_by_link_text("Afdelinger")
        self.browser.find_element_by_link_text("Arrangementer")
        self.browser.find_element_by_link_text("Medlemskaber")
        self.browser.find_element_by_link_text("Støttemedlemskaber")
        links = list(
            map(
                lambda e: e.get_attribute("href"),
                self.browser.find_elements_by_link_text("Arrangementer"),
            )
        )
        self.assertEqual(links[0], links[1])
        links = list(
            map(
                lambda e: e.get_attribute("href"),
                self.browser.find_elements_by_link_text("Afdelinger"),
            )
        )
        self.assertEqual(links[0], links[1])
        links = list(
            map(
                lambda e: e.get_attribute("href"),
                self.browser.find_elements_by_link_text("Medlemskaber"),
            )
        )
        self.assertEqual(links[0], links[1])
        links = list(
            map(
                lambda e: e.get_attribute("href"),
                self.browser.find_elements_by_link_text("Støttemedlemskaber"),
            )
        )
        self.assertEqual(links[0], links[1])
