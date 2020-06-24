import socket
import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from members.tests.factories import DepartmentFactory
from members.models import User

"""
This test goes to the volunteer signup page and creates volunteer.
It uses the address Autocomplete widget to fill the address.

Once the form is filled it uses the generated password and checks that it can be
used to log in.
"""


class SignUpTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())

    def setUp(self):
        self.department_1 = DepartmentFactory.create()
        self.email = "volunteer@example.com"
        self.password = User.objects.make_random_password()
        self.browser = webdriver.Remote(
            "http://selenium:4444/wd/hub", DesiredCapabilities.CHROME
        )

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/volunteer_sign_up_screen_final.png")
        self.browser.quit()

    def test_entry_page(self):
        # Loads the front page
        self.browser.get(f"{self.live_server_url}/volunteer")
        self.assertEqual("Coding Pirates Medlemssystem", self.browser.title)
        self.browser.save_screenshot("test-screens/volunteer_sign_up_screen_1.png")

        # Enter volunteer details
        field = self.browser.find_element_by_name("volunteer_name")
        field.send_keys("Torben Test")

        field = self.browser.find_element_by_name("volunteer_birthday")
        field.send_keys("05-03-2010")

        field = self.browser.find_element_by_name("volunteer_email")
        field.send_keys(self.email)

        field = self.browser.find_element_by_name("volunteer_phone")
        field.send_keys("12345678")

        field = self.browser.find_element_by_name("volunteer_phone")
        field.send_keys("12345678")

        field = Select(self.browser.find_element_by_name("volunteer_department"))
        field.select_by_index("1")

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
        self.browser.save_screenshot("test-screens/volunteer_sign_up_screen_2.png")

        field = self.browser.find_element_by_name("password1")
        field.send_keys(self.password)
        field = self.browser.find_element_by_name("password2")
        field.send_keys(self.password)
        self.browser.save_screenshot("test-screens/volunteer_sign_up_screen_3.png")

        self.browser.find_element_by_name("submit").click()
        self.browser.save_screenshot("test-screens/volunteer_sign_up_screen_4.png")
        # Check that redirect and get password
        self.assertEqual(self.browser.current_url.split("/")[-2], "user_created")

        # Go to login page,
        self.browser.find_elements_by_xpath(
            "//*[text()[contains(.,'Gå til log ind')]]"
        )[0].click()

        # enter email and password
        field = self.browser.find_element_by_name("username")
        field.send_keys(self.email)

        field = self.browser.find_element_by_name("password")
        field.send_keys(self.password)

        self.browser.find_element_by_xpath("//input[@type='submit']").click()

        # Check that we were redirectet to overview page
        elements = self.browser.find_elements_by_xpath(
            "//*[text()[contains(.,'For yderligere hjælp med at bruge denne side')]]"
        )
        self.assertGreater(len(elements), 0)
