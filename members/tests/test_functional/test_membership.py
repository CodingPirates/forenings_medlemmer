import socket
import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class MembershipTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    serialized_rollback = True

    def setUp(self):
        self.browser = webdriver.Remote(
            "http://selenium:4444/wd/hub", DesiredCapabilities.CHROME
        )

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/membership_final.png")
        self.browser.quit()

    def test_membership(self):
        self.browser.get(f"{self.live_server_url}/membership")
        self.assertEqual("Coding Pirates Medlemssystem", self.browser.title)
        self.browser.save_screenshot("test-screens/membership_1.png")

        # for now, just check that the "Department signup" button exists
        button_text = self.browser.find_element(By.XPATH,
            "//a[@href='/department_signup']"
        ).get_attribute("text")
        self.assertNotEqual(button_text, None)
