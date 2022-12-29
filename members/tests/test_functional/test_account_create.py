import socket
import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

"""
This test goes to the root signup page and creates a child and parent.
It uses the address Autocomplete widget to fill the address.

Once the form is filled it uses the generated password and checks that it can be
used to log in.
"""


class AccountCreateTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    serialized_rollback = True

    def setUp(self):
        self.email = "parent@example.com"
        self.password = "ois8Ieli7bah"
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
        self.browser.maximize_window()
        self.browser.get(f"{self.live_server_url}/account/create")
        self.assertEqual("Coding Pirates Medlemssystem", self.browser.title)
        self.browser.save_screenshot("test-screens/sign_up_screen_1.png")

        # Gender
        field = Select(
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.NAME, "child_gender"))
            )
        )
        field.select_by_value("MA")

        # Enter child details
        field = self.browser.find_element(By.NAME, "child_name")
        field.send_keys("Torben Test")

        field = self.browser.find_element(By.NAME, "child_birthday")
        field.send_keys("05-03-2010")

        # Enter parent details
        field = Select(self.browser.find_element(By.NAME, "parent_gender"))
        field.select_by_value("MA")

        field = self.browser.find_element(By.NAME, "parent_name")
        field.send_keys("Anders Afprøvning")

        field = self.browser.find_element(By.NAME, "parent_birthday")
        field.send_keys("05-03-1980")

        field = self.browser.find_element(By.NAME, "parent_email")
        field.send_keys(self.email)

        field = self.browser.find_element(By.NAME, "parent_phone")
        field.send_keys("12345678")

        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.browser.save_screenshot("test-screens/sign_up_screen_1a.png")

        # Set password
        field = self.browser.find_element(By.NAME, "password1")
        field.click()
        field.send_keys(self.password)

        # Set "Gentag password"
        field = self.browser.find_element(By.NAME, "password2")
        field.click()
        field.send_keys(f"{self.password}l")

        # Use addresse Autocomplete
        field = self.browser.find_element(By.NAME, "search_address")
        field.click()
        field.send_keys("Kochsgade 31D, 5000")
        try:
            address = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ui-menu-item"))
            )
            address.click()
        except Exception:
            self.fail("Autocomplete not working")

        self.assertEqual(
            "Kochsgade 31D, 5000 Odense C",
            field.get_attribute("value"),
        )
        self.browser.save_screenshot("test-screens/sign_up_screen_2.png")

        # Submit form
        field.send_keys(Keys.TAB)
        field.send_keys(Keys.ENTER)
        self.browser.save_screenshot("test-screens/sign_up_screen_3.png")
        # Check that it dosnt redirect since passwords arent matching
        self.assertEqual(self.browser.current_url.split("/")[-2], "create")

        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.browser.save_screenshot("test-screens/sign_up_screen_3a.png")

        # Set password
        field = self.browser.find_element(By.NAME, "password1")
        field.click()
        field.send_keys(self.password)

        # Set "Gentag password"
        field = self.browser.find_element(By.NAME, "password2")
        field.click()
        field.send_keys(self.password)

        field.send_keys(Keys.TAB)
        field.send_keys(Keys.TAB)
        field.send_keys(Keys.ENTER)
        self.browser.save_screenshot("test-screens/sign_up_screen_4.png")
        # Check that redirect
        self.assertEqual(self.browser.current_url.split("/")[-2], "user_created")

        # Go to login page,
        self.browser.find_elements(
            By.XPATH, "//*[text()[contains(.,'Gå til log ind')]]"
        )[0].click()

        # enter email and password
        field = self.browser.find_element(By.NAME, "username")
        field.send_keys(self.email)

        field = self.browser.find_element(By.NAME, "password")
        field.send_keys(self.password)

        self.browser.find_element(By.XPATH, "//input[@type='submit']").click()

        # Check that we were redirectet to front page
        self.assertEqual(f"{self.live_server_url}/", self.browser.current_url)
