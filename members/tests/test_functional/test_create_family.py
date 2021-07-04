import socket
import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

"""
This test goes to the root signup page and creates a child and parent.
It uses the address Autocomplete widget to fill the address.

Once the form is filled it uses the generated password and checks that it can be
used to log in.
"""


class SignUpTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    serialized_rollback = True

    def setUp(self):
        self.email = "parent@example.com"
        self.browser = webdriver.Remote(
            "http://selenium:4444/wd/hub", DesiredCapabilities.CHROME
        )

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/sign_up_screen_final.png")
        self.browser.quit()

    def test_account_create(self):
        # Loads the front page
        self.browser.get(self.live_server_url)
        self.assertEqual("Coding Pirates Medlemssystem", self.browser.title)
        self.browser.save_screenshot("test-screens/sign_up_screen_1.png")

        # Enter child details
        field = self.browser.find_element_by_name("child_name")
        field.send_keys("Torben Test")

        field = self.browser.find_element_by_name("child_birthday")
        field.send_keys("05-03-2010")

        # Enter parent details
        field = self.browser.find_element_by_name("parent_name")
        field.send_keys("Anders Afprøvning")

        field = self.browser.find_element_by_name("parent_birthday")
        field.send_keys("05-03-1980")

        field = self.browser.find_element_by_name("parent_email")
        field.send_keys(self.email)

        field = self.browser.find_element_by_name("parent_phone")
        field.send_keys("12345678")

        # Use addresse Autocomplete
        field = self.browser.find_element_by_name("search_address")
        field.click()
        field.send_keys("Sverigesgade 20, 5000")
        try:
            address = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ui-menu-item"))
            )
            address.click()
        except Exception:
            self.fail("Autocomplete not working")

        self.assertEqual("Sverigesgade 20, 5000 Odense C", field.get_attribute("value"))
        self.browser.save_screenshot("test-screens/sign_up_screen_2.png")

        # Submit form
        self.browser.find_element_by_name("submit").click()
        self.browser.save_screenshot("test-screens/sign_up_screen_3.png")
        # Check that redirect and get password
        self.assertEqual(self.browser.current_url.split("/")[-2], "user_created")
        password = self.browser.find_elements_by_xpath(
            "//*[text()[contains(.,'Adgangskoden er')]]"
        )[0].text.split(" ")[-1]

        # Go to login page,
        self.browser.find_elements_by_xpath(
            "//*[text()[contains(.,'Gå til log ind')]]"
        )[0].click()

        # enter email and password
        field = self.browser.find_element_by_name("username")
        field.send_keys(self.email)

        field = self.browser.find_element_by_name("password")
        field.send_keys(password)

        self.browser.find_element_by_xpath("//input[@type='submit']").click()

        # Check that we were redirectet to overview page
        elements = self.browser.find_elements_by_xpath(
            "//*[text()[contains(.,'For yderligere hjælp med at bruge denne side')]]"
        )
        self.assertGreater(len(elements), 0)
