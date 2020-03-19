import socket
import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from members.tests.factories import PersonFactory


class LogInLogOutTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())

    def setUp(self):
        self.email = "parent@example.com"
        self.browser = webdriver.Remote(
            "http://selenium:4444/wd/hub", DesiredCapabilities.CHROME
        )
        self.person = PersonFactory.create()
        self.password = "rioguyp34098gy"
        self.person.user.set_password(self.password)
        self.person.user.email = self.person.email
        self.person.user.save()
        self.person.save()

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/log_in_log_out_final.png")
        self.browser.quit()

    def test_entry_page(self):
        # Loads the login page
        self.browser.get(f"{self.live_server_url}/account/login/")

        # Enter username
        field = self.browser.find_element_by_name("username")
        field.send_keys(self.person.email)

        # Enter username
        field = self.browser.find_element_by_name("password")
        field.send_keys(self.password)

        # Click log ind button
        self.browser.find_element_by_xpath("//input[@type='submit']").click()

        # Click log out button
        self.browser.find_elements_by_xpath("//*[text()[contains(.,'Log ud')]]")[
            0
        ].click()

        # Click log out button
        log_ins = self.browser.find_elements_by_xpath(
            "//*[text()[contains(.,'Log ind')]]"
        )
        self.assertGreater(len(log_ins), 0)
        log_out_msg = self.browser.find_elements_by_xpath(
            "//*[text()[contains(.,'Du er nu logget ud')]]"
        )
        self.assertGreater(len(log_out_msg), 0)
