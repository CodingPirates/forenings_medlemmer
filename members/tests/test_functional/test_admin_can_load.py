import socket
import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
from members.models.person import Person
from members.tests.factories import PersonFactory
from members.tests.factories.department_factory import DepartmentFactory

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
        # An open department is required for the admin signup form
        self.department = DepartmentFactory.create(closed_dtm=None)

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

        # After login the consent middleware redirects admins that do not have
        # an ordinary user (Person) yet to the admin signup form, where one must
        # be created before the rest of the site (incl. admin) can be reached.
        try:
            WebDriverWait(self.browser, 10).until(EC.url_contains("admin_signup"))
        except Exception:
            self.fail("Was not redirected to the admin signup form")

        # Fill out the captain's (admin) signup form
        Select(
            self.browser.find_element(By.ID, "id_volunteer_gender")
        ).select_by_value(Person.MALE)
        self.browser.find_element(By.ID, "id_volunteer_name").send_keys(
            "Kaptajn Testperson"
        )
        self.browser.find_element(By.ID, "id_volunteer_email").send_keys(
            "captain@example.com"
        )
        self.browser.find_element(By.ID, "id_volunteer_phone").send_keys("12345678")

        # The birthday is an <input type="date">, which expects an ISO value
        birthday = self.browser.find_element(By.ID, "id_volunteer_birthday")
        self.browser.execute_script("arguments[0].value = '1980-03-05';", birthday)

        Select(
            self.browser.find_element(By.ID, "id_volunteer_department")
        ).select_by_value(str(self.department.pk))

        # Enable manual address entry so the autofilled fields become editable
        self.browser.find_element(By.ID, "manual-entry").click()
        self.browser.find_element(By.ID, "id_streetname").send_keys("Testvej")
        self.browser.find_element(By.ID, "id_housenumber").send_keys("10")
        self.browser.find_element(By.ID, "id_zipcode").send_keys("5000")
        self.browser.find_element(By.ID, "id_city").send_keys("Odense C")

        # Submit the signup form
        self.browser.find_element(By.NAME, "submit").click()

        # Creating the person redirects to the family detail page
        try:
            WebDriverWait(self.browser, 10).until(EC.url_contains("family"))
        except Exception:
            self.fail("Admin signup form was not submitted successfully")

        # Now that the admin has a person, the admin interface can be loaded
        self.browser.get(f"{self.live_server_url}/admin")

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
