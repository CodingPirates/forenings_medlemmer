import os
import socket
import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

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
        self.password = "securepassword123-securepassword123"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.browser = webdriver.Remote(
            command_executor="http://selenium:4444/wd/hub",
            options=chrome_options,
        )

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/sign_up_screen_final.png")
        self.browser.quit()

    def create_account_ui_flow(self, next_url=None):
        """
        Test the account creation flow in UI.

        Args:
            next (str): Optional url that will be redirected to after account creation.
        """
        # Loads the front page
        self.browser.maximize_window()

        if next_url:
            self.browser.get(f"{self.live_server_url}/account/create?next={next_url}")
        else:
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
        field.send_keys(self.password)

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

        # click on consent checkbox
        field = self.browser.find_element(By.NAME, "consent")
        self.browser.execute_script("arguments[0].scrollIntoView(true);", field)
        time.sleep(0.5)  # give browser a bit of time to scroll

        field.click()

        # Submit form
        field.send_keys(Keys.TAB)
        field.send_keys(Keys.ENTER)
        self.browser.save_screenshot("test-screens/sign_up_screen_3.png")

        # Assert redirection
        if next_url:
            # Check that the browser is redirected to the next_url
            self.assertTrue(
                self.browser.current_url.endswith(next_url),
                f"Expected to be redirected to '{next_url}', but got '{self.browser.current_url}'",
            )
        else:
            # Check that the browser is redirected to the default "user_created" page
            self.assertTrue(
                self.browser.current_url.endswith("user_created/"),
                f"Expected to be redirected to 'user_created/', but got '{self.browser.current_url}'",
            )

    def login_and_assert_frontpage_redirect_ui_flow(self):
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

    def test_account_create_without_redirect(self):
        self.create_account_ui_flow()

        # Check that we were redirected to default 'user_created' page, since no redirect url was given
        self.assertTrue(
            self.browser.current_url.endswith("user_created/"),
            f"After creating account without redirect url, expected '{self.browser.current_url}' to end with default 'user_created/'",
        )

        self.login_and_assert_frontpage_redirect_ui_flow()

    def test_account_create_with_redirection(self):
        next_url = "/redirect/url/"
        self.create_account_ui_flow(next_url=next_url)

        # Check that we were redirected to expected page
        self.assertTrue(
            self.browser.current_url.endswith(next_url),
            f"'{self.browser.current_url}' doesn't end with '{next_url}'",
        )
