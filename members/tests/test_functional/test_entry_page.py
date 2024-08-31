import os
import socket

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By

from members.tests.factories import (
    PersonFactory,
)
from members.tests.test_functional.functional_helpers import log_in


"""
This tests the entry page
"""


class EntryPageTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    serialized_rollback = True

    def setUp(self):
        self.person = PersonFactory.create()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.browser = webdriver.Remote(
            command_executor="http://selenium:4444/wd/hub",
            options=chrome_options,
        )

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/entry_page_final.png")
        self.browser.quit()

    def test_entry_page_as_person(self):
        # Login
        log_in(self, self.person)

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
