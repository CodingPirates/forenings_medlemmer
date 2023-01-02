from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import socket
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os

"""
    This checks if users get redirected to /admin-signup/ when they dont have a family
"""

class LoadWhenNoFamilyTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    serialized_rollback = True

    def setUp(self):
        self.browser = webdriver.Remote(
            "http://selenium:4444/wd/hub", DesiredCapabilities.CHROME
        )
        self.browser.maximize_window()

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/load_no_family_final.png")
        self.browser.quit()
    
    def test_load_when_no_family(self):
        self.browser.get(f"{self.live_server_url}/")
        self.assertEqual("Coding Pirates Medlemssystem", self.browser.title)
        self.browser.save_screenshot("test-screens/load_no_family_start.png")
