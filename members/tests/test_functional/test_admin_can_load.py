import socket
import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
from members.tests.factories import PersonFactory

"""
This test creates a super user and checks that the admin interface can be loaded
"""


class SignUpTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    serialized_rollback = True

    def setUp(self):
        self.person = PersonFactory.create()
        self.password = "Miss1337"
        self.name = "kaptajn hack"
        self.admin = User.objects.create_superuser(
            self.name, "admin@example.com", self.password
        )

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.browser = webdriver.Remote(
            command_executor="http://selenium:4444/wd/hub",
            options=chrome_options,
        )

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/admin_load_test.png")
        self.browser.quit()

    def test_admin_page(self):
        # Loads the admin login page
        self.browser.get(f"{self.live_server_url}/admin")
        self.assertIn("admin", self.browser.title)

        # Enter login details
        field = self.browser.find_element(By.NAME, "username")
        field.send_keys(self.name)

        field = self.browser.find_element(By.NAME, "password")
        field.send_keys(self.password)

        # Submit form
        self.browser.find_element(By.XPATH, "//input[@type='submit']").click()

        # Check that we are logged in with welcome message in top right
        self.assertGreater(
            len(
                self.browser.find_elements(
                    By.XPATH, "//*[text()[contains(.,'Velkommen')]]"
                )
            ),
            0,
        )

        # Check that person admin can load
        elment = self.browser.find_element(By.LINK_TEXT, "Personer")
        self.browser.get(elment.get_attribute("href"))

        try:
            WebDriverWait(self.browser, 10).until(EC.url_contains("person"))
        except Exception:
            self.fail("Could not reach person admin site")

        # GO to person change page
        element = self.browser.find_element(By.LINK_TEXT, str(self.person))
        self.browser.get(element.get_attribute("href"))
        try:
            WebDriverWait(self.browser, 10).until(EC.url_contains("change"))
        except Exception:
            self.fail("Could not reach person admin site")

        self.assertEqual(
            self.browser.find_element(By.NAME, "email").get_attribute("value"),
            self.person.email,
        )
